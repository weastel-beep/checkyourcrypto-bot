"""
Обработчики команд и сообщений для Telegram-бота
"""
import logging
import re
import time
import traceback
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton

from common.database import async_session_maker
from common.services import (
    UserService, CheckService, TextService, SettingService, ChainService
)
from common.metasleuth import wallet_screening, address_label
from common.models import CheckType
from common.config import settings
from common.chain_detector import detect_chain, is_valid_crypto_address
from common.monitoring import monitoring
from common.gpt_service import gpt_service

logger = logging.getLogger(__name__)
router = Router()

# Убираем проблемный декоратор


class CheckStates(StatesGroup):
    """Состояния для процесса проверки адреса"""
    waiting_for_address = State()
    waiting_for_chain = State()


@router.message()
async def catch_all_messages(message: Message):
    """Обработчик-ловушка для всех сообщений"""
    logger.info(f"🎯 ЛОВУШКА: Получено сообщение от пользователя {message.from_user.id}")
    logger.info(f"🎯 ЛОВУШКА: Текст: '{message.text}'")
    logger.info(f"🎯 ЛОВУШКА: Тип сообщения: {type(message.text)}")
    if message.text:
        logger.info(f"🎯 ЛОВУШКА: Длина текста: {len(message.text)}")
        logger.info(f"🎯 ЛОВУШКА: Начинается с '/': {message.text.startswith('/')}")
        logger.info(f"🎯 ЛОВУШКА: В списке исключений: {message.text in ['🔍 Проверка', '💰 Пополнить', '👤 Личный кабинет', '📁 FAQ']}")
    return False  # Продолжаем обработку другими обработчиками

@router.message(CommandStart())
def _get_safe_username(user) -> Optional[str]:
    """Безопасно получить username пользователя"""
    return getattr(user, 'username', None) if user else None

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    username = _get_safe_username(message.from_user)
    logger.info(f"Получена команда /start от пользователя {message.from_user.id} ({username or 'без username'})")
    
    async with async_session_maker() as session:
        # Определяем язык пользователя
        language = "ru" if message.from_user.language_code == "ru" else "en"
        logger.info(f"Определен язык пользователя: {language}")
        
        # Получаем или создаем пользователя
        user = await UserService.get_or_create_user(
            session, message.from_user.id, language, _get_safe_username(message.from_user)
        )
        logger.info(f"Пользователь {'создан' if user.created_at == user.updated_at else 'найден'}: {user.tg_id}")
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await message.answer(blocked_text)
            return
        
        # Получаем текст приветствия
        welcome_text = await TextService.get_text(session, "welcome", user.language)
        logger.info(f"Получен текст приветствия для языка {user.language}")
        
        # Показываем главное меню
        await show_main_menu(message, user)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Обработчик команды /menu"""
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await message.answer(blocked_text)
            return
        await show_main_menu(message, user)


async def show_main_menu(message: Message, user):
    """Показать главное меню"""
    async with async_session_maker() as session:
        # Получаем тексты
        main_menu_text = await TextService.get_text(session, "main_menu", user.language)
        
        # Создаем Reply Keyboard (постоянные кнопки внизу экрана)
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
        
        # Отправляем сообщение с постоянными кнопками
        await message.answer(main_menu_text, reply_markup=keyboard)


async def edit_main_menu(message, user):
    """Редактировать сообщение с главным меню (для CallbackQuery)"""
    async with async_session_maker() as session:
        # Получаем тексты
        main_menu_text = await TextService.get_text(session, "main_menu", user.language)
        
        # Создаем клавиатуру с правильными эмодзи и текстами как на скриншоте
        builder = InlineKeyboardBuilder()
        builder.button(text="🔍 Проверка", callback_data="check_address")
        builder.button(text="💰 Пополнить", callback_data="add_balance")
        builder.button(text="👤 Личный кабинет", callback_data="profile")
        builder.button(text="📁 FAQ", callback_data="faq")
        builder.adjust(2)  # 2 кнопки в ряд
        
        # Редактируем существующее сообщение
        await message.edit_text(main_menu_text, reply_markup=builder.as_markup())


@router.message(F.text == "🔍 Проверка")
async def check_address_menu_handler(message: Message, state: FSMContext):
    """Обработчик кнопки проверки адреса (показывает инструкции)"""
    logger.info(f"🔍 ТЕКСТОВЫЙ ПРОВЕРКА СРАБОТАЛ для пользователя {message.from_user.id}")
    print(f"🔍 ТЕКСТОВЫЙ ПРОВЕРКА СРАБОТАЛ для пользователя {message.from_user.id}")
    logger.info(f"Текст сообщения: '{message.text}'")
    logger.info(f"Длина текста: {len(message.text)}")
    
    try:
        logger.info("Начинаем обработку проверки адреса...")
        async with async_session_maker() as session:
            user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
            
            # Проверяем блокировку пользователя
            if UserService.is_user_blocked(user):
                blocked_text = await TextService.get_text(session, "user_blocked", user.language)
                await message.answer(blocked_text)
                return
            logger.info("Сессия базы данных создана")
            logger.info(f"Пользователь получен: {user.tg_id}, баланс: {user.balance}")
            
            # Получаем тексты
            enter_address_text = await TextService.get_text(session, "enter_address", user.language)
            logger.info("Тексты получены")
            
            # Проверяем возможность бесплатной проверки с новой системой ограничений
            can_free, wait_time = await UserService.can_use_free_check(session, user)
            logger.info(f"КНОПКА ПРОВЕРКА - Пользователь {user.tg_id}: can_free={can_free}, wait_time={wait_time}")
            
            # Получаем информацию о статусе пользователя
            from common.check_limits import check_limits
            status_info = check_limits.get_user_status_info(user)
            logger.info(f"Статус пользователя: {status_info}")
            
            # Сохраняем состояние проверки в FSM для консистентности
            await state.update_data({
                "can_free_check": can_free,
                "check_timestamp": datetime.now().isoformat(),
                "user_status": status_info["status"],
                "user_balance": float(user.balance)
            })
            logger.info("Состояние FSM обновлено")
            
            # Формируем красивое и информативное сообщение
            message_text = f"""🔍 **Проверка криптоадреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Ваш баланс:** {user.balance} USDT

