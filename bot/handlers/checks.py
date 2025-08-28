"""
Обработка проверок криптовалютных адресов
"""
import logging
from typing import Dict, Any, Optional, Tuple
from telegram import Update
from telegram.ext import ContextTypes

from common.database import async_session_maker
from common.services import UserService, CheckService, TextService, SettingService
from common.chain_detector import detect_chain, is_valid_crypto_address
from .base import BaseHandler, HandlerResult

logger = logging.getLogger(__name__)


class CheckHandler(BaseHandler):
    """Обработчик проверок адресов"""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать проверку адреса"""
        try:
            # Получаем адрес из сообщения
            address = update.message.text.strip()
            user_id = update.effective_user.id

            logger.info(f"🔍 CheckHandler.handle вызван для адреса: {address}")

            # Проверяем валидность адреса
            if not is_valid_crypto_address(address):
                await self.handle_invalid_address(update, address)
                return True

            # Определяем блокчейн
            chain = detect_chain(address)
            logger.info(f"🔍 Определен блокчейн: {chain}")

            # Получаем пользователя
            async with async_session_maker() as session:
                user = await UserService.get_or_create_user(session, user_id, "ru", update.effective_user.username)

                # Проверяем баланс и лимиты
                logger.info("🔍 Проверяем баланс и лимиты")
                check_result = await self.check_user_limits(session, user)
                logger.info(f"🔍 check_result: {check_result}")

                if check_result["can_check"]:
                    # Выполняем проверку
                    logger.info("🔍 ВЫЗЫВАЕМ execute_check!")
                    await self.execute_check(update, context, address, chain, user, check_result["check_type"])
                else:
                    # Показываем сообщение о лимитах
                    logger.info("🔍 Пользователь не может проверять, показываем лимиты")
                    await self.show_limits_message(update, user, check_result)

            return True

        except Exception as e:
            self.log_error(e, "обработка проверки адреса", update.effective_user.id)
            await self.show_error_message(update)
            return False

    async def handle_invalid_address(self, update: Update, address: str):
        """Обработать невалидный адрес"""
        logger.warning(f"⚠️ Невалидный адрес: {address}")

        try:
            async with async_session_maker() as session:
                user_id = update.effective_user.id
                text = await TextService.get_text(session, "invalid_address", "ru", user_id)

                from .base import MessageFormatter

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "обработка невалидного адреса")
            await update.message.reply_text("❌ Неверный формат адреса. Проверьте правильность ввода.")

    async def check_user_limits(self, session, user) -> Dict[str, Any]:
        """Проверить лимиты пользователя"""
        try:
            logger.info(f"🔍 check_user_limits: проверяем пользователя {user.tg_id}")
            
            # Проверяем, заблокирован ли пользователь
            if UserService.is_user_blocked(user):
                logger.info("🔍 check_user_limits: пользователь заблокирован")
                return {"can_check": False, "reason": "blocked", "message": "Пользователь заблокирован"}

            # Проверяем баланс
            balance = user.balance or 0.0
            paid_check_price = await SettingService.get_paid_check_price(session)
            logger.info(f"🔍 check_user_limits: баланс {balance}, цена {paid_check_price}")

            if balance >= paid_check_price:
                logger.info("🔍 check_user_limits: достаточно баланса для платной проверки")
                return {"can_check": True, "check_type": "paid", "balance": balance, "price": paid_check_price}

            # Проверяем лимиты бесплатных проверок
            logger.info("🔍 check_user_limits: проверяем бесплатные проверки")
            can_use_free, remaining = await UserService.can_use_free_check(session, user)
            logger.info(f"🔍 check_user_limits: can_use_free={can_use_free}, remaining={remaining}")

            if can_use_free:
                logger.info("🔍 check_user_limits: можно использовать бесплатную проверку")
                return {"can_check": True, "check_type": "free", "balance": balance, "remaining_free": remaining}
            else:
                logger.info("🔍 check_user_limits: лимит бесплатных проверок исчерпан")
                return {
                    "can_check": False,
                    "reason": "limit_exceeded",
                    "balance": balance,
                    "remaining_free": remaining,
                    "price": paid_check_price,
                }

        except Exception as e:
            self.log_error(e, "проверка лимитов пользователя")
            return {"can_check": False, "reason": "error", "message": "Ошибка проверки лимитов"}

    async def execute_check(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, address: str, chain: str, user, check_type: str
    ):
        """Выполнить проверку адреса"""
        logger.info(f"🔍 CheckHandler.execute_check ВЫЗВАН!")
        logger.info(f"🔍 CheckHandler.execute_check вызван для {check_type} проверки адреса {address}")
        logger.info(f"🔍 Это НОВЫЙ КОД с MetaSleuth!")
        logger.info(f"🔍 СТРОКА 116: CheckHandler.execute_check вызван для {check_type} проверки адреса {address}")

        try:
            # Показываем сообщение о начале проверки
            await update.message.reply_text("🔍 Выполняю проверку адреса...\n\n⏳ Это займет несколько секунд...")

            # Выполняем реальную проверку через MetaSleuth
            logger.info("🔍 ИМПОРТИРУЕМ MetaSleuthAPI в CheckHandler")
            from common.metasleuth import MetaSleuthAPI
            
            logger.info(f"🔍 СОЗДАЕМ экземпляр MetaSleuthAPI в CheckHandler")
            metasleuth = MetaSleuthAPI()
            
            logger.info(f"🔍 ВЫЗЫВАЕМ wallet_screening в CheckHandler для адреса {address} и сети {chain}")
            check_result = await metasleuth.wallet_screening(address, chain)
            
            logger.info(f"🔍 MetaSleuth результат в CheckHandler: {check_result}")
            
            # ВЫЗЫВАЕМ address_label (ДОБАВЛЕНО)
            logger.info(f"🔍 ВЫЗЫВАЕМ address_label в CheckHandler для адреса {address} и сети {chain}")
            label_result = await metasleuth.address_label(address, chain)
            logger.info(f"🔍 Address Label результат в CheckHandler: {label_result}")
            
            # Объединяем результаты
            check_result["label_data"] = label_result
            
            # Проверяем, что получили данные
            if not check_result:
                logger.error("❌ MetaSleuth вернул пустой результат в CheckHandler")
                check_result = {"risk": 0, "details": ["Ошибка получения данных"], "percents": {}}

            # Создаем запись о проверке
            async with async_session_maker() as session:
                # Создаем проверку в БД
                from common.models import CheckType

                check_type_enum = CheckType.PAID if check_type == "paid" else CheckType.FREE

                check = await CheckService.create_check(  # noqa: F841
                    session=session,
                    user_id=user.tg_id,
                    address=address,
                    chain=chain,
                    check_type=check_type_enum,
                    result=check_result,
                )

                # Обновляем время последней бесплатной проверки
                if check_type == "free":
                    await UserService.update_last_free_check(session, user)

                # Получаем результат проверки с реальными данными
                result_text = await self.get_check_result_text_with_metasleuth(session, address, chain, check_type, user, check_result)

                # Отправляем результат с динамическими кнопками
                await self.send_check_result_with_dynamic_buttons(update, result_text, check_type, user)

                logger.info(f"✅ {check_type} проверка завершена")

        except Exception as e:
            self.log_error(e, "выполнение проверки", update.effective_user.id)
            await self.show_error_message(update)

    async def get_check_result_text_with_metasleuth(self, session, address: str, chain: str, check_type: str, user, metasleuth_result: Dict) -> str:
        """Получить текст результата проверки с данными MetaSleuth"""
        try:
            logger.info(f"🔍 get_check_result_text_with_metasleuth вызван")
            logger.info(f"🔍 metasleuth_result: {metasleuth_result}")
            # Получаем шаблон из настроек
            template_key = "paid_check_template" if check_type == "paid" else "free_check_template"
            template_setting = await SettingService.get_setting(session, template_key)
            text_key = template_setting if template_setting else ("paid_check_result" if check_type == "paid" else "free_check_result")
            
            # Подготавливаем данные MetaSleuth для плейсхолдеров
            risk_score = metasleuth_result.get("risk", 0)
            
            # Определяем язык
            language = user.language or "ru"
            
            # Определяем уровень риска с цветными эмодзи
            if language == "ru":
                # Русская версия
                if risk_score <= 1:
                    risk_level = "🟢 БЕЗОПАСНЫЙ"
                elif risk_score == 2:
                    risk_level = "🟢 НИЗКИЙ"
                elif risk_score == 3:
                    risk_level = "🟡 СРЕДНИЙ"
                elif risk_score == 4:
                    risk_level = "🟠 ВЫСОКИЙ"
                else:
                    risk_level = "🔴 КРИТИЧЕСКИЙ"
            else:
                # Английская версия
                if risk_score <= 1:
                    risk_level = "🟢 SAFE"
                elif risk_score == 2:
                    risk_level = "🟢 LOW"
                elif risk_score == 3:
                    risk_level = "🟡 MEDIUM"
                elif risk_score == 4:
                    risk_level = "🟠 HIGH"
                else:
                    risk_level = "🔴 CRITICAL"
            
            details_list = metasleuth_result.get("details", [])
            if isinstance(details_list, list):
                risk_details = "\n• ".join(details_list)
                if risk_details:
                    risk_details = "• " + risk_details
                else:
                    risk_details = "Детали недоступны"
            else:
                risk_details = str(details_list) if details_list else "Детали недоступны"

            # Создаем additional_data для плейсхолдеров
            additional_data = {
                "address": address,
                "chain": chain,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_details": risk_details
            }
            
            # Добавляем данные метки адреса
            label_data = metasleuth_result.get("label_data", {})
            if label_data and label_data.get("label") and label_data.get("label") != "Неизвестный адрес":
                additional_data["label"] = label_data.get("label", "Неизвестный адрес")
                additional_data["address_type"] = label_data.get("type", "unknown")
                additional_data["website"] = label_data.get("website", "Неизвестно")
                
                # Формируем статус адреса на основе атрибутов
                attributes = label_data.get("attributes", [])
                status_parts = []
                
                # Проверяем что attributes не None и является списком
                if attributes and isinstance(attributes, list):
                    for attr in attributes:
                        if attr.get("name") == "BLOCKED":
                            status_parts.append("Заблокирован")
                        elif attr.get("name") == "SANCTIONED":
                            status_parts.append("Санкционирован")
                        elif attr.get("name") == "DEPOSIT ADDRESS":
                            status_parts.append("Депозитный адрес")
                
                if status_parts:
                    additional_data["address_status"] = ", ".join(status_parts)
                else:
                    additional_data["address_status"] = "Без ограничений"
            else:
                # Если нет данных от Address Label API, показываем базовую информацию
                additional_data["label"] = "Неизвестный адрес"
                additional_data["address_type"] = "unknown"
                additional_data["website"] = "Неизвестно"
                additional_data["address_status"] = "Без ограничений"

            # Получаем текст с данными MetaSleuth
            logger.info(f"🔍 Передаем additional_data в TextService: {additional_data}")
            text = await TextService.get_text(session, text_key, language, user.tg_id, additional_data)
            
            logger.info(f"🔍 Final text: {text}")

            return text

        except Exception as e:
            self.log_error(e, "получение текста результата с MetaSleuth")
            return f"🔍 Проверка адреса {address} завершена.\n\nБлокчейн: {chain}\nТип: {check_type}"

    async def get_check_result_text(self, session, address: str, chain: str, check_type: str, user) -> str:
        """Получить текст результата проверки (legacy)"""
        try:
            # Получаем базовый текст результата
            text_key = "paid_check_result" if check_type == "paid" else "free_check_result"
            language = user.language or "ru"

            text = await TextService.get_text(session, text_key, language, user.tg_id)

            # Заменяем плейсхолдеры
            text = text.replace("{address}", address)
            text = text.replace("{chain}", chain)
            text = text.replace("{balance}", str(user.balance or 0.0))

            # Получаем цену платной проверки
            paid_check_price = await SettingService.get_paid_check_price(session)
            text = text.replace("{paid_check_price}", str(paid_check_price))

            # Добавляем информацию о типе проверки
            check_type_text = "🛡️ Платная проверка" if check_type == "paid" else "✅ Бесплатная проверка"
            text = text.replace("{check_type}", check_type_text)

            return text

        except Exception as e:
            self.log_error(e, "получение текста результата")
            return f"🔍 Проверка адреса {address} завершена.\n\nБлокчейн: {chain}\nТип: {check_type}"

    async def send_check_result_with_dynamic_buttons(self, update: Update, result_text: str, check_type: str, user):
        """Отправить результат проверки с динамическими кнопками управления через Bot Flow Designer"""
        try:
            from .base import MessageFormatter, KeyboardBuilder
            from telegram.constants import ParseMode
            from common.services import ScenarioService

            # Конвертируем в HTML
            html_text = MessageFormatter.convert_markdown_to_html_simple(result_text)

            # Получаем сценарий из Bot Flow Designer
            async with async_session_maker() as session:
                scenario = await ScenarioService.get_scenario_by_id("address_check_flow")
                
                if not scenario:
                    logger.warning("Сценарий 'address_check_flow' не найден, используем fallback")
                    # Fallback на старую логику
                    balance = user.balance or 0.0
                    paid_check_price = await SettingService.get_paid_check_price(session)
                    
                    if balance >= paid_check_price:
                        buttons_setting = await SettingService.get_setting(session, "rich_result_buttons")
                        button_text = buttons_setting if buttons_setting else "🛡️ Глубокий AI-анализ|📊 Показать пример|🏠 Главное меню"
                    else:
                        buttons_setting = await SettingService.get_setting(session, "poor_result_buttons")
                        button_text = buttons_setting if buttons_setting else "📊 Показать пример|💰 Пополнить баланс|🏠 Главное меню"
                    
                    keyboard = KeyboardBuilder.create_dynamic_keyboard(button_text)
                else:
                    # Используем Bot Flow Designer
                    stages = scenario.get("stages", [])
                    check_result_stage = None
                    
                    # Находим этап "Результат бесплатной проверки"
                    for stage in stages:
                        if stage.get("id") == "check_result_stage":
                            check_result_stage = stage
                            break
                    
                    if check_result_stage:
                        # Оцениваем условия и получаем кнопки
                        conditions = check_result_stage.get("conditions", [])
                        balance = user.balance or 0.0
                        paid_check_price = await SettingService.get_paid_check_price(session)
                        
                        buttons = []
                        for condition in conditions:
                            condition_type = condition.get("type")
                            
                            if condition_type == "balance_sufficient" and balance >= paid_check_price:
                                buttons = condition.get("buttons", [])
                                break
                            elif condition_type == "balance_insufficient" and balance < paid_check_price:
                                buttons = condition.get("buttons", [])
                                break
                        
                        if buttons:
                            keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
                        else:
                            # Fallback если условия не сработали
                            keyboard = KeyboardBuilder.create_dynamic_keyboard("📊 Показать пример|💰 Пополнить баланс|🏠 Главное меню")
                    else:
                        # Fallback если этап не найден
                        keyboard = KeyboardBuilder.create_dynamic_keyboard("📊 Показать пример|💰 Пополнить баланс|🏠 Главное меню")

            # Отправляем результат
            await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "отправка результата с динамическими кнопками")
            await update.message.reply_text("❌ Ошибка отправки результата")

    async def send_check_result(self, update: Update, result_text: str, check_type: str):
        """Отправить результат проверки (legacy)"""
        try:
            from .base import MessageFormatter, KeyboardBuilder
            from telegram.constants import ParseMode

            # Конвертируем в HTML
            html_text = MessageFormatter.convert_markdown_to_html_simple(result_text)

            # Создаем клавиатуру
            keyboard = KeyboardBuilder.create_payment_keyboard()

            # Отправляем результат
            await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "отправка результата проверки")
            await update.message.reply_text("❌ Ошибка отправки результата")

    async def show_limits_message(self, update: Update, user, check_result: Dict[str, Any]):
        """Показать сообщение о лимитах"""
        try:
            async with async_session_maker() as session:
                user_id = update.effective_user.id

                if check_result["reason"] == "blocked":
                    text = await TextService.get_text(session, "user_blocked", "ru", user_id)
                elif check_result["reason"] == "limit_exceeded":
                    text = await TextService.get_text(session, "free_limit_exceeded", "ru", user_id)
                    text = text.replace("{remaining_free}", str(check_result["remaining_free"]))
                    text = text.replace("{price}", str(check_result["price"]))
                else:
                    text = "❌ Превышен лимит бесплатных проверок. Пополните баланс для продолжения."

                from .base import MessageFormatter, KeyboardBuilder
                from telegram.constants import ParseMode

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)
                keyboard = KeyboardBuilder.create_payment_keyboard()

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "показ сообщения о лимитах")
            await update.message.reply_text("❌ Превышен лимит проверок. Пополните баланс.")

    async def show_error_message(self, update: Update):
        """Показать сообщение об ошибке"""
        try:
            async with async_session_maker() as session:
                user_id = update.effective_user.id
                text = await TextService.get_text(session, "check_error", "ru", user_id)

                from .base import MessageFormatter

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "показ сообщения об ошибке")
            await update.message.reply_text("❌ Произошла ошибка при проверке адреса. Попробуйте позже.")


class CheckValidator:
    """Валидатор проверок"""

    @staticmethod
    async def validate_address(address: str) -> Tuple[bool, Optional[str]]:
        """Проверить валидность адреса"""
        if not address or len(address.strip()) < 10:
            return False, "Адрес слишком короткий"

        if not is_valid_crypto_address(address):
            return False, "Неверный формат адреса"

        return True, None

    @staticmethod
    async def validate_user_permissions(user_id: int) -> Tuple[bool, Optional[str]]:
        """Проверить права пользователя на проверку"""
        try:
            async with async_session_maker() as session:
                user = await UserService.get_user_by_tg_id(session, user_id)

                if not user:
                    return False, "Пользователь не найден"

                if UserService.is_user_blocked(user):
                    return False, "Пользователь заблокирован"

                return True, None

        except Exception as e:
            logger.error(f"Ошибка проверки прав пользователя: {e}")
            return False, "Ошибка проверки прав"

    @staticmethod
    async def get_check_cost(user_id: int) -> float:
        """Получить стоимость проверки для пользователя"""
        try:
            async with async_session_maker() as session:
                return await SettingService.get_paid_check_price(session)
        except Exception as e:
            logger.error(f"Ошибка получения стоимости проверки: {e}")
            return 1.0  # Значение по умолчанию


class CheckResultFormatter:
    """Форматировщик результатов проверок"""

    @staticmethod
    def format_chain_info(chain: str) -> str:
        """Форматировать информацию о блокчейне"""
        chain_emojis = {
            "btc": "₿",
            "eth": "Ξ",
            "tron": "TRX",
            "solana": "◎",
            "optimism": "OP",
            "cronos": "CRO",
            "bsc": "BNB",
            "gnosis": "XDAI",
            "polygon": "MATIC",
            "manta": "MANTA",
            "bittorrent": "BTT",
            "fantom": "FTM",
            "boba": "BOBA",
            "zksync": "ZK",
            "clv": "CLV",
            "polygonzkevm": "zkEVM",
            "wemix": "WEMIX",
            "moonbeam": "GLMR",
            "moonriver": "MOVR",
            "mantle": "MNT",
            "base": "BASE",
            "arbitrum": "ARB",
            "celo": "CELO",
            "avalanche": "AVAX",
            "linea": "LINEA",
            "blast": "BLAST",
            "aurora": "AURORA",
        }

        emoji = chain_emojis.get(chain.lower(), "🔗")
        return f"{emoji} {chain.upper()}"

    @staticmethod
    def format_address(address: str) -> str:
        """Форматировать адрес для отображения"""
        if len(address) > 20:
            return f"{address[:10]}...{address[-10:]}"
        return address

    @staticmethod
    def format_balance(balance: float) -> str:
        """Форматировать баланс"""
        return f"${balance:.2f}"

    @staticmethod
    def format_check_type(check_type: str) -> str:
        """Форматировать тип проверки"""
        if check_type == "paid":
            return "🛡️ Платная проверка"
        else:
            return "✅ Бесплатная проверка"
