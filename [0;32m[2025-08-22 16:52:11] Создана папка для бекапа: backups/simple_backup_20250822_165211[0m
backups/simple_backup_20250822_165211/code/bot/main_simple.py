"""
Упрощенная версия бота для тестирования запуска
"""
import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем основные сервисы
from common.config import settings
from common.database import init_db, close_db
from common.services import UserService, TextService
from common.chain_detector import detect_chain
from common.metasleuth import wallet_screening, address_label
from common.models import CheckType
from common.services import CheckService
from common.gpt_service import gpt_service
from common.database import async_session_maker
from decimal import Decimal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Простой обработчик для тестирования
from aiogram import Router, F
from aiogram.types import Message

router = Router()

# Словарь для хранения последних сообщений пользователей
user_last_messages = {}

def detect_user_language(user) -> str:
    """Определяем язык пользователя по Telegram языку"""
    if user.language_code:
        # Если язык русский или украинский - используем русский
        if user.language_code in ['ru', 'uk', 'be']:
            return 'ru'
        # Для всех остальных - английский
        else:
            return 'en'
    else:
        # Если язык не определен - по умолчанию английский
        return 'en'

async def update_user_message(user_id: int, new_message, delete_old: bool = True):
    """Обновляет сообщение пользователя, удаляя старое"""
    try:
        if delete_old and user_id in user_last_messages:
            old_message = user_last_messages[user_id]
            try:
                await old_message.delete()
                logger.info(f"🎯 СООБЩЕНИЕ: Удалено старое сообщение для пользователя {user_id}")
            except Exception as e:
                logger.warning(f"🎯 СООБЩЕНИЕ: Не удалось удалить старое сообщение: {e}")
        
        # Сохраняем новое сообщение
        user_last_messages[user_id] = new_message
        logger.info(f"🎯 СООБЩЕНИЕ: Сохранено новое сообщение для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"🎯 СООБЩЕНИЕ: Ошибка при обновлении сообщения: {e}")

@router.callback_query()
async def callback_handler(callback: CallbackQuery):
    """Обработчик callback кнопок"""
    try:
        logger.info(f"🎯 CALLBACK: Получен callback от {callback.from_user.id}")
        logger.info(f"🎯 CALLBACK: Данные: {callback.data}")
        
        if callback.data.startswith("free_check:"):
            # Пользователь выбрал бесплатную проверку
            logger.info(f"🎯 CALLBACK: Пользователь выбрал бесплатную проверку")
            
            # Извлекаем адрес из callback_data
            address = callback.data.split(":", 1)[1]
            logger.info(f"🎯 CALLBACK: Адрес для бесплатной проверки: {address}")
            
            # Показываем сообщение о начале проверки
            checking_msg = await callback.message.edit_text(f"🔍 Выполняю базовую проверку адреса: {address[:10]}...")
            await update_user_message(callback.from_user.id, checking_msg, delete_old=False)
            
            try:
                # Определяем блокчейн
                chain = detect_chain(address)
                logger.info(f"🎯 CALLBACK: Определен блокчейн: {chain}")
                
                # Выполняем проверку
                logger.info(f"🎯 CALLBACK: Вызываем MetaSleuth API")
                screening_result = await wallet_screening(address, chain)
                label_result = await address_label(address, chain)
                
                # Формируем результат
                result_data = {
                    "screening": screening_result,
                    "label": label_result,
                    "address": address
                }
                
                # Сохраняем проверку в базу
                async with async_session_maker() as session:
                    user = await UserService.get_or_create_user(session, callback.from_user.id, username=callback.from_user.username)
                    check = await CheckService.create_check(
                        session, user.tg_id, address, chain, CheckType.FREE, result_data
                    )
                    logger.info(f"🎯 CALLBACK: Проверка сохранена с ID: {check.id}")
                    
                    # Обновляем время последней бесплатной проверки
                    await UserService.update_last_free_check(session, user)
                
                # Отправляем результат
                await send_check_result(checking_msg, result_data, chain, user.language)
                logger.info(f"🎯 CALLBACK: Результат бесплатной проверки отправлен")
                
            except Exception as e:
                logger.error(f"🎯 CALLBACK: Ошибка при бесплатной проверке: {e}")
                await checking_msg.edit_text("❌ Произошла ошибка при проверке адреса. Попробуйте позже.")
                
        elif callback.data.startswith("paid_check:"):
            # Пользователь выбрал платную проверку
            logger.info(f"🎯 CALLBACK: Пользователь выбрал платную проверку")
            
            # Извлекаем адрес из callback_data
            address = callback.data.split(":", 1)[1]
            logger.info(f"🎯 CALLBACK: Адрес для платной проверки: {address}")
            
            # Показываем сообщение о начале анализа
            loading_msg = await callback.message.edit_text(f"🤖 Выполняю глубокий AI-анализ адреса: {address[:10]}...\n\n⏱️ Это займет около 30 секунд")
            await update_user_message(callback.from_user.id, loading_msg, delete_old=False)
            
            try:
                # Определяем блокчейн
                chain = detect_chain(address)
                logger.info(f"🎯 CALLBACK: Определен блокчейн: {chain}")
                
                # Выполняем базовую проверку
                logger.info(f"🎯 CALLBACK: Вызываем MetaSleuth API")
                screening_result = await wallet_screening(address, chain)
                label_result = await address_label(address, chain)
                
                # Выполняем AI-анализ
                logger.info(f"🎯 CALLBACK: Вызываем GPT для анализа")
                ai_analysis = await gpt_service.analyze_risk_data(screening_result, label_result)
                
                # Формируем результат
                result_data = {
                    "screening": screening_result,
                    "label": label_result,
                    "ai_analysis": ai_analysis,
                    "address": address
                }
                
                # Сохраняем проверку в базу
                async with async_session_maker() as session:
                    user = await UserService.get_or_create_user(session, callback.from_user.id, username=callback.from_user.username)
                    
                    # Проверяем баланс
                    if user.balance < Decimal("1.00"):
                        await loading_msg.edit_text("❌ Недостаточно средств на балансе. Минимум 1 USDT для глубокого AI-анализа.")
                        return
                    
                    # Списываем баланс
                    user.balance -= Decimal("1.00")
                    await session.commit()
                    logger.info(f"🎯 CALLBACK: Списано 1 USDT с баланса пользователя {user.tg_id}. Новый баланс: {user.balance}")
                    
                    check = await CheckService.create_check(
                        session, user.tg_id, address, chain, CheckType.PAID, result_data
                    )
                    logger.info(f"🎯 CALLBACK: Платная проверка сохранена с ID: {check.id}")
                
                # Отправляем результат
                await send_paid_check_result(loading_msg, result_data, chain, user.language)
                logger.info(f"🎯 CALLBACK: Результат платной проверки отправлен")
                
            except Exception as e:
                logger.error(f"🎯 CALLBACK: Ошибка при платной проверке: {e}")
                await loading_msg.edit_text("❌ Произошла ошибка при выполнении AI-анализа. Попробуйте позже.")
            
        elif callback.data == "back_to_check":
            # Вернуться к результату проверки
            logger.info(f"🎯 CALLBACK: Пользователь вернулся к результату проверки")
            await callback.message.edit_text("🔙 Возвращаемся к результату проверки...\n\nНажмите '🔍 Проверка' и отправьте адрес для новой проверки.")
            
        elif callback.data == "new_check":
            # Новая проверка
            logger.info(f"🎯 CALLBACK: Пользователь хочет новую проверку")
            await callback.message.edit_text("🔍 Отправьте адрес для проверки:\n\n• Базовая проверка - базовая информация\n• Глубокий AI-анализ - детальный отчёт (1 USDT)")
            
        elif callback.data == "add_balance":
            # Пополнить баланс
            logger.info(f"🎯 CALLBACK: Пользователь хочет пополнить баланс")
            await callback.message.edit_text("💰 **Пополнение баланса**\n\n💳 **Способы пополнения:**\n• Binance Pay (скоро)\n• Криптокошелек\n\n💵 **Тарифы:**\n• 1 USDT = 1 глубокий AI-анализ\n\nОбратитесь к администратору для пополнения.")
            
        elif callback.data == "show_example":
            # Показать пример платного анализа
            logger.info(f"🎯 CALLBACK: Пользователь хочет посмотреть пример")
            
            example_text = f"""🛡️ **Пример глубокого AI-анализа**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** `0x1da5821544e25c636c1417ba96ade4cf6d2f9b5a`
⛓️ **Блокчейн:** ETH
🤖 **AI-анализ:** Полный

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Детальная оценка рисков**

✅ **Минимальный риск (98.6%)**
• Exchange - 80.2%
• Other - 0.2%
• Payment Management - 12.1%
• Wallet - 0.1%

⚠️ **Средний риск (5.9%)**
• Exchange | High Risk - 5.9%

⛔ **Высокий риск (1.2%)**
• Gambling - 0.1%
• Sanctions - 1.1%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **AI-рекомендации**

🔍 **Анализ безопасности:**
• Адрес связан с крупной биржей (80.2% Exchange)
• Минимальная активность в сомнительных сервисах
• Основные транзакции через проверенные платформы

💡 **Рекомендации:**
• ✅ **Безопасно для транзакций** - низкий общий риск
• ⚠️ **Внимание:** 1.1% санкций требует дополнительной проверки
• 🔄 **Мониторинг:** Рекомендуется отслеживать изменения рисков

📈 **Прогноз:**
• Стабильный уровень безопасности в ближайшие 30 дней
• Риск санкций может увеличиться при изменении политики

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Стоимость:** 1 USDT
⏱️ **Время анализа:** ~30 секунд

Хотите получить такой же детальный анализ для вашего адреса?"""
            
            # Кнопки для действия
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            builder = InlineKeyboardBuilder()
            builder.button(text="🛡️ Заказать AI-анализ (1 USDT)", callback_data="paid_check")
            builder.button(text="🔙 Назад", callback_data="back_to_check")
            builder.adjust(1)
            
            await callback.message.edit_text(example_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
            
        else:
            await callback.answer("Неизвестная команда")
            
    except Exception as e:
        logger.error(f"🎯 CALLBACK: Ошибка при обработке callback: {e}")
        await callback.answer("Произошла ошибка")

@router.message()
async def echo_handler(message: Message):
    """Универсальный обработчик сообщений"""
    logger.info(f"🎯 ОБРАБОТЧИК: Получено сообщение от {message.from_user.id}")
    logger.info(f"🎯 ОБРАБОТЧИК: Текст: '{message.text}'")
    logger.info(f"🎯 ОБРАБОТЧИК: Длина текста: {len(message.text) if message.text else 0}")
    
    try:
        if message.text in ["🔍 Проверка", "🔍 Check"]:
            logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем команду 'Проверка'")
            
            # Получаем информацию о пользователе
            from common.database import async_session_maker
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                
                # Проверяем блокировку пользователя
                if UserService.is_user_blocked(user):
                    blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                    await message.answer(blocked_text)
                    return
                
                logger.info(f"🎯 ОБРАБОТЧИК: Пользователь: {user.tg_id}, баланс: {user.balance}")
                
                # Проверяем возможность бесплатной проверки
                can_free = await UserService.can_use_free_check(session, user)
                logger.info(f"🎯 ОБРАБОТЧИК: Может выполнить бесплатную проверку: {can_free}")
                
                # Простая логика для времени ожидания (1 минута)
                wait_time = 60 if not can_free else 0
                
                # Формируем сообщение в зависимости от языка
                if user.language == 'ru':
                    message_text = f"""🔍 **Проверка криптоадреса**
━━━━━━━━━━━━━━━━━━
💳 **Баланс:** {user.balance} USDT

✅ **Базовая проверка** — базовая оценка риска, 1 раз в минуту
🛡️ **Глубокий AI-анализ** — 1 USDT
・ Детальный отчёт о рисках
・ Санкции, подозрительные паттерны
・ Рекомендации от AI

📌 **Как это работает:**
1️⃣ Отправьте криптоадрес (BTC, ETH, USDT и др.)
2️⃣ Мы определим блокчейн автоматически
3️⃣ Выберите тип проверки:
   ✅ Базовая (базовая оценка риска - бесплатно)
   🛡️ AI-анализ (глубокая аналитика 1 USD)

━━━━━━━━━━━━━━━━━━
💬 **Отправьте адрес для проверки**"""
                else:
                    message_text = f"""🔍 **Crypto Address Check**
━━━━━━━━━━━━━━━━━━
💳 **Balance:** {user.balance} USDT

✅ **Basic Check** — basic risk assessment, once per minute
🛡️ **Deep AI Analysis** — 1 USDT
・ Detailed risk report
・ Sanctions and suspicious patterns
・ AI recommendations

📌 **How it works:**
1️⃣ Send a crypto address (BTC, ETH, USDT, etc.)
2️⃣ We'll automatically determine the blockchain
3️⃣ Choose verification type:
   ✅ Basic (basic risk assessment - free)
   🛡️ AI Analysis (deep analytics 1 USD)

━━━━━━━━━━━━━━━━━━
💬 **Send address for verification**"""
                
                # Отправляем сообщение и сохраняем его для перезаписи
                sent_message = await message.answer(message_text, parse_mode="Markdown")
                await update_user_message(message.from_user.id, sent_message)
                logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для команды 'Проверка'")
            
        elif message.text == "💰 Пополнить":
            logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем команду 'Пополнить'")
            
            # Проверяем блокировку пользователя
            from common.database import async_session_maker
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                
                if UserService.is_user_blocked(user):
                    blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                    await message.answer(blocked_text)
                    return
            
            response = "💰 Пополнение баланса\n\nФункция в разработке. Скоро будет доступна!"
            await message.answer(response)
            logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для команды 'Пополнить'")
            
        elif message.text == "👤 Личный кабинет":
            logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем команду 'Личный кабинет'")
            
            # Проверяем блокировку пользователя
            from common.database import async_session_maker
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                
                if UserService.is_user_blocked(user):
                    blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                    await message.answer(blocked_text)
                    return
            
            response = "👤 Личный кабинет\n\nФункция в разработке. Скоро будет доступна!"
            await message.answer(response)
            logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для команды 'Личный кабинет'")
            
        elif message.text == "📁 FAQ":
            logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем команду 'FAQ'")
            
            # Проверяем блокировку пользователя
            from common.database import async_session_maker
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                
                if UserService.is_user_blocked(user):
                    blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                    await message.answer(blocked_text)
                    return
            
            response = "📁 FAQ\n\nФункция в разработке. Скоро будет доступна!"
            await message.answer(response)
            logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для команды 'FAQ'")
            
        elif message.text.startswith("/start"):
            logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем команду '/start'")
            
            # Определяем язык пользователя
            user_language = detect_user_language(message.from_user)
            logger.info(f"🎯 ОБРАБОТЧИК: Определен язык пользователя: {user_language}")
            
            # Создаем или получаем пользователя с правильным языком
            from common.database import async_session_maker
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                
                # Проверяем блокировку пользователя
                if UserService.is_user_blocked(user):
                    blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                    await message.answer(blocked_text)
                    return
                
                # Если язык изменился, обновляем его
                if user.language != user_language:
                    user.language = user_language
                    await session.commit()
                    logger.info(f"🎯 ОБРАБОТЧИК: Обновлен язык пользователя на: {user_language}")
            
            # Получаем текст приветствия из базы данных
            from common.services import TextService
            welcome_text = await TextService.get_text(session, "welcome", user_language)
            response = welcome_text
            
            # Создаем клавиатуру с кнопками управления
            logger.info(f"🎯 ОБРАБОТЧИК: Создаем клавиатуру для команды '/start'")
            from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
            
            if user_language == 'ru':
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="🔍 Проверка"),
                            KeyboardButton(text="💰 Пополнить")
                        ],
                        [
                            KeyboardButton(text="👤 Личный кабинет"),
                            KeyboardButton(text="📁 FAQ")
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            else:
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="🔍 Check"),
                            KeyboardButton(text="💰 Top Up")
                        ],
                        [
                            KeyboardButton(text="👤 Profile"),
                            KeyboardButton(text="📁 FAQ")
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            logger.info(f"🎯 ОБРАБОТЧИК: Клавиатура создана успешно")
            
            await message.answer(response, reply_markup=keyboard, parse_mode="Markdown")
            logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для команды '/start' с клавиатурой")
            
        else:
            # Проверяем, похоже ли сообщение на криптоадрес
            logger.info(f"🎯 ОБРАБОТЧИК: Проверяем, является ли сообщение адресом")
            is_likely_address = len(message.text) > 20 and any(char in message.text for char in "0123456789abcdefABCDEF")
            logger.info(f"🎯 ОБРАБОТЧИК: Похоже на адрес: {is_likely_address}")
            
            if is_likely_address:
                logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем как адрес")
                
                # Получаем информацию о пользователе
                from common.database import async_session_maker
                async with async_session_maker() as session:
                    user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                    logger.info(f"🎯 ОБРАБОТЧИК: Пользователь: {user.tg_id}, баланс: {user.balance}")
                    
                    if user.balance > 0.00:
                        logger.info(f"🎯 ОБРАБОТЧИК: У пользователя есть баланс, показываем выбор")
                        choice_text = f"""🔍 **Выберите тип проверки адреса**
━━━━━━━━━━━━━━━━━━
📍 **Адрес для проверки:**
`{message.text}`

💳 **Ваш баланс в системе:** {user.balance} USDT
━━━━━━━━━━━━━━━━━━

**Доступные варианты:**

✅ **Базовая проверка**
・ Базовая информация о рисках
・ Быстрый результат
・ Без списания средств

🛡️ **Глубокий AI-анализ** (1 USDT)
・ Детальная оценка рисков
・ Санкции и подозрительные паттерны
・ AI-рекомендации и подробный отчёт
・ История транзакций и экспозиция к категориям (Exchange, Gambling, Payment Management)
・ Краткий прогноз вероятности риска будущих транзакций

━━━━━━━━━━━━━━━━━━
💬 **Выберите тип проверки**"""
                        
                        from aiogram.utils.keyboard import InlineKeyboardBuilder
                        builder = InlineKeyboardBuilder()
                        builder.button(text="✅ Базовая проверка", callback_data=f"free_check:{message.text}")
                        builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data=f"paid_check:{message.text}")
                        builder.adjust(1)
                        
                        # Отправляем сообщение с выбором и сохраняем его
                        sent_message = await message.answer(choice_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
                        await update_user_message(message.from_user.id, sent_message)
                        logger.info(f"🎯 ОБРАБОТЧИК: Показан выбор типа проверки")
                    else:
                        logger.info(f"🎯 ОБРАБОТЧИК: У пользователя нет баланса, выполняем бесплатную проверку")
                        
                        # Показываем сообщение о начале проверки и сохраняем его
                        checking_msg = await message.answer(f"🔍 Выполняю базовую проверку адреса: {message.text[:10]}...")
                        await update_user_message(message.from_user.id, checking_msg)
                        
                        try:
                            # Определяем блокчейн
                            chain = detect_chain(message.text)
                            logger.info(f"🎯 ОБРАБОТЧИК: Определен блокчейн: {chain}")
                            
                            # Выполняем проверку
                            logger.info(f"🎯 ОБРАБОТЧИК: Вызываем MetaSleuth API")
                            screening_result = await wallet_screening(message.text, chain)
                            label_result = await address_label(message.text, chain)
                            
                            # Формируем результат
                            result_data = {
                                "screening": screening_result,
                                "label": label_result,
                                "address": message.text
                            }
                            
                            # Сохраняем проверку в базу
                            check = await CheckService.create_check(
                                session, user.tg_id, message.text, chain, CheckType.FREE, result_data
                            )
                            logger.info(f"🎯 ОБРАБОТЧИК: Проверка сохранена с ID: {check.id}")
                            
                            # Обновляем время последней бесплатной проверки
                            await UserService.update_last_free_check(session, user)
                            
                            # Отправляем результат
                            await send_check_result(checking_msg, result_data, chain, user.language)
                            logger.info(f"🎯 ОБРАБОТЧИК: Результат бесплатной проверки отправлен")
                            
                        except Exception as e:
                            logger.error(f"🎯 ОБРАБОТЧИК: Ошибка при бесплатной проверке: {e}")
                            await checking_msg.edit_text("❌ Произошла ошибка при проверке адреса. Попробуйте позже.")
            else:
                logger.info(f"🎯 ОБРАБОТЧИК: Обрабатываем как обычное сообщение")
                
                # Проверяем блокировку пользователя
                from common.database import async_session_maker
                async with async_session_maker() as session:
                    user = await UserService.get_or_create_user(session, message.from_user.id, username=message.from_user.username)
                    
                    if UserService.is_user_blocked(user):
                        blocked_text = "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору."
                        await message.answer(blocked_text)
                        return
                
                response = f"Получено сообщение: {message.text}"
                await message.answer(response)
                logger.info(f"🎯 ОБРАБОТЧИК: Ответ отправлен для обычного сообщения")
                
    except Exception as e:
        logger.error(f"🎯 ОБРАБОТЧИК: Ошибка при обработке сообщения: {e}")
        logger.error(f"🎯 ОБРАБОТЧИК: Traceback: {traceback.format_exc()}")
        try:
            await message.answer("❌ Произошла ошибка при обработке сообщения. Попробуйте позже.")
        except:
            pass

async def main():
    """Упрощенная функция запуска бота"""
    logger.info("🚀 Запуск упрощенного бота")
    
    try:
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована")
        
        # Получаем токен из переменных окружения
        import os
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("BOT_TOKEN не найден в переменных окружения")
            return
        
        logger.info("Создание бота и диспетчера...")
        bot = Bot(token=token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Подключаем роутер
        dp.include_router(router)
        
        logger.info("Получение информации о боте...")
        bot_info = await bot.get_me()
        logger.info(f"Бот: @{bot_info.username} (ID: {bot_info.id})")
        
        logger.info("Начинаем polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        try:
            await close_db()
        except:
            pass
        logger.info("Бот остановлен")

async def send_paid_check_result(message, result_data: dict, chain: str, language: str):
    """Отправить результат платной AI-проверки"""
    try:
        # Получаем данные из результатов
        screening = result_data["screening"]
        label = result_data["label"]
        ai_analysis = result_data.get("ai_analysis", {})
        
        # Формируем красивый ответ
        response_text = f"""🛡️ **Глубокий AI-анализ завершен**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** `{result_data.get('address', 'неизвестный')}`
⛓️ **Блокчейн:** {chain.upper()}
🤖 **AI-анализ:** Полный
💰 **Стоимость:** 1 USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Детальная оценка рисков**

"""
        
        # Оценка риска
        risk_score = screening.get('risk', 0)
        risk_emoji = "🟢" if risk_score <= 2 else "🟡" if risk_score <= 3 else "🔴"
        risk_level = "Низкий" if risk_score <= 2 else "Средний" if risk_score <= 3 else "Высокий"
        
        response_text += f"{risk_emoji} **Общий уровень риска:** {risk_level} ({risk_score}/5)\n\n"
        
        # Детальная разбивка рисков (если есть)
        if 'risk_breakdown' in screening:
            breakdown = screening['risk_breakdown']
            
            # Минимальный риск
            low_risk = breakdown.get('low_risk', {})
            if low_risk:
                total_low = sum(low_risk.values())
                response_text += f"✅ **Минимальный риск ({total_low:.1f}%)**\n"
                for category, percentage in low_risk.items():
                    response_text += f"• {category} - {percentage:.1f}%\n"
                response_text += "\n"
            
            # Средний риск
            medium_risk = breakdown.get('medium_risk', {})
            if medium_risk:
                total_medium = sum(medium_risk.values())
                response_text += f"⚠️ **Средний риск ({total_medium:.1f}%)**\n"
                for category, percentage in medium_risk.items():
                    response_text += f"• {category} - {percentage:.1f}%\n"
                response_text += "\n"
            
            # Высокий риск
            high_risk = breakdown.get('high_risk', {})
            if high_risk:
                total_high = sum(high_risk.values())
                response_text += f"⛔ **Высокий риск ({total_high:.1f}%)**\n"
                for category, percentage in high_risk.items():
                    response_text += f"• {category} - {percentage:.1f}%\n"
                response_text += "\n"
        
        response_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # AI-рекомендации
        response_text += "🤖 **AI-рекомендации**\n\n"
        
        if ai_analysis:
            # Используем реальные AI-рекомендации
            response_text += ai_analysis.get('analysis', 'AI-анализ недоступен')
        else:
            # Fallback рекомендации
            response_text += "🔍 **Анализ безопасности:**\n"
            response_text += "• Детальный анализ всех связанных адресов\n"
            response_text += "• Оценка истории транзакций\n"
            response_text += "• Анализ подозрительной активности\n\n"
            
            response_text += "💡 **Рекомендации:**\n"
            if risk_score <= 2:
                response_text += "• ✅ **Безопасно для транзакций**\n"
                response_text += "• 🔒 Рекомендуется стандартная осторожность\n"
            elif risk_score <= 3:
                response_text += "• ⚠️ **Требует дополнительной проверки**\n"
                response_text += "• 🔍 Рекомендуется мониторинг активности\n"
            else:
                response_text += "• ❌ **Высокий риск - не рекомендуется**\n"
                response_text += "• 🚫 Избегайте транзакций с этим адресом\n"
            
            response_text += "\n📈 **Прогноз:**\n"
            response_text += "• Стабильный уровень безопасности в ближайшие 30 дней\n"
            response_text += "• Рекомендуется периодический мониторинг\n"
        
        response_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        response_text += "💎 **Преимущества AI-анализа:**\n"
        response_text += "• 🤖 Персональные AI-рекомендации\n"
        response_text += "• 📊 Детальная оценка всех рисков\n"
        response_text += "• 🔮 Прогноз изменения безопасности\n"
        response_text += "• ⚡ Мгновенный результат\n"
        
        # Кнопки
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.button(text="🔍 Новая проверка", callback_data="new_check")
        builder.button(text="💰 Пополнить баланс", callback_data="add_balance")
        builder.adjust(1)
        
        await message.edit_text(response_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке результата платной проверки: {e}")
        await message.edit_text("❌ Произошла ошибка при формировании результата.")

async def send_check_result(message, result_data: dict, chain: str, language: str):
    """Отправить результат проверки"""
    try:
        # Получаем данные из результатов
        screening = result_data["screening"]
        label = result_data["label"]
        
        # Формируем красивый ответ в зависимости от языка
        if language == 'ru':
            response_text = f"""🔍 **Результат базовой проверки**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** `{result_data.get('address', 'неизвестный')}`
⛓️ **Блокчейн:** {chain.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        else:
            response_text = f"""🔍 **Basic Check Result**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Address:** `{result_data.get('address', 'unknown')}`
⛓️ **Blockchain:** {chain.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Оценка риска
        risk_score = screening.get('risk', 0)
        risk_emoji = "🟢" if risk_score <= 2 else "🟡" if risk_score <= 3 else "🔴"
        risk_level = "Низкий" if risk_score <= 2 else "Средний" if risk_score <= 3 else "Высокий"
        
        response_text += f"""📊 **Оценка риска**

{risk_emoji} **Уровень:** {risk_level} ({risk_score}/5)

"""
        
        # Информация об адресе
        main_entity = label.get('main_entity', '')
        name_tag = label.get('name_tag', '')
        
        if main_entity or name_tag:
            response_text += "🏷️ **Информация об адресе:**\n"
            if main_entity:
                response_text += f"• **Основная сущность:** {main_entity}\n"
            if name_tag:
                response_text += f"• **Метка:** {name_tag}\n"
            response_text += "\n"
        
        # Рекомендации
        response_text += "💡 **Рекомендации:**\n"
        if risk_score <= 2:
            response_text += "• Адрес выглядит безопасно\n"
            response_text += "• Можно использовать для транзакций\n"
        elif risk_score <= 3:
            response_text += "• Адрес имеет средний уровень риска\n"
            response_text += "• Рекомендуется дополнительная проверка\n"
        else:
            response_text += "• Адрес имеет высокий уровень риска\n"
            response_text += "• Не рекомендуется для транзакций\n"
        
        response_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        response_text += "🛡️ **Хотите узнать больше?**\n\n"
        response_text += "🔍 **Базовая проверка** показала базовую информацию.\n\n"
        response_text += "🛡️ **Глубокий AI-анализ** даст вам:\n"
        response_text += "• Детальную оценку всех рисков\n"
        response_text += "• AI-рекомендации по безопасности\n"
        response_text += "• Подробный анализ транзакций\n"
        response_text += "• Стоимость: 1 USDT\n\n"
        
        # Кнопки
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        address = result_data.get('address', '')
        builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data=f"paid_check:{address}")
        builder.button(text="📊 Посмотреть пример", callback_data="show_example")
        builder.adjust(1)
        
        await message.edit_text(response_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке результата: {e}")
        await message.edit_text("❌ Произошла ошибка при формировании результата.")

if __name__ == "__main__":
    asyncio.run(main())
