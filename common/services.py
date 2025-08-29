"""
Сервисы для Check Your Crypto
"""

# Импортируем все старые сервисы
from .services_legacy import (
    TextService, UserService, SettingService, CheckService, PaymentService,
    ReferralService, NotificationService, AnalyticsService
)

# Импортируем новые единые сервисы
from .services.unified import UnifiedTextService, UnifiedScenarioService, UnifiedSettingService

# Экспортируем все сервисы
__all__ = [
    # Старые сервисы
    "TextService", "UserService", "SettingService", "CheckService", "PaymentService",
    "ReferralService", "NotificationService", "AnalyticsService",
    # Новые единые сервисы
    "UnifiedTextService", "UnifiedScenarioService", "UnifiedSettingService"
]
