"""
Базовые классы для интеграций - новая архитектура
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Базовый класс для всех провайдеров"""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.is_active = True
        self.last_check = None
        self.error_count = 0
        self.max_errors = 3

    @abstractmethod
    async def check_health(self) -> bool:
        """Проверить здоровье провайдера"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Получить статус провайдера"""
        pass

    def mark_error(self):
        """Отметить ошибку провайдера"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.is_active = False
            logger.warning(f"Провайдер {self.name} деактивирован из-за ошибок")

    def mark_success(self):
        """Отметить успешную операцию"""
        self.error_count = 0
        self.last_check = datetime.now()
        if not self.is_active:
            self.is_active = True
            logger.info(f"Провайдер {self.name} реактивирован")


class BaseIntegration(ABC):
    """Базовый класс для интеграций"""

    def __init__(self, integration_type: str):
        self.integration_type = integration_type
        self.providers: Dict[str, BaseProvider] = {}
        self.active_provider: Optional[str] = None

    def add_provider(self, provider: BaseProvider):
        """Добавить провайдера"""
        self.providers[provider.name] = provider
        if not self.active_provider:
            self.active_provider = provider.name
            logger.info(f"Установлен активный провайдер: {provider.name}")

    def remove_provider(self, provider_name: str):
        """Удалить провайдера"""
        if provider_name in self.providers:
            del self.providers[provider_name]
            if self.active_provider == provider_name:
                self.active_provider = next(iter(self.providers.keys()), None)
                logger.info(f"Активный провайдер изменен на: {self.active_provider}")

    def set_active_provider(self, provider_name: str) -> bool:
        """Установить активного провайдера"""
        if provider_name in self.providers:
            self.active_provider = provider_name
            logger.info(f"Активный провайдер изменен на: {provider_name}")
            return True
        logger.error(f"Провайдер {provider_name} не найден")
        return False

    def get_active_provider(self) -> Optional[BaseProvider]:
        """Получить активного провайдера"""
        if self.active_provider and self.active_provider in self.providers:
            return self.providers[self.active_provider]
        return None

    def get_all_providers(self) -> List[BaseProvider]:
        """Получить всех провайдеров"""
        return list(self.providers.values())

    def get_provider_status(self) -> Dict[str, Any]:
        """Получить статус всех провайдеров"""
        status = {"integration_type": self.integration_type, "active_provider": self.active_provider, "providers": {}}

        for name, provider in self.providers.items():
            status["providers"][name] = {
                "is_active": provider.is_active,
                "error_count": provider.error_count,
                "last_check": provider.last_check.isoformat() if provider.last_check else None,
            }

        return status

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Выполнить операцию через активного провайдера"""
        pass
