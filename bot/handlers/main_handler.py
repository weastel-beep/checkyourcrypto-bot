"""
Главный обработчик сообщений бота
"""
import logging
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

from common.database import async_session_maker
from common.services import TextService
from .base import BaseHandler, TriggerDetector, MessageFormatter, KeyboardBuilder
from .scenarios import ScenarioHandler
from .checks import CheckHandler
from .flow_buttons import FlowButtonHandler

logger = logging.getLogger(__name__)


class MainHandler(BaseHandler):
    """Главный обработчик всех сообщений"""

    def __init__(self):
        super().__init__()
        self.scenario_handler = ScenarioHandler()
        self.check_handler = CheckHandler()
        self.flow_button_handler = FlowButtonHandler()

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
            if trigger["type"] == "button" and "🔍 Показать пример" in trigger["value"]:
                return await self.handle_show_example(update, context)

            # Обрабатываем кнопку "Заказать AI анализ"
            if trigger["type"] == "button" and "🤖 Заказать AI анализ" in trigger["value"]:
                return await self.handle_order_ai_analysis(update, context)

            # Обрабатываем callback_query для новых кнопок
            if update.callback_query:
                return await self.handle_callback_query(update, context)

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

            # Получаем приветственное сообщение
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

                logger.info("✅ Команда /start обработана")
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
                
                # Создаем inline кнопки
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                buttons = [
                    [InlineKeyboardButton("🛡️ Заказать AI-анализ", callback_data="order_paid_check")],
                    [InlineKeyboardButton("💰 Пополнить баланс", callback_data="top_up_balance")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_result")],
                    [InlineKeyboardButton("👤 Личный кабинет", callback_data="personal_cabinet")]
                ]
                
                keyboard = InlineKeyboardMarkup(buttons)
                
                # Отправляем пример
                from telegram.constants import ParseMode
                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                
                logger.info("✅ Пример показан")
                return True

        except Exception as e:
            self.log_error(e, "показ примера", update.effective_user.id)
            return await self.handle_fallback(update, context)

    async def handle_order_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Заказать AI анализ'"""
        try:
            logger.info("🤖 Обработка кнопки 'Заказать AI анализ'")

            async with async_session_maker() as session:
                user_id = update.effective_user.id
                
                # Получаем пользователя
                from common.services import UserService
                user = await UserService.get_user_by_tg_id(session, user_id)
                
                if not user:
                    await update.message.reply_text("❌ Пользователь не найден")
                    return False
                
                # Проверяем баланс
                balance = user.balance or 0.0
                from common.services import SettingService
                paid_check_price = await SettingService.get_paid_check_price(session)
                
                if balance >= paid_check_price:
                    # У пользователя достаточно средств
                    await update.message.reply_text(
                        f"🤖 Заказ AI анализа оформлен!\n\n"
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

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать callback_query для новых кнопок"""
        try:
            callback_data = update.callback_query.data
            logger.info(f"🔍 Обрабатываем callback_query: {callback_data}")

            # Обрабатываем различные callback_data
            if callback_data == "show_example":
                return await self.flow_button_handler.handle_example_button(update, context)
            elif callback_data == "top_up_balance":
                return await self.flow_button_handler.handle_payment_button(update, context)
            elif callback_data == "back_to_result":
                return await self.flow_button_handler.handle_back_button(update, context)
            elif callback_data == "order_paid_check":
                return await self.flow_button_handler.handle_order_paid_check(update, context)
            elif callback_data == "insufficient_balance":
                return await self.flow_button_handler.handle_insufficient_balance(update, context)
            elif callback_data == "binance_pay":
                return await self.flow_button_handler.handle_binance_pay(update, context)
            elif callback_data == "crypto_wallet":
                return await self.flow_button_handler.handle_crypto_wallet(update, context)
            elif callback_data == "main_menu":
                return await self.flow_button_handler.handle_main_menu(update, context)
            elif callback_data == "personal_cabinet":
                return await self.flow_button_handler.handle_personal_cabinet(update, context)
            else:
                logger.warning(f"⚠️ Неизвестный callback_data: {callback_data}")
                await update.callback_query.answer("❌ Неизвестная команда")
                return True

        except Exception as e:
            self.log_error(e, "обработка callback_query", update.effective_user.id)
            return False

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