"""
            logger.info("Начало сообщения сформировано")
            
            # Информация о бесплатной проверке
            if can_free:
                message_text += "✅ **Бесплатная проверка доступна!**\n"
                message_text += "🕐 **Лимит:** 1 проверка в минуту\n\n"
            else:
                # Показываем время ожидания
                wait_time_formatted = check_limits.format_wait_time(wait_time) if wait_time else "неизвестно"
                message_text += f"⏰ **Время ожидания:** {wait_time_formatted}\n\n"
            
            logger.info("Информация о бесплатной проверке добавлена")
            
            # Информация о возможностях
            if user.balance >= Decimal("1.00"):
                message_text += "🛡️ **Доступен глубокий AI-анализ!**\n"
                message_text += "• Детальная оценка рисков\n"
                message_text += "• AI-рекомендации\n"
                message_text += "• Стоимость: 1 USDT\n\n"
            else:
                message_text += "💡 **Пополните баланс для доступа к:**\n"
                message_text += "• Глубокому AI-анализу (1 USDT)\n"
                message_text += "• Ускоренным проверкам\n\n"
            
            logger.info("Информация о возможностях добавлена")
            
            # Инструкция для пользователя
            message_text += "📝 **Как проверить адрес:**\n"
            message_text += "1️⃣ Отправьте мне криптоадрес\n"
            message_text += "2️⃣ Я автоматически определю блокчейн\n"
            
            if user.balance > Decimal("0.00"):
                message_text += "3️⃣ Выберите тип проверки:\n"
                message_text += "   • ✅ Бесплатная (базовая информация)\n"
                message_text += "   • 🛡️ AI-анализ (детальный отчёт)\n"
            else:
                message_text += "3️⃣ Получите результат проверки\n"
            
            message_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            message_text += "💬 **Отправьте адрес для проверки:**"
            
            logger.info("Инструкция для пользователя добавлена")

            # Добавляем полезные кнопки
            builder = InlineKeyboardBuilder()
            builder.button(text="💰 Пополнить баланс", callback_data="payment:add_balance")
            builder.button(text="📁 FAQ", callback_data="faq")
            builder.button(text="👤 Личный кабинет", callback_data="profile")
            builder.adjust(2, 1)
            
            logger.info("Кнопки созданы")
            
            logger.info(f"Отправляем сообщение пользователю {message.from_user.id}")
            logger.info(f"Длина сообщения: {len(message_text)}")
            logger.info(f"Первые 100 символов: {message_text[:100]}")
            
            try:
                await message.answer(message_text, parse_mode="Markdown", reply_markup=builder.as_markup())
                logger.info(f"Сообщение успешно отправлено пользователю {message.from_user.id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения: {e}")
                # Попробуем отправить простое сообщение без Markdown
                simple_message = f"🔍 Проверка криптоадреса\n💰 Баланс: {user.balance} USDT\n✅ Бесплатная проверка доступна!"
                await message.answer(simple_message)
                logger.info("Простое сообщение отправлено")
                
    except Exception as e:
        logger.error(f"Ошибка в check_address_menu_handler: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Отправляем простое сообщение в случае ошибки
        try:
            await message.answer("🔍 Проверка криптоадреса\nОтправьте мне адрес для проверки!")
        except:
            pass

        # Добавляем полезные кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Пополнить баланс", callback_data="payment:add_balance")
        builder.button(text="📁 FAQ", callback_data="faq")
        builder.button(text="👤 Личный кабинет", callback_data="profile")
        builder.adjust(2, 1)
        
        logger.info(f"Отправляем сообщение пользователю {message.from_user.id}")
        logger.info(f"Длина сообщения: {len(message_text)}")
        logger.info(f"Первые 100 символов: {message_text[:100]}")
        
        try:
            await message.answer(message_text, parse_mode="Markdown", reply_markup=builder.as_markup())
            logger.info(f"Сообщение успешно отправлено пользователю {message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            # Попробуем отправить простое сообщение без Markdown
            simple_message = f"🔍 Проверка криптоадреса\n💰 Баланс: {user.balance} USDT\n✅ Бесплатная проверка доступна!"
            await message.answer(simple_message)


@router.message(lambda message: message.text and not message.text.startswith('/') and not message.text in ["🔍 Проверка", "💰 Пополнить", "👤 Личный кабинет", "📁 FAQ"])
async def universal_address_handler(message: Message, state: FSMContext):
    """Универсальный обработчик для проверки любых текстовых сообщений как адресов"""
    logger.info(f"🔍 УНИВЕРСАЛЬНЫЙ ОБРАБОТЧИК СРАБОТАЛ для пользователя {message.from_user.id}")
    logger.info(f"Текст сообщения: '{message.text}'")
    logger.info(f"Начинается с '/': {message.text.startswith('/')}")
    logger.info(f"В списке исключений: {message.text in ['🔍 Проверка', '💰 Пополнить', '👤 Личный кабинет', '📁 FAQ']}")
    
    address = message.text.strip()
    logger.info(f"Пользователь {message.from_user.id} отправил сообщение: {address[:10]}...")
    logger.info(f"Полный адрес: {address}")
    logger.info(f"Длина адреса: {len(address)}")
    
    # Проверяем, является ли сообщение валидным криптоадресом
    logger.info(f"Проверяем валидность адреса: {address}")
    is_valid = is_valid_crypto_address(address)
    logger.info(f"Результат проверки валидности: {is_valid}")
    
    if not is_valid:
        logger.warning(f"Невалидный адрес от пользователя {message.from_user.id}: {address}")
        async with async_session_maker() as session:
            user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
            invalid_text = await TextService.get_text(session, "invalid_address", user.language)
            await message.answer(invalid_text)
        return

    # Автоматически определяем блокчейн
    chain = detect_chain(address)
    logger.info(f"Автоматически определен блокчейн: {chain} для адреса {address[:10]}...")
    
    # Проверяем баланс пользователя
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await message.answer(blocked_text)
            return
        
        logger.info(f"Проверяем баланс пользователя {message.from_user.id}: {user.balance} USDT")
        
        if user.balance > Decimal("0.00"):
            # У пользователя есть баланс - показываем выбор типа проверки
            choice_text = f"""🔍 **Выберите тип проверки адреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** `{address}`
⛓️ **Блокчейн:** {chain.upper()}
💰 **Ваш баланс:** {user.balance} USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Доступные варианты:**

✅ **Бесплатная проверка**
• Базовая информация о рисках
• Быстрый результат
• Без списания средств

🛡️ **Глубокий AI-анализ** (1 USDT)
• Детальная оценка рисков
• AI-рекомендации
• Подробный отчёт

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Выберите вариант:**"""
            
            builder = InlineKeyboardBuilder()
            builder.button(text="✅ Бесплатная проверка", callback_data=f"check_type:free:{address}:{chain}")
            builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data=f"check_type:paid:{address}:{chain}")
            builder.button(text="🏠 Главное меню", callback_data="main_menu")
            builder.adjust(1)
            
            await message.answer(choice_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
            return
    
    # У пользователя нет баланса - выполняем обычную проверку
    logger.info(f"У пользователя {message.from_user.id} нет баланса ({user.balance} USDT), выполняем бесплатную проверку")
    try:
        await perform_address_check(message, address, chain, state)
        logger.info(f"Бесплатная проверка для пользователя {message.from_user.id} завершена успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении бесплатной проверки для пользователя {message.from_user.id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при проверке адреса. Попробуйте позже.")


# Удаляем старый обработчик состояния waiting_for_address, так как теперь используем универсальный обработчик


async def show_chain_selection(message: Message):
    """Показать выбор блокчейна"""
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        select_chain_text = await TextService.get_text(session, "select_chain", user.language)
        
        # Создаем клавиатуру с популярными блокчейнами
        builder = InlineKeyboardBuilder()
        
        popular_chains = ['btc', 'eth', 'tron', 'solana', 'bsc', 'polygon', 'arbitrum']
        for chain in popular_chains:
            emoji = ChainService.get_chain_emoji(chain)
            builder.button(text=f"{emoji} {chain.upper()}", callback_data=f"chain:{chain}")
        
        # Добавляем кнопку "Другие"
        builder.button(text="🔗 Другие...", callback_data="chain:other")
        builder.adjust(3)
        
        await message.answer(select_chain_text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("chain:"))
async def process_chain_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора блокчейна"""
    chain = callback.data.split(":")[1]
    
    if chain == "other":
        # Показываем полный список блокчейнов
        await show_all_chains(callback.message)
        await callback.answer()
        return
    
    # Получаем адрес из состояния
    data = await state.get_data()
    address = data.get("address")
    
    if not address:
        await callback.answer("Ошибка: адрес не найден")
        return
    
    # Выполняем проверку
    await perform_address_check(callback.message, address, chain, state)
    await state.clear()
    await callback.answer()


