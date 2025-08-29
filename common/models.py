"""
Модели данных для Check Your Crypto
"""

# Импортируем старые модели
from .models_old import (
    User, Check, Payment, Referral, Outbox, BotText, Scenario, Setting,
    CheckType, PaymentStatus, OutboxStatus
)

# Импортируем новые единые модели
from .models.unified import UnifiedBotText, UnifiedScenario, UnifiedSetting

# Экспортируем все модели
__all__ = [
    # Старые модели
    "User", "Check", "Payment", "Referral", "Outbox", "BotText", "Scenario", "Setting",
    "CheckType", "PaymentStatus", "OutboxStatus",
    # Новые единые модели
    "UnifiedBotText",
    "UnifiedScenario", 
    "UnifiedSetting"
]
