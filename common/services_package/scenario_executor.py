"""
Автоматический исполнитель сценариев из конструктора
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ScenarioExecutor:
    """Автоматический исполнитель сценариев из конструктора"""

    @staticmethod
    async def execute_stage(
        session: AsyncSession, scenario: Dict[str, Any], stage_id: str, user_id: int, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Автоматически выполняет стадию сценария из конструктора

        Args:
            session: Сессия БД
            scenario: Сценарий из API
            stage_id: ID стадии для выполнения
            user_id: ID пользователя
            context: Контекст (адрес, данные и т.д.)

        Returns:
            Результат выполнения: {action, next_stage, text, buttons, etc.}
        """
        try:
            from .scenario_service import ScenarioService
            from common.services_legacy import TextService, UserService, SettingService

            # Получаем стадию
            stage = await ScenarioService.get_stage(scenario, stage_id)
            if not stage:
                logger.error(f"❌ Стадия {stage_id} не найдена")
                return {"error": f"Stage {stage_id} not found"}

            logger.info(f"🔍 Выполняем стадию: {stage_id} ({stage.get('name', 'Unknown')})")

            # Получаем пользователя
            user_obj = await UserService.get_user_by_tg_id(session, user_id)
            if not user_obj:
                logger.error(f"❌ Пользователь {user_id} не найден")
                return {"error": "User not found"}

            # Получаем текст стадии с заменой плейсхолдеров
            text_key = stage.get("text_key", "unknown")
            text = await TextService.get_text(session, text_key, user_obj.language or "ru", user_id)

            # Конвертируем Markdown в HTML
            import re

            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

            # Получаем кнопки стадии
            logger.info(f"🔍 Получаем кнопки для стадии {stage_id}...")
            buttons = await ScenarioService.get_stage_buttons(scenario, stage_id)
            logger.info(f"🔍 Получены кнопки: {buttons}")

            # Проверяем условия и определяем следующее действие
            # НО НЕ ПЕРЕХОДИМ К СЛЕДУЮЩЕЙ СТАДИИ - только выполняем текущую
            next_action = {"action": "end"}  # Всегда останавливаемся на текущей стадии

            result = {
                "stage_id": stage_id,
                "stage_name": stage.get("name", "Unknown"),
                "text": text,
                "buttons": buttons,
                "next_action": next_action,
            }

            logger.info(f"✅ Стадия {stage_id} выполнена: {next_action}")
            logger.info(f"🔍 РЕЗУЛЬТАТ: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ Ошибка выполнения стадии {stage_id}: {e}")
            return {"error": str(e)}

    @staticmethod
    async def _evaluate_conditions(
        session: AsyncSession, stage: Dict[str, Any], user_obj, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Оценивает условия стадии и определяет следующее действие"""
        try:
            conditions = stage.get("conditions", [])
            context = context or {}

            logger.info(f"🔍 Условия стадии: {conditions}")

            if not conditions:
                logger.warning(f"⚠️ Нет условий в стадии!")
                # Если ни одно условие не выполнено, используем next_stage из стадии
                default_next = stage.get("next_stage")
                if default_next:
                    logger.info(f"🔄 Переходим к следующей стадии по умолчанию: {default_next}")
                    return {"action": "continue", "next_stage": default_next}

                return {"action": "end"}

            for condition in conditions:
                condition_type = condition.get("type")
                action = condition.get("action")

                logger.info(f"🔍 Проверяем условие: {condition_type} -> {action}")

                # Проверяем условие
                condition_met = await ScenarioExecutor._check_condition(session, condition_type, user_obj, context)

                if condition_met:
                    logger.info(f"✅ Условие {condition_type} выполнено")
                    return {
                        "action": action,
                        "next_stage": condition.get("next_stage") or condition.get("target_stage"),
                        "text_key": condition.get("text_key"),
                        "check_type": condition.get("check_type"),
                    }

            # Если ни одно условие не выполнено, используем next_stage из стадии
            default_next = stage.get("next_stage")
            if default_next:
                logger.info(f"🔄 Переходим к следующей стадии по умолчанию: {default_next}")
                return {"action": "continue", "next_stage": default_next}

            return {"action": "end"}

        except Exception as e:
            logger.error(f"❌ Ошибка оценки условий: {e}")
            return {"action": "error", "error": str(e)}

    @staticmethod
    async def _check_condition(session: AsyncSession, condition_type: str, user_obj, context: Dict[str, Any]) -> bool:
        """Проверяет конкретное условие"""
        try:
            from common.services_legacy import SettingService

            if condition_type == "user_blocked":
                result = user_obj.is_blocked
                return result

            elif condition_type == "address_valid":
                address = context.get("address", "")
                # Используем реальную валидацию адреса
                from common.chain_detector import is_valid_crypto_address

                is_valid = is_valid_crypto_address(address)
                logger.info(f"🔍 Проверка адреса '{address}': валиден = {is_valid}")
                return is_valid

            elif condition_type == "address_invalid":
                address = context.get("address", "")
                # Используем реальную валидацию адреса
                from common.chain_detector import is_valid_crypto_address

                is_valid = is_valid_crypto_address(address)
                logger.info(f"🔍 Проверка адреса '{address}': невалиден = {not is_valid}")
                return not is_valid

            elif condition_type == "balance_sufficient":
                paid_check_price = await SettingService.get_paid_check_price(session)
                return user_obj.balance >= paid_check_price

            elif condition_type == "balance_insufficient":
                paid_check_price = await SettingService.get_paid_check_price(session)
                return user_obj.balance < paid_check_price

            else:
                logger.warning(f"⚠️ Неизвестный тип условия: {condition_type}")
                return False

        except Exception as e:
            logger.error(f"❌ Ошибка проверки условия {condition_type}: {e}")
            return False