async def show_all_chains(message: Message):
    """Показать все поддерживаемые блокчейны"""
    builder = InlineKeyboardBuilder()
    
    # Группируем блокчейны по категориям
    categories = {
        "Основные": ['btc', 'eth'],
        "DeFi": ['tron', 'solana', 'bsc', 'polygon', 'arbitrum', 'optimism'],
        "L2": ['zksync', 'polygonzkevm', 'base', 'linea'],
        "Другие": ['cronos', 'gnosis', 'manta', 'bittorrent', 'fantom', 'boba', 'clv', 'wemix', 'moonbeam', 'moonriver', 'mantle', 'celo', 'avalanche', 'blast', 'aurora']
    }
    
    for category, chains in categories.items():
        for chain in chains:
            emoji = ChainService.get_chain_emoji(chain)
            builder.button(text=f"{emoji} {chain.upper()}", callback_data=f"chain:{chain}")
    
    builder.adjust(3)
    await message.edit_reply_markup(reply_markup=builder.as_markup())


async def perform_address_check(message: Message, address: str, chain: str, state: FSMContext = None):
    """Выполнить проверку адреса"""
    start_time = time.time()
    logger.info(f"🔍 PERFORM_ADDRESS_CHECK: Начинаем проверку адреса {address[:10]}... для цепочки {chain}")
    logger.info(f"🔍 PERFORM_ADDRESS_CHECK: Пользователь: {message.from_user.id}")
    logger.info(f"🔍 PERFORM_ADDRESS_CHECK: Состояние: {state is not None}")
    
    # Сохраняем адрес в состоянии для платной проверки
    if state:
        await state.update_data(address=address)
    
    # Логируем начало проверки
    monitoring.log_analytics("address_check_started", {
        "user_id": message.from_user.id,
        "chain": chain,
        "address_prefix": address[:10]
    })
    
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        logger.info(f"Пользователь: {user.tg_id}, баланс: {user.balance}")
        
        # Проверяем возможность бесплатной проверки
        logger.info(f"🔍 PERFORM_ADDRESS_CHECK: Проверяем лимиты для пользователя {user.tg_id}")
        can_free, wait_time = await UserService.can_use_free_check(session, user)
        logger.info(f"🔍 PERFORM_ADDRESS_CHECK: Может выполнить бесплатную проверку: {can_free}, время ожидания: {wait_time}")
        
        if not can_free:
            # Показываем сообщение о времени ожидания
            from common.check_limits import check_limits
            wait_time_formatted = check_limits.format_wait_time(wait_time) if wait_time else "неизвестно"
            
            limit_text = f"""⏰ **Время ожидания: {wait_time_formatted}**

💰 **Ваш баланс:** {user.balance} USDT

💡 **Пополните баланс для глубокого AI-анализа (1 USDT)**"""

            builder = InlineKeyboardBuilder()
            builder.button(text="💰 Пополнить баланс", callback_data="payment:insufficient_balance")
            builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data="detailed_check:stub")
            builder.button(text="🏠 Главное меню", callback_data="main_menu")
            builder.adjust(1)
            
            await message.answer(limit_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
            return
        
        # Показываем сообщение о начале проверки
        checking_text = await TextService.get_text(session, "checking_address", user.language)
        checking_msg = await message.answer(checking_text.format(chain=chain.upper()))
        
        try:
            logger.info(f"Вызываем MetaSleuth API для адреса {address[:10]}...")
            # Выполняем проверку через MetaSleuth
            screening_result = await wallet_screening(address, chain)
            logger.info(f"Результат screening: {screening_result}")
            
            label_result = await address_label(address, chain)
            logger.info(f"Результат label: {label_result}")
            
            # Формируем результат
            result_data = {
                "screening": screening_result,
                "label": label_result,
                "address": address
            }
            
            # Сохраняем проверку в базу (всегда FREE, так как мы уже проверили лимиты)
            check_type = CheckType.FREE
            logger.info(f"Создаем запись о проверке типа {check_type}")
            check = await CheckService.create_check(
                session, user.tg_id, address, chain, check_type, result_data
            )
            logger.info(f"Проверка сохранена с ID: {check.id}")
            
            # Обновляем время последней бесплатной проверки (всегда, так как это бесплатная проверка)
            logger.info("Обновляем время последней бесплатной проверки")
            await UserService.update_last_free_check(session, user)
            
            # Формируем и отправляем результат
            logger.info("Отправляем результат пользователю")
            await send_check_result(checking_msg, result_data, chain, user.language)
            
            # Логируем успешную проверку
            response_time = time.time() - start_time
            monitoring.log_request(response_time)
            monitoring.log_analytics("address_check_completed", {
                "user_id": user.tg_id,
                "chain": chain,
                "check_type": check_type.value,
                "response_time": response_time,
                "risk_score": screening_result.get("risk", 0)
            })
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Ошибка при проверке адреса: {e}")
            monitoring.log_error(f"Address check failed: {e}", {
                "user_id": message.from_user.id,
                "chain": chain,
                "response_time": response_time
            })
            error_text = await TextService.get_text(session, "error_occurred", user.language)
            await checking_msg.edit_text(error_text)


async def send_check_result(message: Message, result_data: dict, chain: str, language: str):
    """Отправить результат проверки"""
    async with async_session_maker() as session:
        # Получаем данные из результатов
        screening = result_data["screening"]
        label = result_data["label"]
        
        # Формируем красивый ответ с разделителями
        response_text = f"""🔍 **Результат бесплатной проверки**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** `{result_data.get('address', 'неизвестный')}`
⛓️ **Блокчейн:** {chain.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Оценка риска
        risk_score = screening.get('risk', 0)
        risk_emoji = "🟢" if risk_score <= 2 else "🟡" if risk_score <= 3 else "🔴"
        risk_level = "Низкий" if risk_score <= 2 else "Средний" if risk_score <= 3 else "Высокий"
        
        response_text += f"""📊 **Оценка риска**

{risk_emoji} **Уровень:** {risk_level} ({risk_score}/5)

"""
        
        # Индикаторы риска
        risk_indicators = screening.get('risk_indicators', [])
        if risk_indicators and isinstance(risk_indicators, list):
            response_text += "⚠️ **Индикаторы риска:**\n"
            for indicator in risk_indicators:
                if isinstance(indicator, dict):
                    indicator_data = indicator.get('indicator', {})
                    if isinstance(indicator_data, dict):
                        name = indicator_data.get('name', 'Unknown')
                        # Убираем технический код из ответа пользователю
                        response_text += f"• {name}\n"
            response_text += "\n"
        
        # Информация об адресе
        main_entity = label.get('main_entity', '')
        name_tag = label.get('name_tag', '')
        
        # Фильтруем технические метки, которые не несут смысловой нагрузки
        technical_tags = [
            'transparentupgradeableproxy',
            'proxy',
            'implementation',
            'factory',
            'router',
            'deployer',
            'uniswap v',
            'universal router',
            'swap router'
        ]
        
        is_technical_tag = False
        if name_tag:
            name_tag_lower = name_tag.lower()
            is_technical_tag = any(tech_tag in name_tag_lower for tech_tag in technical_tags)
        
        if main_entity or (name_tag and not is_technical_tag):
            response_text += "🏷️ **Информация об адресе:**\n"
            if main_entity:
                response_text += f"• **Основная сущность:** {main_entity}\n"
            if name_tag and not is_technical_tag:
                response_text += f"• **Метка:** {name_tag}\n"
            
            # Веб-сайт
            main_entity_info = label.get('main_entity_info', {})
            if main_entity_info and isinstance(main_entity_info, dict):
                description = main_entity_info.get('description', {})
                if isinstance(description, dict) and description.get('website'):
                    website = description['website']
                    response_text += f"• Веб-сайт: {website}\n"
            
            # Категории
            if main_entity_info and isinstance(main_entity_info, dict):
                categories = main_entity_info.get('categories', [])
                if categories and isinstance(categories, list):
                    response_text += "• Категории:\n"
                    for cat in categories:
                        if isinstance(cat, dict):
                            cat_name = cat.get('name', 'Unknown')
                            # Убираем технический код из ответа пользователю
                            response_text += f"  - {cat_name}\n"
            
            response_text += "\n"
        
        # Атрибуты (важная информация)
        attributes = label.get('attributes', [])
        if attributes and isinstance(attributes, list):
            response_text += "🚨 **Важные атрибуты:**\n"
            
            # Справочник кодов атрибутов MetaSleuth
            # 4002 - BLOCKED (Заблокированный)
            # 4007 - DEPOSIT ADDRESS (Депозитный адрес)
            # 4008 - WITHDRAWAL ADDRESS (Адрес для вывода)
            # 4015 - SANCTIONED (Санкционированный)
            # 4016 - HOT WALLET (Горячий кошелек)
            # 4017 - COLD WALLET (Холодный кошелек)
            # 4018 - MIXER (Миксер)
            # 4019 - SCAM (Мошеннический)
            
            for attr in attributes:
                if isinstance(attr, dict):
                    attr_name = attr.get('name', 'Unknown')
                    # Убираем технический код из ответа пользователю
                    
                    # Создаем понятное описание атрибута
                    attr_description = ""
                    if attr_name == "DEPOSIT ADDRESS":
                        attr_description = f"Депозитный адрес клиента {main_entity}" if main_entity else "Депозитный адрес клиента"
                    elif attr_name == "WITHDRAWAL ADDRESS":
                        attr_description = f"Адрес для вывода {main_entity}" if main_entity else "Адрес для вывода"
                    elif attr_name == "HOT WALLET":
                        attr_description = f"Горячий кошелек {main_entity}" if main_entity else "Горячий кошелек"
                    elif attr_name == "COLD WALLET":
                        attr_description = f"Холодный кошелек {main_entity}" if main_entity else "Холодный кошелек"
                    elif attr_name == "SANCTIONED":
                        attr_description = "Санкционированный адрес"
                    elif attr_name == "BLOCKED":
                        attr_description = "Заблокированный адрес"
                    elif attr_name == "MIXER":
                        attr_description = "Адрес миксер-сервиса"
                    elif attr_name == "SCAM":
                        attr_description = "Мошеннический адрес"
                    else:
                        attr_description = attr_name
                    
                    response_text += f"• {attr_description}\n"
                    
                    # Дополнительная информация
                    comp_info = attr.get('comp_info', [])
                    if comp_info and isinstance(comp_info, list):
                        for info in comp_info:
                            response_text += f"  - {info}\n"
            response_text += "\n"
        
        # Связанные сущности
        comp_entities = label.get('comp_entities', [])
        if comp_entities and isinstance(comp_entities, list):
            response_text += "🔗 **Связанные сущности:**\n"
            for entity in comp_entities:
                # Добавляем объяснения для известных сущностей
                if entity == "Secondeye Solution":
                    response_text += f"• {entity} (компания по анализу блокчейн-рисков)\n"
                else:
                    response_text += f"• {entity}\n"
            response_text += "\n"
        
        # Рекомендации на основе риска
        response_text += "💡 **Рекомендации:**\n\n"
        if risk_score >= 4:
            response_text += "🚨 **ВНИМАНИЕ!** Высокий уровень риска.\n"
            response_text += "Рекомендуется избегать транзакций с этим адресом.\n\n"
        elif risk_score >= 3:
            response_text += "⚠️ **ВНИМАНИЕ!** Средний уровень риска.\n"
            response_text += "Будьте осторожны при взаимодействии с этим адресом.\n\n"
        else:
            # Для низкого риска даем более подробное объяснение
            if not main_entity and not label.get('attributes'):
                response_text += "✅ **Безопасно.** Адрес не вызывает серьезных опасений.\n"
                response_text += "Check Your Crypto не обнаружил связи с известными рискованными сущностями.\n\n"
            else:
                response_text += "✅ **Безопасно.** Адрес не вызывает серьезных опасений.\n\n"
        
        # Создаем клавиатуру с кнопками
        builder = InlineKeyboardBuilder()
        
        # Добавляем продающий текст и кнопки детальной проверки
        response_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        response_text += "🛡️ **Хотите узнать больше?**\n\n"
        response_text += "🔍 **Бесплатная проверка** показала базовую информацию.\n\n"
        response_text += "🤖 **Глубокий AI-анализ** (1 USDT) даст вам:\n"
        response_text += "• 📊 Детальную разбивку рисков по категориям\n"
        response_text += "• 🎯 Процентное соотношение источников\n"
        response_text += "• 💡 AI-рекомендации для максимальной безопасности\n"
        response_text += "• 🔗 Анализ связанных адресов и транзакций\n\n"
        
                # Проверяем баланс пользователя и статус для показа соответствующей кнопки
        # Получаем user_id из чата
        user_id = message.chat.id if hasattr(message, 'chat') else None
        if not user_id:
            # Если не можем получить user_id, показываем базовые кнопки
            builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data="detailed_check:stub")
            builder.button(text="💰 Пополнить баланс", callback_data="payment:insufficient_balance")
        else:
            try:
                async with async_session_maker() as session:
                    user = await UserService.get_or_create_user(session, user_id)
                    
                    # Получаем информацию о статусе пользователя
                    from common.check_limits import check_limits
                    status_info = check_limits.get_user_status_info(user)
                    
                    # Показываем статус и время до следующей бесплатной проверки
                    response_text += f"👤 **Статус:** {status_info['status_text']}\n"
                    response_text += f"💰 **Баланс:** {user.balance} USDT\n"
                    
                    # Показываем время до следующей бесплатной проверки
                    if status_info["next_check_time"]:
                        from datetime import datetime
                        time_until_next = status_info["next_check_time"] - datetime.now()
                        if time_until_next.total_seconds() > 0:
                            wait_time_formatted = check_limits.format_wait_time(int(time_until_next.total_seconds()))
                            response_text += f"⏰ **Следующая бесплатная проверка через:** {wait_time_formatted}\n"
                        else:
                            response_text += "✅ **Можете выполнить бесплатную проверку**\n"
                    else:
                        response_text += "✅ **Можете выполнить бесплатную проверку**\n"
                    
                    response_text += "\n"
                    
                    if user.balance >= Decimal("1.00"):
                        response_text += "🛡️ **Достаточно средств для глубокого AI-анализа!**\n\n"
                        builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data="detailed_check:stub")
                    else:
                        response_text += "💡 **Пополните баланс для глубокого AI-анализа**\n\n"
                        builder.button(text="💰 Пополнить баланс", callback_data="payment:insufficient_balance")
            except Exception as e:
                # В случае ошибки показываем базовые кнопки
                logger.error(f"Ошибка при получении информации о пользователе: {e}")
                builder.button(text="🛡️ Глубокий AI-анализ (1 USDT)", callback_data="detailed_check:stub")
                builder.button(text="💰 Пополнить баланс", callback_data="payment:insufficient_balance")
        
        # Вторая кнопка - пример анализа
        builder.button(text="📊 Пример Глубокого AI-анализа", callback_data="show_example:stub")
        builder.button(text="🏠 Главное меню", callback_data="main_menu")
        
        builder.adjust(1, 1)
        
        # Отправляем результат
        await message.edit_text(
            response_text, 
            reply_markup=builder.as_markup(),
            disable_web_page_preview=True
        )


@router.message(F.text == "👤 Личный кабинет")
async def profile_handler(message: Message):
    """Обработчик профиля пользователя"""
    logger.info(f"👤 ПРОФИЛЬ СРАБОТАЛ для пользователя {message.from_user.id}")
    logger.info(f"Текст: '{message.text}'")
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        
        # Получаем количество проверок за сегодня
        checks_today = await CheckService.get_checks_today(session, user.tg_id)
        
        # Получаем информацию о статусе пользователя
        from common.check_limits import check_limits
        status_info = check_limits.get_user_status_info(user)
        
        # Формируем расширенную информацию профиля
        profile_info = f"""👤 **Личный кабинет**

🆔 **ID:** {user.tg_id}
👤 **Статус:** {status_info['status_text']}
💰 **Баланс:** {user.balance} USDT
🌐 **Язык:** {user.language}
🔗 **Реферальный код:** {user.referral_code}
📊 **Проверок сегодня:** {checks_today}

📅 **Дата регистрации:** {user.created_at.strftime('%d.%m.%Y')}
⏰ **Дней с регистрации:** {status_info['days_since_creation']}"""

        # Добавляем информацию о времени до следующей бесплатной проверки
        if status_info["next_check_time"]:
            from datetime import datetime
            time_until_next = status_info["next_check_time"] - datetime.now()
            if time_until_next.total_seconds() > 0:
                wait_time_formatted = check_limits.format_wait_time(int(time_until_next.total_seconds()))
                profile_info += f"\n⏰ **Следующая бесплатная проверка через:** {wait_time_formatted}"
            else:
                profile_info += "\n✅ **Можете выполнить бесплатную проверку**"
        else:
            profile_info += "\n✅ **Можете выполнить бесплатную проверку**"
        
        # Добавляем информацию о привилегиях
        profile_info += f"""

💡 **Ваши привилегии:**
"""
        if status_info["status"] == "new_user":
            profile_info += "• 🎉 Новый пользователь (3 дня без ограничений)"
        elif status_info["status"] == "vip":
            profile_info += "• 👑 VIP пользователь (без ограничений на бесплатные проверки)"
        elif status_info["status"] == "premium":
            profile_info += "• ⭐ Премиум (проверка каждую минуту)"
        elif status_info["status"] == "standard":
            profile_info += "• 🔹 Стандарт (проверка каждые 10 минут)"
        else:
            profile_info += "• 🔸 Базовый (проверка каждый час)"
        
        await message.answer(profile_info, parse_mode="Markdown")


@router.message(F.text == "📁 FAQ")
async def faq_handler(message: Message):
    """Обработчик FAQ"""
    logger.info(f"📁 FAQ СРАБОТАЛ для пользователя {message.from_user.id}")
    logger.info(f"Текст: '{message.text}'")
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await message.answer(blocked_text)
            return
        
        faq_text = await TextService.get_text(session, "faq_content", user.language)
        
        await message.answer(faq_text)


@router.message(F.text == "💰 Пополнить")
async def add_balance_handler(message: Message):
    """Обработчик пополнения баланса"""
    logger.info(f"💰 ПОПОЛНИТЬ СРАБОТАЛ для пользователя {message.from_user.id}")
    logger.info(f"Текст: '{message.text}'")
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, message.from_user.id, username=_get_safe_username(message.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await message.answer(blocked_text)
            return
        
        # Формируем сообщение с Binance Pay
        payment_text = f"""💳 **Пополнение баланса**

💰 Ваш текущий баланс: **{user.balance}** USDT

🔄 **Доступные методы оплаты:**

🔸 **Binance Pay** (рекомендуется)
• Быстрое пополнение
• Низкие комиссии
• Поддержка криптовалют

💰 **Стоимость:**
• 1 проверка = 1 USDT

⚠️ **Важно:** Интеграция с Binance Pay находится в разработке.
Пока доступны тестовые платежи для демонстрации функционала."""

        # Создаем клавиатуру с кнопками
        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Binance Pay", callback_data="payment:binance_pay")
        builder.button(text="🧪 Тестовый платеж", callback_data="payment:test")
        builder.button(text="🏠 Главное меню", callback_data="main_menu")
        builder.adjust(1)
        
        await message.answer(payment_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("payment:"))
async def payment_handler(callback: CallbackQuery):
    """Обработчик выбора метода оплаты"""
    payment_method = callback.data.split(":")[1]
    
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, callback.from_user.id, username=_get_safe_username(callback.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await callback.message.answer(blocked_text)
            await callback.answer()
            return
        
        if payment_method == "binance_pay":
            # Binance Pay (пока заглушка)
            payment_text = f"""💳 **Binance Pay**

🔸 Выбран метод: **Binance Pay**

💰 **Стоимость:**
• 1 проверка = 1 USDT

⚠️ **Интеграция в разработке**
Пока доступны только тестовые платежи."""

            builder = InlineKeyboardBuilder()
            builder.button(text="🧪 Тестовый платеж", callback_data="payment:test")
            builder.button(text="🔙 Назад", callback_data="payment:back")
            builder.adjust(1)
            
        elif payment_method == "test":
            # Тестовый платеж - добавляем баланс
            await UserService.add_balance(session, user, Decimal("10.00"))
            await session.commit()
            
            payment_text = f"""✅ **Тестовый платеж успешен!**

💰 Ваш баланс пополнен на **10 USDT**
💳 Новый баланс: **{user.balance} USDT**

🎉 Теперь вы можете использовать глубокий AI-анализ адресов!

🔍 Проверьте любой адрес и выберите "Глубокий AI-анализ"."""

            builder = InlineKeyboardBuilder()
            builder.button(text="🔍 Проверить адрес", callback_data="check_address_after_payment")
            builder.button(text="🏠 Главное меню", callback_data="main_menu")
            builder.adjust(1)
            
        elif payment_method == "insufficient_balance":
            # Перенаправление на пополнение при недостаточном балансе
            payment_text = f"""💳 **Пополнение баланса**

💰 Ваш текущий баланс: **{user.balance}** USDT

🔄 **Доступные методы оплаты:**

🔸 **Binance Pay** (рекомендуется)
• Быстрое пополнение
• Низкие комиссии
• Поддержка криптовалют

💰 **Стоимость:**
• 1 проверка = 1 USDT

⚠️ **Важно:** Интеграция с Binance Pay находится в разработке.
Пока доступны тестовые платежи для демонстрации функционала."""

            builder = InlineKeyboardBuilder()
            builder.button(text="💳 Binance Pay", callback_data="payment:binance_pay")
            builder.button(text="🧪 Тестовый платеж", callback_data="payment:test")
            builder.button(text="🏠 Главное меню", callback_data="main_menu")
            builder.adjust(1)
            
        else:
            payment_text = "❌ Неизвестный метод оплаты"
            builder = InlineKeyboardBuilder()
            builder.button(text="🔙 Назад", callback_data="payment:back")
        
        await callback.message.edit_text(payment_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, callback.from_user.id, username=_get_safe_username(callback.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await callback.message.answer(blocked_text)
            await callback.answer()
            return
        
        await edit_main_menu(callback.message, user)
        await callback.answer()


@router.callback_query(F.data == "payment:back")
async def payment_back_handler(callback: CallbackQuery):
    """Обработчик возврата в меню платежей"""
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, callback.from_user.id)
        
        # Показываем меню платежей снова
        payment_text = f"""💳 **Пополнение баланса**

💰 Ваш текущий баланс: **{user.balance}** USDT

🔄 **Доступные методы оплаты:**

🔸 **Binance Pay** (рекомендуется)
• Быстрое пополнение
• Низкие комиссии
• Поддержка криптовалют

📊 **Тарифы:**
• 1 проверка = 1 USDT
• 5 проверок = 4 USDT (экономия 20%)
• 10 проверок = 7 USDT (экономия 30%)

⚠️ **Важно:** Интеграция с Binance Pay находится в разработке.
Пока доступны тестовые платежи для демонстрации функционала."""

        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Binance Pay", callback_data="payment:binance_pay")
        builder.button(text="🧪 Тестовый платеж", callback_data="payment:test")
        builder.button(text="🏠 Главное меню", callback_data="main_menu")
        builder.adjust(1)
        
        await callback.message.edit_text(payment_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()


@router.callback_query(F.data == "check_address")
async def check_address_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback кнопки проверки адреса"""
    logger.info(f"🔍 CALLBACK ПРОВЕРКА СРАБОТАЛ для пользователя {callback.from_user.id}")
    print(f"🔍 CALLBACK ПРОВЕРКА СРАБОТАЛ для пользователя {callback.from_user.id}")
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, callback.from_user.id)
        
        # Получаем тексты
        enter_address_text = await TextService.get_text(session, "enter_address", user.language)
        
        # Проверяем возможность бесплатной проверки с новой системой ограничений
        can_free, wait_time = await UserService.can_use_free_check(session, user)
        logger.info(f"CALLBACK ПРОВЕРКА - Пользователь {user.tg_id}: can_free={can_free}, wait_time={wait_time}")
        
        # Получаем информацию о статусе пользователя
        from common.check_limits import check_limits
        status_info = check_limits.get_user_status_info(user)
        
        # Сохраняем состояние проверки в FSM для консистентности
        await state.update_data({
            "can_free_check": can_free,
            "check_timestamp": datetime.now().isoformat(),
            "user_status": status_info["status"],
            "user_balance": float(user.balance)
        })
        
        # Формируем красивое и информативное сообщение
        message_text = f"""🔍 **Проверка криптоадреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Ваш баланс:** {user.balance} USDT

"""
        
        # Информация о бесплатной проверке
        if can_free:
            message_text += "✅ **Бесплатная проверка доступна!**\n"
            message_text += "🕐 **Лимит:** 1 проверка в минуту\n\n"
        else:
            # Показываем время ожидания
            wait_time_formatted = check_limits.format_wait_time(wait_time) if wait_time else "неизвестно"
            message_text += f"⏰ **Время ожидания:** {wait_time_formatted}\n\n"
        
        # Информация о возможностях
        if user.balance >= Decimal("1.00"):
            message_text += "🛡️ **Доступен глубокий AI-анализ!**\n"
            message_text += "• Детальная оценка рисков\n"
            message_text += "• AI-рекомендации\n"
            message_text += "• Стоимость: 1 USDT\n\n"
        else:
            message_text += "💡 **Пополните баланс для доступа к:**\n"
            message_text += "• Глубокому AI-анализу (1 USDT)\n"
            message_text += "• Ускоренным проверкам\n\n"
        
        # Инструкция для пользователя
        message_text += "📝 **Как проверить адрес:**\n"
        message_text += "1️⃣ Отправьте мне криптоадрес\n"
        message_text += "2️⃣ Я автоматически определю блокчейн\n"
        
        if user.balance > Decimal("0.00"):
            message_text += "3️⃣ Выберите тип проверки:\n"
            message_text += "   • ✅ Бесплатная (базовая информация)\n"
            message_text += "   • 🛡️ AI-анализ (детальный отчёт)\n"
        else:
            message_text += "3️⃣ Получите результат проверки\n"
        
        message_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message_text += "💬 **Отправьте адрес для проверки:**"

        # Добавляем полезные кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Пополнить баланс", callback_data="payment:add_balance")
        builder.button(text="📁 FAQ", callback_data="faq")
        builder.button(text="👤 Личный кабинет", callback_data="profile")
        builder.adjust(2, 1)
        
        await callback.message.edit_text(message_text, parse_mode="Markdown", reply_markup=builder.as_markup())
        await callback.answer()


