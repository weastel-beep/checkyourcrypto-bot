"""
Сервис для работы со сценариями бота через API конструктора
"""
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_handling import (
    get_retry_decorator,
    http_circuit_breaker,
    ErrorHandler,
    create_timeout_decorator,
    RetryConfig,
)

logger = logging.getLogger(__name__)


class ScenarioService:
    """Сервис для работы со сценариями через API конструктора"""

    @staticmethod
    def get_api_base_url() -> str:
        """Получить базовый URL API из конфига"""
        from common.services_legacy import get_api_base_url

        base_url = get_api_base_url()
        logger.info(f"🔍 ScenarioService: Используем API URL: {base_url}")
        return base_url

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_active_scenario(session: AsyncSession) -> Optional[Dict[str, Any]]:
        """Получить активный сценарий через API"""
        try:
            import aiohttp

            logger.info("🔍 ScenarioService: Запрашиваем активный сценарий через API")

            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(f"{ScenarioService.get_api_base_url()}/api/bot-flow/scenarios") as response:
                    if response.status == 200:
                        scenarios = await response.json()

                        # Ищем активный сценарий
                        for scenario in scenarios:
                            if scenario.get("is_active"):
                                logger.info(f"✅ Получен активный сценарий через API: {scenario.get('name')}")
                                return scenario

                        logger.warning("⚠️ Активный сценарий не найден через API")
                        return None
                    else:
                        error_msg = f"API вернул статус {response.status} для сценариев"
                        ErrorHandler.log_error(Exception(error_msg), "получение активного сценария")
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, "получение активного сценария через API")
            return None

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_all_scenarios(session: AsyncSession) -> List[Dict[str, Any]]:
        """Получить все сценарии через API"""
        try:
            import aiohttp

            api_url = f"{ScenarioService.get_api_base_url()}/api/bot-flow/scenarios"
            logger.info(f"🔍 ScenarioService: Запрашиваем все сценарии через API: {api_url}")

            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(api_url) as response:
                    if response.status == 200:
                        scenarios = await response.json()
                        logger.info(f"✅ Получено {len(scenarios)} сценариев через API")
                        return scenarios
                    else:
                        error_msg = f"API вернул статус {response.status} для сценариев"
                        ErrorHandler.log_error(Exception(error_msg), "получение всех сценариев")
                        return []

        except Exception as e:
            ErrorHandler.log_error(e, "получение сценариев через API")
            return []

    @staticmethod
    async def get_stage(scenario: Dict[str, Any], stage_name: str) -> Optional[Dict[str, Any]]:
        """Получить конкретную стадию из сценария"""
        try:
            stages = scenario.get("stages", [])

            # API возвращает стадии как массив объектов, а не как объект с ключами
            if isinstance(stages, list):
                # Ищем стадию по id или name
                for stage in stages:
                    if stage.get("id") == stage_name or stage.get("name") == stage_name:
                        logger.info(f"✅ Получена стадия '{stage_name}' из сценария")
                        return stage

                logger.warning(f"⚠️ Стадия '{stage_name}' не найдена в сценарии")
                return None
            else:
                # Fallback для старого формата (объект с ключами)
                stage = stages.get(stage_name)
                if stage:
                    logger.info(f"✅ Получена стадия '{stage_name}' из сценария (старый формат)")
                    return stage
                else:
                    logger.warning(f"⚠️ Стадия '{stage_name}' не найдена в сценарии")
                    return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение стадии '{stage_name}'")
            return None

    @staticmethod
    async def get_next_stage(scenario: Dict[str, Any], current_stage: str) -> Optional[str]:
        """Получить следующую стадию"""
        try:
            stage = await ScenarioService.get_stage(scenario, current_stage)
            if stage:
                return stage.get("next")
            return None
        except Exception as e:
            ErrorHandler.log_error(e, "получение следующей стадии")
            return None

    @staticmethod
    async def get_stage_type(scenario: Dict[str, Any], stage_name: str) -> Optional[str]:
        """Получить тип стадии"""
        try:
            stage = await ScenarioService.get_stage(scenario, stage_name)
            if stage:
                return stage.get("type")
            return None
        except Exception as e:
            ErrorHandler.log_error(e, "получение типа стадии")
            return None

    @staticmethod
    async def get_stage_text_category(scenario: Dict[str, Any], stage_name: str) -> Optional[str]:
        """Получить категорию текста для стадии"""
        try:
            stage = await ScenarioService.get_stage(scenario, stage_name)
            if stage:
                return stage.get("text_category")
            return None
        except Exception as e:
            ErrorHandler.log_error(e, "получение категории текста")
            return None

    @staticmethod
    async def get_stage_buttons(scenario: Dict[str, Any], stage_name: str) -> List[Dict[str, Any]]:
        """Получить кнопки для стадии"""
        logger.info(f"🔍 get_stage_buttons: ищем кнопки для стадии {stage_name}")
        try:
            stage = await ScenarioService.get_stage(scenario, stage_name)
            logger.info(f"🔍 Стадия найдена: {stage}")

            if stage:
                # В новом формате кнопки хранятся как массив строк
                buttons = stage.get("buttons", [])
                logger.info(f"🔍 Кнопки в стадии: {buttons}")

                if isinstance(buttons, list):
                    # Преобразуем строки в объекты для совместимости
                    result = [{"text": button} if isinstance(button, str) else button for button in buttons]
                    logger.info(f"🔍 Преобразованные кнопки: {result}")
                    return result
            logger.warning(f"⚠️ Кнопки не найдены для стадии {stage_name}")
            return []
        except Exception as e:
            ErrorHandler.log_error(e, "получение кнопок")
            return []

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_scenario_by_id(session: AsyncSession, scenario_id: int) -> Optional[Dict[str, Any]]:
        """Получить сценарий по ID через API"""
        try:
            import aiohttp

            logger.info(f"🔍 ScenarioService: Запрашиваем сценарий с ID {scenario_id} через API")

            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(f"{ScenarioService.get_api_base_url()}/api/bot-flow/scenarios/{scenario_id}") as response:
                    if response.status == 200:
                        scenario = await response.json()
                        logger.info(f"✅ Получен сценарий с ID {scenario_id} через API: {scenario.get('name')}")
                        return scenario
                    else:
                        error_msg = f"API вернул статус {response.status} для сценария с ID {scenario_id}"
                        ErrorHandler.log_error(Exception(error_msg), "получение сценария по ID")
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение сценария с ID {scenario_id} через API")
            return None

    @staticmethod
    async def replace_placeholders_in_text(session: AsyncSession, text: str, user_id: int) -> str:
        """Заменить плейсхолдеры в тексте на реальные значения пользователя"""
        try:
            from .placeholder_service import PlaceholderService

            return await PlaceholderService.replace_placeholders(session, text, user_id)
        except Exception as e:
            ErrorHandler.log_error(e, "замена плейсхолдеров", user_id)
            return text
