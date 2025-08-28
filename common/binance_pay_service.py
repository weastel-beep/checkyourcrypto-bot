"""
Заглушка для интеграции с Binance Pay
Будет реализована после получения API ключей
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BinancePayService:
    """Заглушка для Binance Pay интеграции"""

    def __init__(self):
        self.api_key = None
        self.secret_key = None
        self.is_configured = False
        logger.info("Binance Pay Service: Заглушка инициализирована")

    def configure(self, api_key: str, secret_key: str) -> bool:
        """Настроить API ключи"""
        self.api_key = api_key
        self.secret_key = secret_key
        self.is_configured = bool(api_key and secret_key)

        if self.is_configured:
            logger.info("Binance Pay Service: API ключи настроены")
        else:
            logger.warning("Binance Pay Service: API ключи не настроены")

        return self.is_configured

    async def create_payment_order(
        self, amount: Decimal, currency: str = "USDT", description: str = "Check Your Crypto - AI Analysis"
    ) -> Dict[str, Any]:
        """Создать платежный ордер (заглушка)"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "Binance Pay не настроен. Ожидаем API ключи.",
                "order_id": None,
                "payment_url": None,
            }

        # Заглушка - возвращаем тестовые данные
        order_id = f"test_order_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "order_id": order_id,
            "payment_url": f"https://test.binancepay.com/pay/{order_id}",
            "amount": float(amount),
            "currency": currency,
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }

    async def check_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Проверить статус платежа (заглушка)"""
        if not self.is_configured:
            return {"success": False, "error": "Binance Pay не настроен", "status": "unknown"}

        # Заглушка - имитируем успешный платеж
        return {
            "success": True,
            "status": "PAID",
            "order_id": order_id,
            "paid_amount": 1.00,
            "paid_currency": "USDT",
            "paid_at": datetime.utcnow().isoformat(),
        }

    async def get_payment_history(self, limit: int = 50) -> Dict[str, Any]:
        """Получить историю платежей (заглушка)"""
        if not self.is_configured:
            return {"success": False, "error": "Binance Pay не настроен", "payments": []}

        # Заглушка - возвращаем тестовые данные
        return {
            "success": True,
            "payments": [
                {
                    "order_id": f"test_order_{i}",
                    "amount": 1.00,
                    "currency": "USDT",
                    "status": "PAID",
                    "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "paid_at": (datetime.utcnow() - timedelta(days=i, hours=1)).isoformat(),
                }
                for i in range(min(limit, 5))
            ],
        }

    async def refund_payment(self, order_id: str, reason: str = "User request") -> Dict[str, Any]:
        """Возврат платежа (заглушка)"""
        if not self.is_configured:
            return {"success": False, "error": "Binance Pay не настроен"}

        return {
            "success": True,
            "refund_id": f"refund_{order_id}",
            "order_id": order_id,
            "status": "PROCESSING",
            "reason": reason,
        }

    def get_status(self) -> Dict[str, Any]:
        """Получить статус сервиса"""
        return {
            "configured": self.is_configured,
            "api_key_set": bool(self.api_key),
            "secret_key_set": bool(self.secret_key),
            "status": "ready" if self.is_configured else "waiting_for_keys",
        }


# Создаем экземпляр сервиса
binance_pay_service = BinancePayService()


# Функции для интеграции с основным платежным сервисом
async def create_binance_payment(user_id: int, amount: Decimal) -> Dict[str, Any]:
    """Создать платеж через Binance Pay"""
    return await binance_pay_service.create_payment_order(
        amount=amount, description=f"Check Your Crypto - AI Analysis for user {user_id}"
    )


async def process_binance_payment(order_id: str) -> Dict[str, Any]:
    """Обработать платеж через Binance Pay"""
    return await binance_pay_service.check_payment_status(order_id)