@router.callback_query(F.data.startswith("check_type:"))
async def check_type_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора типа проверки"""
    try:
        # Парсим данные из callback
        parts = callback.data.split(":")
        check_type = parts[1]  # free или paid
        address = parts[2]
        chain = parts[3]
        
        async with async_session_maker() as session:
            user = await UserService.get_or_create_user(session, callback.from_user.id, username=_get_safe_username(callback.from_user))
            
            # Проверяем блокировку пользователя
            if UserService.is_user_blocked(user):
                blocked_text = await TextService.get_text(session, "user_blocked", user.language)
                await callback.message.answer(blocked_text)
                await callback.answer()
                return
            
            if check_type == "free":
                # Бесплатная проверка
                await perform_free_check(callback.message, address, chain, user)
            elif check_type == "paid":
                # Платная проверка
                if user.balance < Decimal("1.00"):
                    await callback.answer("❌ Недостаточно средств!")
                    return
                
                # Списываем средства
                await UserService.deduct_balance(session, user, Decimal("1.00"))
                await session.commit()
                
                await perform_paid_check(callback.message, address, chain, user)
            
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике типа проверки: {e}")
        await callback.answer("❌ Ошибка при выборе типа проверки")


@router.callback_query(F.data == "check_address_after_payment")
async def check_address_after_payment_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик проверки адреса после пополнения"""
    await state.set_state(CheckStates.waiting_for_address)
    
    async with async_session_maker() as session:
        user = await UserService.get_or_create_user(session, callback.from_user.id, username=_get_safe_username(callback.from_user))
        
        # Проверяем блокировку пользователя
        if UserService.is_user_blocked(user):
            blocked_text = await TextService.get_text(session, "user_blocked", user.language)
            await callback.message.answer(blocked_text)
            await callback.answer()
            return
        
        # Получаем текст для ввода адреса
        enter_address_text = await TextService.get_text(session, "enter_address", user.language)
        
        # Добавляем информацию о балансе
        balance_info = f"""💰 **Ваш баланс: {user.balance} USDT**

{enter_address_text}

💡 **Совет:** После ввода адреса выберите "Глубокий AI-анализ" для детальной проверки."""

        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="main_menu")
        
        await callback.message.edit_text(balance_info, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()


@router.callback_query(F.data == "show_example:stub")
async def show_example_handler(callback: CallbackQuery):
    """Обработчик показа примера глубокого анализа"""
    try:
        # Показываем сообщение о загрузке в новом сообщении
        loading_message = await callback.message.answer(
            "🤖 Загружаю пример AI-анализа...\n\n"
            "⏳ Это займет несколько секунд...",
            reply_markup=None
        )
        
        # Тестовые данные (наш пример)
        test_risk_data = {
            "minimal_risk": 80.2,
            "medium_risk": 5.9,
            "high_risk": 1.1
        }
        
        test_address_info = {
            "type": "unknown",
            "main_entity": "",
            "categories": []
        }
        
        # Получаем реальную AI-рекомендацию от GPT
        ai_recommendation = await gpt_service.analyze_risk_data(test_risk_data, test_address_info)
        
        example_text = f"""📊 Пример Глубокого AI-анализа

Подробный анализ:

✅ Минимальный риск
  •  Exchange - 80.2%
  •  Other - 0.2%
  •  Payment Management - 12.1%
  •  Wallet - 0.1%

⚠ Средний риск
  •  Exchange | High Risk - 5.9%

⛔ Высокий риск
  •  Gambling - 0.1%
  •  Sanctions - 1.1%

🤖 AI-рекомендация:
{ai_recommendation}

────────────────────────
🛡️ Защитите свои средства - закажите глубокий анализ вашего адреса.

`Глубокий AI-анализ адреса с детальным отчетом рисков, процентным соотношением и рекомендациями для максимальной безопасности.`"""
        
        builder = InlineKeyboardBuilder()
        # Одна кнопка на всю ширину
        builder.button(text="🛡️ Глубокий AI-анализ адреса", callback_data="detailed_check:stub")
        builder.adjust(1)
        
        # Отправляем новое сообщение с результатом
        await callback.message.answer(example_text, reply_markup=builder.as_markup())
        
        # Удаляем сообщение о загрузке
        await loading_message.delete()
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в примере AI-анализа: {e}")
        await callback.message.answer(
            "❌ Ошибка при загрузке примера.\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=None
        )
        await callback.answer()


@router.callback_query(F.data == "empty")
async def empty_button_handler(callback: CallbackQuery):
    """Обработчик пустой кнопки"""
    await callback.answer()


@router.callback_query(F.data.startswith("detailed_check:"))
async def detailed_check_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик глубокого анализа адреса"""
    try:
        async with async_session_maker() as session:
            user = await UserService.get_or_create_user(session, callback.from_user.id, username=_get_safe_username(callback.from_user))
            
            # Проверяем баланс пользователя
            if user.balance < Decimal("1.00"):
                insufficient_balance_text = f"""❌ **Недостаточно средств**

💰 Ваш баланс: **{user.balance} USDT**
💳 Требуется: **1 USDT** для глубокого анализа

💡 **Пополните баланс для использования глубокого AI-анализа адресов!**"""

                builder = InlineKeyboardBuilder()
                builder.button(text="💰 Пополнить баланс", callback_data="payment:insufficient_balance")
                builder.button(text="🔙 Назад", callback_data="main_menu")
                builder.adjust(1)
                
                await callback.message.edit_text(insufficient_balance_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
                await callback.answer()
                return
            
            # Получаем адрес из состояния или из callback data
            address_data = await state.get_data()
            address = address_data.get('address', '')
            
            if not address:
                await callback.answer("❌ Адрес не найден. Проверьте адрес заново.")
                return
            
            # Списываем средства за глубокий анализ
            await UserService.deduct_balance(session, user, Decimal("1.00"))
            await session.commit()
            
            # Показываем сообщение о загрузке
            loading_message = await callback.message.answer(
                f"🤖 Выполняю глубокий AI-анализ адреса...\n\n"
                f"⏳ Это займет несколько секунд...\n"
                f"💰 Списано: 1 USDT (остаток: {user.balance} USDT)",
                reply_markup=None
            )
        
        # Получаем данные от MetaSleuth
        wallet_data = await wallet_screening(address)
        label_data = await address_label(address)
        
        # Объединяем данные
        combined_data = {
            'wallet': wallet_data,
            'label': label_data
        }
        
        # Формируем данные для GPT
        risk_data = {
            'minimal_risk': wallet_data.get('minimal_risk', 0),
            'medium_risk': wallet_data.get('medium_risk', 0),
            'high_risk': wallet_data.get('high_risk', 0)
        }
        
        address_info = {
            'type': label_data.get('type', 'unknown'),
            'main_entity': label_data.get('main_entity', ''),
            'categories': label_data.get('categories', [])
        }
        
        # Получаем AI-анализ от GPT
        ai_recommendation = await gpt_service.analyze_risk_data(risk_data, address_info)
        
        # Формируем детальный отчет
        detailed_report = f"""🔍 **ГЛУБОКИЙ AI-АНАЛИЗ АДРЕСА**

📊 **Детальная оценка рисков:**
• Минимальный риск: {risk_data['minimal_risk']}%
• Средний риск: {risk_data['medium_risk']}%
• Высокий риск: {risk_data['high_risk']}%

🏷️ **Информация об адресе:**
• Тип: {address_info['type']}
• Основная сущность: {address_info['main_entity'] or 'Не определена'}
• Категории: {', '.join(address_info['categories']) if address_info['categories'] else 'Не указаны'}

🤖 **AI-рекомендация:**
{ai_recommendation}

📋 **Детальная информация:**
{await format_detailed_analysis(combined_data)}

⚠️ **Важно:** Данный анализ предоставлен в информационных целях и не является финансовой консультацией."""

        # Удаляем сообщение о загрузке
        await loading_message.delete()
        
        # Отправляем детальный отчет
        await callback.message.answer(
            detailed_report,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        await callback.answer("✅ Глубокий анализ завершен!")
        
    except Exception as e:
        logger.error(f"Ошибка в глубоком анализе: {e}")
        await callback.message.answer(
            "❌ Ошибка при выполнении глубокого анализа.\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=None
        )
        await callback.answer()


async def perform_free_check(message: Message, address: str, chain: str, user):
    """Выполнить бесплатную проверку адреса"""
    start_time = time.time()
    logger.info(f"Выполняем бесплатную проверку адреса {address[:10]}... для цепочки {chain}")
    
    # Показываем сообщение о начале проверки
    async with async_session_maker() as session:
        checking_text = await TextService.get_text(session, "checking_address", user.language)
        checking_msg = await message.answer(checking_text.format(chain=chain.upper()))
        
        try:
            # Выполняем проверку через MetaSleuth
            screening_result = await wallet_screening(address, chain)
            label_result = await address_label(address, chain)
            
            # Формируем результат
            result_data = {
                "screening": screening_result,
                "label": label_result,
                "address": address
            }
            
            # Сохраняем проверку в базу
            check = await CheckService.create_check(
                session, user.tg_id, address, chain, CheckType.FREE, result_data
            )
            
            # Обновляем время последней бесплатной проверки
            await UserService.update_last_free_check(session, user)
            
            # Отправляем результат
            await send_check_result(checking_msg, result_data, chain, user.language)
            
            # Логируем успешную проверку
            response_time = time.time() - start_time
            monitoring.log_analytics("free_check_completed", {
                "user_id": user.tg_id,
                "chain": chain,
                "response_time": response_time
            })
            
        except Exception as e:
            logger.error(f"Ошибка при бесплатной проверке: {e}")
            error_text = await TextService.get_text(session, "error_occurred", user.language)
            await checking_msg.edit_text(error_text)


async def perform_paid_check(message: Message, address: str, chain: str, user):
    """Выполнить платную глубокую проверку адреса"""
    start_time = time.time()
    logger.info(f"Выполняем платную проверку адреса {address[:10]}... для цепочки {chain}")
    
    # Показываем сообщение о загрузке
    loading_message = await message.answer(
        f"🤖 Выполняю глубокий AI-анализ адреса...\n\n"
        f"⏳ Это займет несколько секунд...\n"
        f"💰 Списано: 1 USDT (остаток: {user.balance} USDT)",
        reply_markup=None
    )
    
    try:
        # Получаем данные от MetaSleuth
        wallet_data = await wallet_screening(address, chain)
        label_data = await address_label(address, chain)
        
        # Объединяем данные
        combined_data = {
            'wallet': wallet_data,
            'label': label_data
        }
        
        # Формируем данные для GPT
        risk_data = {
            'minimal_risk': wallet_data.get('minimal_risk', 0),
            'medium_risk': wallet_data.get('medium_risk', 0),
            'high_risk': wallet_data.get('high_risk', 0)
        }
        
        address_info = {
            'type': label_data.get('type', 'unknown'),
            'main_entity': label_data.get('main_entity', ''),
            'categories': label_data.get('categories', [])
        }
        
        # Получаем AI-анализ от GPT
        ai_recommendation = await gpt_service.analyze_risk_data(risk_data, address_info)
        
        # Формируем детальный отчет
        detailed_report = f"""🔍 **ГЛУБОКИЙ AI-АНАЛИЗ АДРЕСА**

📊 **Детальная оценка рисков:**
• Минимальный риск: {risk_data['minimal_risk']}%
• Средний риск: {risk_data['medium_risk']}%
• Высокий риск: {risk_data['high_risk']}%

🏷️ **Информация об адресе:**
• Тип: {address_info['type']}
• Основная сущность: {address_info['main_entity'] or 'Не определена'}
• Категории: {', '.join(address_info['categories']) if address_info['categories'] else 'Не указаны'}

🤖 **AI-рекомендация:**
{ai_recommendation}

📋 **Детальная информация:**
{await format_detailed_analysis(combined_data)}

⚠️ **Важно:** Данный анализ предоставлен в информационных целях и не является финансовой консультацией."""

        # Сохраняем проверку в базу
        async with async_session_maker() as session:
            result_data = {
                "screening": wallet_data,
                "label": label_data,
                "address": address,
                "ai_recommendation": ai_recommendation
            }
            
            check = await CheckService.create_check(
                session, user.tg_id, address, chain, CheckType.PAID, result_data
            )
        
        # Удаляем сообщение о загрузке
        await loading_message.delete()
        
        # Отправляем детальный отчет
        await message.answer(
            detailed_report,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        # Логируем успешную проверку
        response_time = time.time() - start_time
        monitoring.log_analytics("paid_check_completed", {
            "user_id": user.tg_id,
            "chain": chain,
            "response_time": response_time
        })
        
    except Exception as e:
        logger.error(f"Ошибка в платной проверке: {e}")
        await loading_message.delete()
        await message.answer(
            "❌ Ошибка при выполнении глубокого анализа.\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=None
        )


async def format_detailed_analysis(data: Dict[str, Any]) -> str:
    """Форматирует детальную информацию для отчета"""
    wallet = data.get('wallet', {})
    label = data.get('label', {})
    
    result = []
    
    # Информация о рисках
    if wallet.get('risk_indicators'):
        result.append("🚨 **Индикаторы риска:**")
        for indicator in wallet['risk_indicators']:
            result.append(f"• {indicator}")
    
    # Категории
    if wallet.get('categories'):
        result.append("\n📂 **Категории:**")
        for category in wallet['categories']:
            result.append(f"• {category}")
    
    # Атрибуты
    if label.get('attributes'):
        result.append("\n🏷️ **Атрибуты:**")
        for attr in label['attributes']:
            attr_name = attr.get('name', '')
            attr_value = attr.get('value', '')
            if attr_name and attr_value:
                result.append(f"• {attr_name}: {attr_value}")
    
    # Связанные сущности
    if label.get('comp_entities'):
        result.append("\n🔗 **Связанные сущности:**")
        for entity in label['comp_entities']:
            entity_name = entity.get('name', '')
            if entity_name:
                result.append(f"• {entity_name}")
    
    return '\n'.join(result) if result else "Дополнительная информация не найдена."


@router.message(Command("gpt_stats"))
async def gpt_stats_handler(message: Message):
    """Показывает статистику использования GPT"""
    stats = gpt_service.get_usage_stats()
    
    stats_text = f"""🤖 Статистика GPT

📊 Запросы сегодня: {stats['requests_today']}/{stats['daily_limit']}
🔄 Осталось запросов: {stats['remaining_requests']}
💾 Размер кэша: {stats['cache_size']} записей

💰 Экономия: кэширование и лимиты активны"""
    
    await message.answer(stats_text)


def is_valid_address(address: str) -> bool:
    """Простая валидация адреса"""
    # Убираем пробелы
    address = address.strip()
    
    # Минимальная длина
    if len(address) < 10:
        return False
    
    # Проверяем на наличие недопустимых символов
    if not re.match(r'^[a-zA-Z0-9]+$', address):
        return False
    
    return True
