"""
Обработчики кнопок для Bot Flow Designer
"""
import logging
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

from common.database import async_session_maker
from common.services import UserService, TextService, SettingService
from .base import BaseHandler, HandlerResult

logger = logging.getLogger(__name__)


class FlowButtonHandler(BaseHandler):
    """Обработчик кнопок Bot Flow Designer"""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Основной метод обработки (требуется BaseHandler)"""
        # Этот класс используется только для отдельных методов
        return False

    async def handle_example_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Показать пример'"""
        try:
            user_id = update.effective_user.id
            logger.info(f"🔍 handle_example_button вызван для пользователя {user_id}")

            async with async_session_maker() as session:
                # Получаем пользователя
                user = await UserService.get_user_by_tg_id(session, user_id)
                if not user:
                    logger.error(f"❌ Пользователь {user_id} не найден")
                    return False

                # Получаем текст примера
                text = await TextService.get_text(session, "deep_analysis_example", user.language or "ru", user_id)
                
                # Конвертируем Markdown в HTML
                from .base import MessageFormatter
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем кнопки
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                # Проверяем баланс для определения активных кнопок
                balance = user.balance or 0.0
                paid_check_price = await SettingService.get_paid_check_price(session)
                has_sufficient_balance = balance >= paid_check_price

                buttons = []
                
                # Кнопка "Заказать AI-анализ" (активна только при достаточном балансе)
                if has_sufficient_balance:
                    buttons.append([InlineKeyboardButton("🛡️ Заказать AI-анализ", callback_data="order_paid_check")])
                else:
                    buttons.append([InlineKeyboardButton("🛡️ Заказать AI-анализ", callback_data="insufficient_balance")])
                
                buttons.extend([
                    [InlineKeyboardButton("💰 Пополнить баланс", callback_data="top_up_balance")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_result")],
                    [InlineKeyboardButton("👤 Личный кабинет", callback_data="personal_cabinet")]
                ])

                keyboard = InlineKeyboardMarkup(buttons)

                from telegram.constants import ParseMode
                await update.callback_query.edit_message_text(
                    html_text, 
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )

            return True

        except Exception as e:
            self.log_error(e, "обработка кнопки 'Показать пример'", update.effective_user.id)
            await self.show_error_message(update)
            return False

    async def handle_payment_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Пополнить баланс'"""
        try:
            user_id = update.effective_user.id
            logger.info(f"🔍 handle_payment_button вызван для пользователя {user_id}")

            async with async_session_maker() as session:
                # Получаем пользователя
                user = await UserService.get_user_by_tg_id(session, user_id)
                if not user:
                    logger.error(f"❌ Пользователь {user_id} не найден")
                    return False

                # Получаем текст методов оплаты
                text = await TextService.get_text(session, "payment_methods", user.language or "ru", user_id)
                
                # Заменяем плейсхолдеры
                from common.services_package.placeholder_service import PlaceholderService
                text = await PlaceholderService.replace_placeholders(session, text, user_id)
                
                # Конвертируем Markdown в HTML
                from .base import MessageFormatter
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем кнопки
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                buttons = [
                    [InlineKeyboardButton("💳 Binance Pay", callback_data="binance_pay")],
                    [InlineKeyboardButton("🪙 Криптокошелек", callback_data="crypto_wallet")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_result")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]

                keyboard = InlineKeyboardMarkup(buttons)

                from telegram.constants import ParseMode
                await update.callback_query.edit_message_text(
                    html_text, 
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )

            return True

        except Exception as e:
            self.log_error(e, "обработка кнопки 'Пополнить баланс'", update.effective_user.id)
            await self.show_error_message(update)
            return False

    async def handle_back_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Назад'"""
        try:
            user_id = update.effective_user.id
            logger.info(f"🔍 handle_back_button вызван для пользователя {user_id}")

            async with async_session_maker() as session:
                # Получаем пользователя
                user = await UserService.get_user_by_tg_id(session, user_id)
                if not user:
                    logger.error(f"❌ Пользователь {user_id} не найден")
                    return False

                # Получаем текст результата проверки
                text = await TextService.get_text(session, "free_check_result", user.language or "ru", user_id)
                
                # Конвертируем Markdown в HTML
                from .base import MessageFormatter
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем динамические кнопки на основе баланса
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                balance = user.balance or 0.0
                paid_check_price = await SettingService.get_paid_check_price(session)
                has_sufficient_balance = balance >= paid_check_price

                buttons = []
                
                if has_sufficient_balance:
                    buttons.extend([
                        [InlineKeyboardButton("🛡️ Глубокий AI-анализ", callback_data="deep_analysis")],
                        [InlineKeyboardButton("📊 Показать пример", callback_data="show_example")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                    ])
                else:
                    buttons.extend([
                        [InlineKeyboardButton("📊 Показать пример", callback_data="show_example")],
                        [InlineKeyboardButton("💰 Пополнить баланс", callback_data="top_up_balance")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                    ])

                keyboard = InlineKeyboardMarkup(buttons)

                from telegram.constants import ParseMode
                await update.callback_query.edit_message_text(
                    html_text, 
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )

            return True

        except Exception as e:
            self.log_error(e, "обработка кнопки 'Назад'", update.effective_user.id)
            await self.show_error_message(update)
            return False

    async def handle_order_paid_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Заказать AI-анализ'"""
        try:
            user_id = update.effective_user.id
            logger.info(f"🔍 handle_order_paid_check вызван для пользователя {user_id}")

            async with async_session_maker() as session:
                # Получаем пользователя
                user = await UserService.get_user_by_tg_id(session, user_id)
                if not user:
                    logger.error(f"❌ Пользователь {user_id} не найден")
                    return False

                # Проверяем баланс
                balance = user.balance or 0.0
                paid_check_price = await SettingService.get_paid_check_price(session)
                
                if balance < paid_check_price:
                    await update.callback_query.answer("❌ Недостаточно средств на балансе!")
                    return True

                # Здесь будет логика платной проверки
                # Пока просто показываем сообщение
                await update.callback_query.answer("🔄 Функция платной проверки в разработке...")

            return True

        except Exception as e:
            self.log_error(e, "обработка кнопки 'Заказать AI-анализ'", update.effective_user.id)
            await self.show_error_message(update)
            return False

    async def handle_insufficient_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать попытку заказа при недостаточном балансе"""
        try:
            await update.callback_query.answer("❌ Недостаточно средств на балансе! Пополните баланс.")
            return True

        except Exception as e:
            self.log_error(e, "обработка недостаточного баланса", update.effective_user.id)
            return False

    async def handle_binance_pay(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Binance Pay'"""
        try:
            await update.callback_query.answer("🔄 Интеграция с Binance Pay в разработке...")
            return True

        except Exception as e:
            self.log_error(e, "обработка Binance Pay", update.effective_user.id)
            return False

    async def handle_crypto_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Криптокошелек'"""
        try:
            await update.callback_query.answer("🔄 Интеграция с криптокошельками в разработке...")
            return True

        except Exception as e:
            self.log_error(e, "обработка криптокошелька", update.effective_user.id)
            return False

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Главное меню'"""
        try:
            # Здесь будет логика возврата в главное меню
            await update.callback_query.answer("🏠 Возврат в главное меню...")
            return True

        except Exception as e:
            self.log_error(e, "обработка главного меню", update.effective_user.id)
            return False

    async def handle_personal_cabinet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать кнопку 'Личный кабинет'"""
        try:
            # Здесь будет логика личного кабинета
            await update.callback_query.answer("👤 Переход в личный кабинет...")
            return True

        except Exception as e:
            self.log_error(e, "обработка личного кабинета", update.effective_user.id)
            return False
