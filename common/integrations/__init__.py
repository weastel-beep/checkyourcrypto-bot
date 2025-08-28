"""
Модуль интеграций - новая архитектура для управления провайдерами
"""

from .base import BaseIntegration, BaseProvider
from .cache_service import CacheService
from .providers import (
    MetaSleuthProvider,
    Provider2,
    Provider3,
    AIAnalysisProvider,
    DeepScanProvider,
    BinancePayProvider,
    StripeProvider,
    CryptoProvider,
)
from .free_check_service import FreeCheckService
from .paid_check_service import PaidCheckService
from .payment_service import PaymentService

__all__ = [
    "BaseIntegration",
    "BaseProvider",
    "CacheService",
    "MetaSleuthProvider",
    "Provider2",
    "Provider3",
    "AIAnalysisProvider",
    "DeepScanProvider",
    "BinancePayProvider",
    "StripeProvider",
    "CryptoProvider",
    "FreeCheckService",
    "PaidCheckService",
    "PaymentService",
]
