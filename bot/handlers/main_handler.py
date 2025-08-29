"""
Главный обработчик сообщений бота
"""
import logging
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

from common.database import async_session_maker
from common.services_legacy import TextService
from .base import BaseHandler, TriggerDetector, MessageFormatter, KeyboardBuilder
from .scenarios import ScenarioHandler
from .checks import CheckHandler

logger = logging.getLogger(__name__)


class MainHandler(BaseHandler):
    """Главный обработчик всех сообщений"""

    def __init__(self):
        super().__init__()
        self.scenario_handler = ScenarioHandler()
        self.check_handler = CheckHandler()

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать любое сообщение"""
        try:
            # Определяем триггер
            trigger = await TriggerDetector.detect_trigger(update)
            logger.info(f"🔍 Главный обработчик: определен триггер {trigger['type']} для текста '{update.message.text}'")

            # Обрабатываем команду /start
            if trigger["type"] == "command" and trigger["value"] == "/start":
                return await self.handle_start_command(update, context)

            # Обрабатываем проверку адреса
            if trigger["type"] == "address_input":
                logger.info("🔍 Обрабатываем адрес через CheckHandler")
                logger.info("🔍 ВЫЗЫВАЕМ CheckHandler.handle")
                result = await self.check_handler.handle(update, context)
                logger.info(f"🔍 CheckHandler.handle вернул: {result}")
                return result

            # Обрабатываем кнопку "Показать пример"
            if trigger["type"] == "button" and "📊 Показать пример" in trigger["value"]:
                return await self.handle_show_example(update, context)

            # Обрабатываем кнопку "Глубокий AI-анализ"
            if trigger["type"] == "button" and "🛡️ Глубокий AI-анализ" in trigger["value"]:
                return await self.handle_deep_analysis(update, context)

            # Обрабатываем кнопку "Пополнить баланс"
            if trigger["type"] == "button" and "💰 Пополнить баланс" in trigger["value"]:
                return await self.handle_top_up_balance(update, context)

            # Обрабатываем кнопку "Главное меню"
            if trigger["type"] == "button" and "🏠 Главное меню" in trigger["value"]:
                return await self.handle_main_menu(update, context)

            # Обрабатываем сценарии
            logger.info("🔍 Пробуем обработать через ScenarioHandler")
            if await self.scenario_handler.handle(update, context):
                logger.info("🔍 Обработано через ScenarioHandler")
                return True

            # Если ничего не подошло, показываем fallback
            return await self.handle_fallback(update, context)

        except Exception as e:
            self.log_error(e, "главный обработчик", update.effective_user.id)
            await self.handle_error(update, context)
            return False

    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать команду /start"""
        try:
            logger.info("🚀 Обработка команды /start")

            # Получаем активный сценарий из конструктора
            async with async_session_maker() as session:
                from common.services_package.scenario_service import ScenarioService
                
                # Получаем активный сценарий
                active_scenario = await ScenarioService.get_active_scenario(session)
                
                if active_scenario:
                    logger.info(f"✅ Используем активный сценарий: {active_scenario.get('name')}")
                    
                    # Ищем этап Start в сценарии
                    stages = active_scenario.get("stages", [])
                    start_stage = None
                    
                    for stage in stages:
                        if stage.get("trigger") == "command" and stage.get("trigger_value") == "/start":
                            start_stage = stage
                            break
                    
                    if start_stage:
                        logger.info(f"✅ Найден этап Start в сценарии")
                        
                        # Получаем текст для этапа
                        text_key = start_stage.get("text_key", "welcome")
                        user_id = update.effective_user.id
                        text = await TextService.get_text(session, text_key, "ru", user_id)
                        
                        # Конвертируем в HTML
                        html_text = MessageFormatter.convert_markdown_to_html_simple(text)
                        
                        # Создаем клавиатуру из кнопок этапа
                        buttons = start_stage.get("buttons", [])
                        if buttons:
                            keyboard = KeyboardBuilder.create_dynamic_keyboard("|".join(buttons))
                        else:
                            keyboard = KeyboardBuilder.create_main_menu_keyboard()
                        
                        # Отправляем приветствие
                        from telegram.constants import ParseMode
                        await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                        
                        # Сохраняем текущий сценарий в контекст
                        context.user_data["current_scenario"] = active_scenario
                        context.user_data["current_stage_id"] = start_stage.get("id")
                        
                        logger.info("✅ Команда /start обработана через сценарий")
                        return True
                    else:
                        logger.warning("⚠️ Этап Start не найден в активном сценарии")
                else:
                    logger.warning("⚠️ Активный сценарий не найден")

            # Fallback к старому способу
            async with async_session_maker() as session:
                user_id = update.effective_user.id
                text = await TextService.get_text(session, "welcome", "ru", user_id)

                # Конвертируем в HTML
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем клавиатуру главного меню
                keyboard = KeyboardBuilder.create_main_menu_keyboard()

                # Отправляем приветствие
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                logger.info("✅ Команда /start обработана через fallback")
                return True

        except Exception as e:
            self.log_error(e, "обработка команды /start", update.effective_user.id)
            return await self.handle_fallback(update, context)

    async def handle_fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать неизвестное сообщение"""
        try:
            logger.info("❓ Обработка fallback для неизвестного сообщения")

            # Показываем fallback сообщение
            text = MessageFormatter.format_fallback_message()
            keyboard = KeyboardBuilder.create_main_menu_keyboard()

            await update.message.reply_text(text, reply_markup=keyboard)

            logger.info("✅ Fallback обработан")
            return True

        except Exception as e:
            self.log_error(e, "обработка fallback", update.effective_user.id)
            return False

    async def handle_show_example(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Показать пример'"""
        try:
            logger.info("🔍 Обработка кнопки 'Показать пример'")

            async with async_session_maker() as session:
                user_id = update.effective_user.id
                
                # Получаем шаблон примера
                example_text = await TextService.get_text(session, "deep_analysis_example", "ru", user_id)
                
                # Заменяем плейсхолдеры
                example_text = example_text.replace("{address}", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
                example_text = example_text.replace("{paid_check_price}", "2.0")
                
                # Конвертируем в HTML
                html_text = MessageFormatter.convert_markdown_to_html_simple(example_text)
                
                # Создаем обычные кнопки управления
                from .base import KeyboardBuilder
                
                keyboard = KeyboardBuilder.create_dynamic_keyboard("🛡️ Заказать AI-анализ|💰 Пополнить баланс|🔙 Назад|👤 Личный кабинет")
                
                # Отправляем пример
                from telegram.constants import ParseMode
                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                
                logger.info("✅ Пример показан")
                return True

        except Exception as e:
            self.log_error(e, "показ примера", update.effective_user.id)
            return await self.handle_fallback(update, context)

    async def handle_deep_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Глубокий AI-анализ'"""
        try:
            logger.info("🛡️ Обработка кнопки 'Глубокий AI-анализ'")

            async with async_session_maker() as session:
                user_id = update.effective_user.id
                
                # Получаем пользователя
                from common.services_legacy import UserService
                user = await UserService.get_user_by_tg_id(session, user_id)
                
                if not user:
                    await update.message.reply_text("❌ Пользователь не найден")
                    return False
                
                # Проверяем баланс
                balance = user.balance or 0.0
                from common.services_legacy import SettingService
                paid_check_price = await SettingService.get_paid_check_price(session)
                
                if balance >= paid_check_price:
                    # У пользователя достаточно средств
                    await update.message.reply_text(
                        f"🛡️ Заказ глубокого AI-анализа оформлен!\n\n"
                        f"💰 Списано: {paid_check_price} USDT\n"
                        f"💳 Остаток: {balance - paid_check_price} USDT\n\n"
                        f"📝 Отправьте адрес для глубокого AI анализа:"
                    )
                    
                    # Списываем средства
                    await UserService.deduct_balance(session, user, paid_check_price)
                    
                else:
                    # Недостаточно средств
                    await update.message.reply_text(
                        f"❌ Недостаточно средств для AI анализа\n\n"
                        f"💰 Ваш баланс: {balance} USDT\n"
                        f"💳 Требуется: {paid_check_price} USDT\n\n"
                        f"Пополните баланс для продолжения."
                    )
                
                logger.info("✅ Заказ AI анализа обработан")
                return True

        except Exception as e:
            self.log_error(e, "заказ AI анализа", update.effective_user.id)
            return await self.handle_fallback(update, context)

    async def handle_top_up_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Пополнить баланс'"""
        try:
            logger.info("💰 Обработка кнопки 'Пополнить баланс'")

            async with async_session_maker() as session:
                user_id = update.effective_user.id
                
                # Получаем текст методов оплаты
                text = await TextService.get_text(session, "payment_methods", "ru", user_id)
                
                # Заменяем плейсхолдеры
                from common.services_package.placeholder_service import PlaceholderService
                text = await PlaceholderService.replace_placeholders(session, text, user_id)
                
                # Конвертируем в HTML
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем кнопки
                from .base import KeyboardBuilder
                keyboard = KeyboardBuilder.create_dynamic_keyboard("💳 Binance Pay|🪙 Криптокошелек|🔙 Назад|🏠 Главное меню")

                # Отправляем сообщение
                from telegram.constants import ParseMode
                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

            return True

        except Exception as e:
            self.log_error(e, "пополнение баланса", update.effective_user.id)
            return await self.handle_fallback(update, context)

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Главное меню'"""
        try:
            logger.info("🏠 Обработка кнопки 'Главное меню'")
            
            # Возвращаемся в главное меню
            return await self.handle_start_command(update, context)

        except Exception as e:
            self.log_error(e, "главное меню", update.effective_user.id)
            return await self.handle_fallback(update, context)



    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать ошибку"""
        try:
            logger.error("❌ Обработка ошибки в главном обработчике")

            # Показываем сообщение об ошибке
            text = MessageFormatter.format_error_message()
            keyboard = KeyboardBuilder.create_main_menu_keyboard()

            await update.message.reply_text(text, reply_markup=keyboard)

            return True

        except Exception as e:
            logger.error(f"❌ Критическая ошибка в обработке ошибки: {e}")
            return False


# Создаем глобальный экземпляр главного обработчика
main_handler = MainHandler()


async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главная функция для обработки всех сообщений"""
    try:
        # Проверяем, что это текстовое сообщение
        if not update.message or not update.message.text:
            logger.warning("⚠️ Получено не текстовое сообщение")
            return

        # Обрабатываем сообщение через главный обработчик
        success = await main_handler.handle(update, context)

        if success:
            logger.info("✅ Сообщение успешно обработано")
        else:
            logger.warning("⚠️ Сообщение не было обработано")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка в handle_all_messages: {e}")
        try:
            # Пытаемся показать ошибку пользователю
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        except Exception:
            pass


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        logger.info("🚀 Обработка команды /start")

        # Обрабатываем через главный обработчик
        success = await main_handler.handle_start_command(update, context)

        if not success:
            logger.warning("⚠️ Команда /start не была обработана")

    except Exception as e:
        logger.error(f"❌ Ошибка в cmd_start: {e}")
        try:
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        except Exception:
            pass
