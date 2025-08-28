"""
Обработка сценариев бота
"""
import logging
from typing import Dict, Any, Optional, List
from telegram import Update
from telegram.ext import ContextTypes

from common.database import async_session_maker
from common.services_package.scenario_service import ScenarioService
from common.services import TextService, UserService
from .base import BaseHandler, TriggerDetector, HandlerResult

logger = logging.getLogger(__name__)


class ScenarioHandler(BaseHandler):
    """Обработчик сценариев"""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать обновление"""
        try:
            logger.info(f"🔍 ScenarioHandler.handle вызван для текста: '{update.message.text}'")
            # Определяем триггер
            trigger = await TriggerDetector.detect_trigger(update)
            logger.info(f"🔍 Определен триггер: {trigger}")

            # Сохраняем адрес в контекст если это address_input
            if trigger["type"] == "address_input":
                address = trigger["value"]
                context.user_data["current_address"] = address
                logger.info(f"🔍 Адрес сохранен в контекст: {address}")

            # Ищем подходящий сценарий
            scenario = await self.find_scenario_by_trigger(trigger)

            if scenario and scenario.get("current_stage"):
                logger.info(f"✅ Найден сценарий: {scenario.get('name')}")
                logger.info(f"✅ Текущий этап: {scenario.get('current_stage_id')}")

                # Выполняем этап
                await self.execute_stage(update, context, scenario)
                return True
            else:
                logger.warning("⚠️ Подходящий сценарий не найден")
                return False

        except Exception as e:
            self.log_error(e, "обработка сценария", update.effective_user.id)
            return False

    async def find_scenario_by_trigger(self, trigger: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Поиск подходящего сценария по триггеру"""
        logger.info(f"🔍 Поиск сценария для триггера: {trigger}")

        try:
            async with async_session_maker() as session:
                # Получаем все активные сценарии
                scenarios = await ScenarioService.get_all_scenarios(session)
                logger.info(f"🔍 Получено сценариев: {len(scenarios)}")

                for scenario in scenarios:
                    if not scenario.get("is_active"):
                        continue

                    # Получаем этапы сценария
                    stages = scenario.get("stages", [])
                    logger.info(f"🔍 Сценарий {scenario.get('name')}: {len(stages)} этапов")

                    # Ищем этап с подходящим триггером
                    for stage in stages:
                        stage_id = stage.get("id")
                        stage_trigger = stage.get("trigger")
                        stage_trigger_value = stage.get("trigger_value")
                        stage_name = stage.get("name")

                        logger.info(
                            f"🔍 Проверяем этап {stage_name}: trigger={stage_trigger}, trigger_value={stage_trigger_value}"
                        )

                        # Гибкое сравнение триггеров
                        trigger_match = (
                            stage_trigger == trigger["type"]
                            or (stage_trigger == "command" and trigger["type"] == "command_start")
                            or (stage_trigger == "command_start" and trigger["type"] == "command")
                            or (stage_trigger == "button" and trigger["type"] == "text_equals")
                            or (stage_trigger == "text_equals" and trigger["type"] == "button")
                        )

                        logger.info(f"🔍 trigger_match: {trigger_match}")

                        # Для address_input не проверяем value - любой адрес подходит
                        if stage_trigger == "address_input":
                            value_match = True
                        else:
                            value_match = stage_trigger_value == trigger["value"]

                        if trigger_match and value_match:
                            logger.info(f"✅ Найден подходящий этап: {stage_id} в сценарии {scenario.get('name')}")

                            # Возвращаем сценарий с найденным этапом
                            result_scenario = scenario.copy()
                            result_scenario["current_stage"] = stage
                            result_scenario["current_stage_id"] = stage_id

                            return result_scenario

                logger.warning("⚠️ Подходящий сценарий не найден")
                return None

        except Exception as e:
            self.log_error(e, "поиск сценария по триггеру")
            return None

    async def execute_stage(self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any]):
        """Выполнить этап сценария"""
        try:
            stage = scenario.get("current_stage")
            stage_id = scenario.get("current_stage_id")

            logger.info(f"🔍 Выполняем этап: {stage_id}")

            # Получаем текст этапа
            text_key = stage.get("text_key", "welcome")
            logger.info(f"🔍 Ключ текста: {text_key}")

            # Получаем текст из БД
            async with async_session_maker() as session:
                # Получаем или создаем пользователя
                user_id = update.effective_user.id
                try:
                    user_obj = await UserService.get_or_create_user(session, user_id, "ru", update.effective_user.username)
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось создать пользователя через API: {e}")
                    # Создаем простой объект пользователя для fallback
                    from common.models import User
                    from decimal import Decimal
                    from datetime import datetime

                    user_obj = User(
                        tg_id=user_id,
                        username=update.effective_user.username,
                        language="ru",
                        balance=Decimal("0.0"),
                        referral_code="FALLBACK",
                        is_blocked=False,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    logger.info(f"✅ Создан fallback пользователь: {user_id}")

                # Получаем текст
                language = user_obj.language or "ru"
                text = await TextService.get_text(session, text_key, language, user_id)
                logger.info(f"🔍 Получен текст для ключа '{text_key}': {text[:100]}...")

                # Получаем кнопки из базы данных по языку клиента
                buttons = await self.get_buttons_from_database(session, stage, language, user_id)
                logger.info(f"🔍 Кнопки из БД: {buttons}")

                # Создаем клавиатуру
                from .base import KeyboardBuilder, MessageFormatter

                keyboard = None
                if buttons:
                    keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
                    logger.info(f"🔍 Клавиатура создана")

                # Конвертируем Markdown в HTML
                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Отправляем с HTML парсингом
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                logger.info("✅ Сообщение отправлено")

            # Проверяем условия и выполняем автоматические переходы
            await self.process_stage_conditions(update, context, scenario, user_obj)

        except Exception as e:
            self.log_error(e, "выполнение этапа", update.effective_user.id)
            raise

    async def get_buttons_from_database(self, session, stage: Dict[str, Any], language: str, user_id: int) -> List[str]:
        """Получить кнопки из базы данных по языку клиента"""
        logger.info(f"🔍 Получаем кнопки из БД для языка: {language}")

        try:
            # Получаем кнопки из этапа
            button_keys = stage.get("buttons", [])
            logger.info(f"🔍 Ключи кнопок из этапа: {button_keys}")

            if not button_keys:
                logger.info("🔍 Кнопки не найдены в этапе")
                return []

            # Получаем тексты кнопок из базы данных
            button_texts = []
            for button_key in button_keys:
                try:
                    button_text = await TextService.get_text(session, button_key, language, user_id)
                    button_texts.append(button_text)
                    logger.info(f"🔍 Кнопка '{button_key}' -> '{button_text}'")
                except Exception as e:
                    logger.error(f"❌ Ошибка получения кнопки '{button_key}': {e}")
                    # Если не удалось получить из БД, используем ключ как текст
                    button_texts.append(button_key)

            logger.info(f"🔍 Получены кнопки: {button_texts}")
            return button_texts

        except Exception as e:
            self.log_error(e, "получение кнопок из БД")
            # Возвращаем кнопки из этапа как fallback
            return stage.get("buttons", [])

    async def process_stage_conditions(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], user_obj
    ):
        """Обработать условия этапа"""
        stage = scenario.get("current_stage")
        conditions = stage.get("conditions", [])

        logger.info(f"🔍 Условия этапа: {conditions}")

        if conditions:
            logger.info(f"🔍 Проверяем {len(conditions)} условий этапа")

            for i, condition in enumerate(conditions):
                condition_type = condition.get("type")
                action = condition.get("action")
                next_stage = condition.get("next_stage")

                logger.info(f"🔍 Условие {i+1}: тип={condition_type}, действие={action}, следующий_этап={next_stage}")

                # Проверка валидности адреса
                if condition_type == "address_valid":
                    await self.handle_address_valid_condition(update, context, scenario, condition, user_obj)
                    return

                elif condition_type == "address_invalid":
                    await self.handle_address_invalid_condition(update, context, condition)
                    return

                # Проверка баланса
                elif condition_type == "balance_sufficient" and action == "show_paid_options":
                    await self.handle_balance_sufficient_condition(update, context, scenario, condition, user_obj)
                    return

                elif condition_type == "balance_insufficient" and action == "redirect":
                    await self.transition_to_stage(update, context, scenario, "check_result_stage")
                    return

                elif (
                    condition_type == "balance_insufficient"
                    and action == "execute_check"
                    and condition.get("check_type") == "free_check"
                ):
                    await self.handle_free_check_condition(update, context, scenario, condition, user_obj)
                    return
        else:
            logger.info("🔍 Условий не найдено, проверяем next_stage из этапа")

            # Переход к следующему этапу
            next_stage_name = stage.get("next_stage")
            logger.info(f"🔍 next_stage_name = {next_stage_name}")

            if next_stage_name:
                logger.info(f"🔄 Переходим к следующему этапу: {next_stage_name}")
                await self.transition_to_stage(update, context, scenario, next_stage_name)
            else:
                logger.info("🔍 next_stage не указан, этап завершен")

    async def handle_address_valid_condition(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], condition: Dict[str, Any], user_obj
    ):
        """Обработать условие валидного адреса"""
        logger.info("🔍 Проверяем валидность адреса...")
        address = context.user_data.get("current_address")

        if address and await self.check_address_validity(address):
            logger.info("✅ Адрес валидный")

            # Проверяем действие из условия
            action = condition.get("action")
            if action == "continue" or action == "redirect":
                next_stage = condition.get("next_stage")
                if next_stage:
                    logger.info(f"🔄 Переходим к этапу: {next_stage}")
                    await self.transition_to_stage(update, context, scenario, next_stage)
                else:
                    logger.info("🔄 Переходим к balance_check_stage (по умолчанию)")
                    await self.transition_to_stage(update, context, scenario, "balance_check_stage")

    async def handle_address_invalid_condition(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, condition: Dict[str, Any]
    ):
        """Обработать условие невалидного адреса"""
        logger.info("🔍 Адрес невалидный")
        action = condition.get("action")

        if action == "show_message":
            text_key = condition.get("text_key", "error")
            logger.info(f"❌ Показываем ошибку: {text_key}")
            await self.show_error_message(update, text_key)

    async def handle_balance_sufficient_condition(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], condition: Dict[str, Any], user_obj
    ):
        """Обработать условие достаточного баланса"""
        logger.info("🔍 Проверяем достаточность баланса...")
        balance = await self.check_user_balance(user_obj)

        from common.services import SettingService

        async with async_session_maker() as session:
            paid_check_price = await SettingService.get_paid_check_price(session)

        if balance >= paid_check_price:
            logger.info("✅ Баланс достаточный, показываем опции...")
            text_template = condition.get("text_template")
            if text_template:
                await self.show_options_with_template(update, context, scenario, user_obj, text_template)
            else:
                await self.show_paid_check_options(update, context, scenario, user_obj)

    async def handle_free_check_condition(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], condition: Dict[str, Any], user_obj
    ):
        """Обработать условие бесплатной проверки"""
        logger.info("🔍 Выполняем бесплатную проверку...")
        text_template = condition.get("text_template")
        if text_template:
            await self.execute_check_with_template(update, context, scenario, user_obj, text_template)
        else:
            await self.execute_free_check(update, context, scenario, user_obj)

    async def transition_to_stage(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], target_stage_name: str
    ):
        """Переход к указанному этапу"""
        logger.info(f"🔄 Переходим к этапу: {target_stage_name}")

        try:
            # Находим целевой этап в сценарии
            stages = scenario.get("stages", [])
            target_stage = None

            for stage in stages:
                stage_name = stage.get("name")
                if stage_name == target_stage_name:
                    target_stage = stage
                    break

            if not target_stage:
                logger.error(f"❌ Целевой этап не найден: {target_stage_name}")
                return

            # Проверяем, является ли этап автоматическим переходом
            if target_stage.get("trigger") is None:
                logger.info(f"🔄 Автоматический переход: {target_stage.get('name')}")

                # Если у этапа есть next_stage, переходим к нему
                next_stage_name = target_stage.get("next_stage")
                if next_stage_name:
                    await self.transition_to_stage(update, context, scenario, next_stage_name)
                else:
                    logger.warning(f"⚠️ Автоматический этап {target_stage.get('name')} не имеет next_stage")
            else:
                # Выполняем целевой этап
                await self.execute_stage_simple(update, context, target_stage)

        except Exception as e:
            self.log_error(e, f"переход к этапу {target_stage_name}")

    async def execute_stage_simple(self, update: Update, context: ContextTypes.DEFAULT_TYPE, stage: Dict[str, Any]):
        """Простое выполнение этапа без рекурсии"""
        logger.info(f"🔍 Выполняем этап: {stage.get('id')}")

        try:
            # Получаем текст этапа
            text_key = stage.get("text_key")
            logger.info(f"🔍 Ключ текста: {text_key}")

            # Получаем кнопки из базы данных по языку клиента
            async with async_session_maker() as session:
                # Получаем или создаем пользователя
                user_id = update.effective_user.id
                try:
                    user_obj = await UserService.get_or_create_user(session, user_id, "ru", update.effective_user.username)
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось создать пользователя через API: {e}")
                    # Создаем простой объект пользователя для fallback
                    from common.models import User
                    from decimal import Decimal
                    from datetime import datetime

                    user_obj = User(
                        tg_id=user_id,
                        username=update.effective_user.username,
                        language="ru",
                        balance=Decimal("0.0"),
                        referral_code="FALLBACK",
                        is_blocked=False,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    logger.info(f"✅ Создан fallback пользователь: {user_id}")

                language = user_obj.language or "ru"

                # Получаем кнопки
                buttons = await self.get_buttons_from_database(session, stage, language, user_id)
                logger.info(f"🔍 Кнопки из БД: {buttons}")

                # Создаем клавиатуру
                from .base import KeyboardBuilder, MessageFormatter

                keyboard = None
                if buttons:
                    keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
                    logger.info(f"🔍 Клавиатура создана")

                # Если есть text_key и он не пустой, получаем и отправляем текст
                if text_key and text_key.strip():
                    text = await TextService.get_text(session, text_key, language, user_id)
                    logger.info(f"🔍 Получен текст для ключа '{text_key}': {text[:100]}...")

                    # Конвертируем Markdown в HTML
                    html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                    # Отправляем с HTML парсингом
                    from telegram.constants import ParseMode

                    await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                    logger.info("✅ Сообщение с текстом отправлено")
                else:
                    # Если нет text_key или он пустой, отправляем только клавиатуру
                    if keyboard:
                        await update.message.reply_text("Выберите действие:", reply_markup=keyboard)
                        logger.info("✅ Сообщение только с клавиатурой отправлено")
                    else:
                        logger.info("🔍 Нет текста и кнопок для отправки - этап пропускается")

        except Exception as e:
            self.log_error(e, "простое выполнение этапа")

    async def check_address_validity(self, address: str) -> bool:
        """Проверка валидности адреса"""
        try:
            from common.chain_detector import is_valid_crypto_address

            is_valid = is_valid_crypto_address(address)
            logger.info(f"🔍 Адрес {address} валидный: {is_valid}")
            return is_valid
        except Exception as e:
            self.log_error(e, "проверка валидности адреса")
            return False

    async def check_user_balance(self, user_obj) -> float:
        """Проверка баланса пользователя"""
        try:
            balance = user_obj.balance or 0.0
            logger.info(f"💰 Баланс пользователя {user_obj.tg_id}: {balance}")
            return balance
        except Exception as e:
            self.log_error(e, "проверка баланса")
            return 0.0

    async def show_error_message(self, update: Update, error_type: str):
        """Показ сообщения об ошибке"""
        logger.info(f"❌ Показываем ошибку: {error_type}")

        try:
            async with async_session_maker() as session:
                # Получаем текст ошибки
                user_id = update.effective_user.id
                text = await TextService.get_text(session, error_type, "ru", user_id)

                # Конвертируем в HTML
                from .base import MessageFormatter

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Отправляем ошибку
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.log_error(e, "показ сообщения об ошибке")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

    async def show_options_with_template(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], user_obj, text_template: str
    ):
        """Показ опций с текстом из условия"""
        logger.info(f"🔍 Показываем опции с шаблоном: {text_template}")

        try:
            # Получаем адрес из контекста
            address = context.user_data.get("current_address")
            if not address:
                logger.error("❌ Адрес не найден в контексте")
                await update.message.reply_text("❌ Ошибка: адрес не найден")
                return

            # Получаем текст из шаблона
            async with async_session_maker() as session:
                # Получаем текст из шаблона
                language = user_obj.language or "ru"
                text = await TextService.get_text(session, text_template, language, user_obj.tg_id)

                # Заменяем плейсхолдеры
                text = text.replace("{address}", address)
                text = text.replace("{chain}", "Bitcoin")  # Заглушка
                text = text.replace("{balance}", str(user_obj.balance or 0.0))

                # Получаем цену платной проверки
                from common.services import SettingService

                paid_check_price = await SettingService.get_paid_check_price(session)
                text = text.replace("{paid_check_price}", str(paid_check_price))

                # Конвертируем в HTML
                from .base import MessageFormatter, KeyboardBuilder

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем клавиатуру
                keyboard = KeyboardBuilder.create_check_options_keyboard()

                # Отправляем опции
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                logger.info(f"✅ Опции показаны с шаблоном {text_template}")

        except Exception as e:
            self.log_error(e, "показ опций с шаблоном")
            await update.message.reply_text("❌ Произошла ошибка при показе опций")

    async def show_paid_check_options(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], user_obj
    ):
        """Показ опций платной проверки"""
        logger.info("🔍 Показываем опции платной проверки...")

        try:
            # Получаем адрес из контекста
            address = context.user_data.get("current_address")
            if not address:
                logger.error("❌ Адрес не найден в контексте")
                await update.message.reply_text("❌ Ошибка: адрес не найден")
                return

            # Получаем текст опций
            async with async_session_maker() as session:
                # Получаем текст выбора
                language = user_obj.language or "ru"
                text = await TextService.get_text(session, "check_choice", language, user_obj.tg_id)

                # Заменяем плейсхолдеры
                text = text.replace("{address}", address)
                text = text.replace("{chain}", "Bitcoin")  # Заглушка
                text = text.replace("{balance}", str(user_obj.balance or 0.0))

                # Получаем цену платной проверки
                from common.services import SettingService

                paid_check_price = await SettingService.get_paid_check_price(session)
                text = text.replace("{paid_check_price}", str(paid_check_price))

                # Конвертируем в HTML
                from .base import MessageFormatter, KeyboardBuilder

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем клавиатуру
                keyboard = KeyboardBuilder.create_check_options_keyboard()

                # Отправляем опции
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                logger.info("✅ Опции платной проверки показаны")

        except Exception as e:
            self.log_error(e, "показ опций платной проверки")
            await update.message.reply_text("❌ Произошла ошибка при показе опций")

    async def execute_check_with_template(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], user_obj, text_template: str
    ):
        """Выполнение проверки с текстом из условия"""
        logger.info(f"🔍 execute_check_with_template ВЫЗВАН!")
        logger.info(f"🔍 Выполняем проверку с шаблоном: {text_template}")

        try:
            # Получаем адрес из контекста
            address = context.user_data.get("current_address")
            if not address:
                logger.error("❌ Адрес не найден в контексте")
                await update.message.reply_text("❌ Ошибка: адрес не найден")
                return

            # Определяем блокчейн
            from common.chain_detector import detect_chain
            chain = detect_chain(address)
            logger.info(f"🔍 Определен блокчейн: {chain}")

            # Выполняем реальную проверку через MetaSleuth
            logger.info("🔍 ИМПОРТИРУЕМ MetaSleuthAPI в execute_check_with_template")
            from common.metasleuth import MetaSleuthAPI
            
            logger.info(f"🔍 СОЗДАЕМ экземпляр MetaSleuthAPI в execute_check_with_template")
            metasleuth = MetaSleuthAPI()
            
            logger.info(f"🔍 ВЫЗЫВАЕМ wallet_screening в execute_check_with_template для адреса {address} и сети {chain}")
            check_result = await metasleuth.wallet_screening(address, chain)
            
            logger.info(f"🔍 MetaSleuth результат: {check_result}")
            
            # Проверяем, что получили данные
            if not check_result:
                logger.error("❌ MetaSleuth вернул пустой результат")
                check_result = {"risk": 0, "details": ["Ошибка получения данных"], "percents": {}}

            # Получаем текст из шаблона условия
            async with async_session_maker() as session:
                # Подготавливаем данные MetaSleuth для плейсхолдеров
                risk_score = check_result.get("risk", 0)
                if risk_score <= 1:
                    risk_level = "Низкий"
                elif risk_score <= 3:
                    risk_level = "Средний"
                else:
                    risk_level = "Высокий"
                
                details_list = check_result.get("details", [])
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

                # Получаем текст из шаблона с данными MetaSleuth
                language = user_obj.language or "ru"
                text = await TextService.get_text(session, text_template, language, user_obj.tg_id, additional_data)

                # Конвертируем в HTML
                from .base import MessageFormatter, KeyboardBuilder

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем клавиатуру
                keyboard = KeyboardBuilder.create_payment_keyboard()

                # Отправляем результат
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                logger.info(f"✅ Проверка выполнена с шаблоном {text_template}")

        except Exception as e:
            self.log_error(e, "выполнение проверки с шаблоном")
            await update.message.reply_text("❌ Произошла ошибка при выполнении проверки")

    async def execute_free_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE, scenario: Dict[str, Any], user_obj):
        """Выполнение бесплатной проверки"""
        logger.info("🔍 ScenarioHandler.execute_free_check вызван!")
        logger.info("🔍 Это НОВЫЙ КОД с MetaSleuth!")

        try:
            # Получаем адрес из контекста
            address = context.user_data.get("current_address")
            if not address:
                logger.error("❌ Адрес не найден в контексте")
                await update.message.reply_text("❌ Ошибка: адрес не найден")
                return

            # Определяем блокчейн
            from common.chain_detector import detect_chain
            chain = detect_chain(address)
            logger.info(f"🔍 Определен блокчейн: {chain}")

            # Выполняем реальную проверку через MetaSleuth
            logger.info("🔍 ИМПОРТИРУЕМ MetaSleuthAPI в ScenarioHandler")
            from common.metasleuth import MetaSleuthAPI
            
            logger.info(f"🔍 СОЗДАЕМ экземпляр MetaSleuthAPI в ScenarioHandler")
            metasleuth = MetaSleuthAPI()
            
            logger.info(f"🔍 ВЫЗЫВАЕМ wallet_screening в ScenarioHandler для адреса {address} и сети {chain}")
            check_result = await metasleuth.wallet_screening(address, chain)
            
            logger.info(f"🔍 MetaSleuth результат: {check_result}")
            
            # Проверяем, что получили данные
            if not check_result:
                logger.error("❌ MetaSleuth вернул пустой результат")
                check_result = {"risk": 0, "details": ["Ошибка получения данных"], "percents": {}}

            # Получаем текст результата бесплатной проверки
            async with async_session_maker() as session:
                # Получаем шаблон из настроек
                from common.services import SettingService
                template_setting = await SettingService.get_setting(session, "free_check_template")
                text_key = template_setting if template_setting else "free_check_result"
                
                # Подготавливаем данные MetaSleuth для плейсхолдеров
                risk_score = check_result.get("risk", 0)
                if risk_score <= 1:
                    risk_level = "Низкий"
                elif risk_score <= 3:
                    risk_level = "Средний"
                else:
                    risk_level = "Высокий"
                
                details_list = check_result.get("details", [])
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

                # Получаем текст с данными MetaSleuth
                language = user_obj.language or "ru"
                text = await TextService.get_text(session, text_key, language, user_obj.tg_id, additional_data)
                
                logger.info(f"🔍 Final text: {text}")

                # Конвертируем в HTML
                from .base import MessageFormatter, KeyboardBuilder

                html_text = MessageFormatter.convert_markdown_to_html_simple(text)

                # Создаем клавиатуру
                keyboard = KeyboardBuilder.create_payment_keyboard()

                # Отправляем результат
                from telegram.constants import ParseMode

                await update.message.reply_text(html_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                logger.info("✅ Бесплатная проверка выполнена")

        except Exception as e:
            self.log_error(e, "выполнение бесплатной проверки")
            await update.message.reply_text("❌ Произошла ошибка при выполнении проверки")
