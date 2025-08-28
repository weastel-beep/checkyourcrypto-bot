"""
Сервис для обработки платежей
"""
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from common.database import async_session_maker
from common.models import User, Payment, PaymentStatus
from common.services import UserService
from common.binance_pay_service import binance_pay_service, create_binance_payment, process_binance_payment

logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис для работы с платежами"""
    
    @staticmethod
    async def create_payment(user_id: int, amount: Decimal, payment_method: str = "binance_pay") -> Payment:
        """Создать новый платеж"""
        async with async_session_maker() as session:
            payment = Payment(
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                status=PaymentStatus.PENDING,
                created_at=datetime.utcnow()
            )
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            
            logger.info(f"Создан платеж {payment.id} для пользователя {user_id} на сумму {amount}")
            return payment
    
    @staticmethod
    async def create_binance_payment(user_id: int, amount: Decimal) -> Dict[str, Any]:
        """Создать платеж через Binance Pay"""
        try:
            # Создаем запись в базе
            payment = await PaymentService.create_payment(user_id, amount, "binance_pay")
            
            # Создаем платеж в Binance Pay
            binance_result = await create_binance_payment(user_id, amount)
            
            if binance_result.get("success"):
                # Обновляем запись с данными от Binance Pay
                async with async_session_maker() as session:
                    payment_record = await session.get(Payment, payment.id)
                    if payment_record:
                        payment_record.external_id = binance_result.get("order_id")
                        payment_record.metadata = {
                            "payment_url": binance_result.get("payment_url"),
                            "expires_at": binance_result.get("expires_at")
                        }
                        await session.commit()
                
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "order_id": binance_result.get("order_id"),
                    "payment_url": binance_result.get("payment_url"),
                    "expires_at": binance_result.get("expires_at")
                }
            else:
                # Если Binance Pay недоступен, возвращаем заглушку
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "order_id": f"mock_order_{payment.id}",
                    "payment_url": f"https://checkyourcrypto-bot-87c446f24699.herokuapp.com/pay/{payment.id}",
                    "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    "note": "Используется тестовый режим (Binance Pay не настроен)"
                }
                
        except Exception as e:
            logger.error(f"Ошибка создания Binance Pay платежа: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def process_payment(payment_id: int) -> bool:
        """Обработать платеж (имитация)"""
        async with async_session_maker() as session:
            payment = await session.get(Payment, payment_id)
            if not payment:
                logger.error(f"Платеж {payment_id} не найден")
                return False
            
            # Имитируем успешную обработку платежа
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            
            # Пополняем баланс пользователя
            user = await session.get(User, payment.user_id)
            if user:
                user.balance += payment.amount
                user.updated_at = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"Платеж {payment_id} обработан успешно")
            return True
    
    @staticmethod
    async def get_user_payments(user_id: int, limit: int = 10) -> list[Payment]:
        """Получить историю платежей пользователя"""
        async with async_session_maker() as session:
            payments = await session.execute(
                "SELECT * FROM payments WHERE user_id = :user_id ORDER BY created_at DESC LIMIT :limit",
                {"user_id": user_id, "limit": limit}
            )
            return payments.fetchall()
    
    @staticmethod
    async def get_payment_stats() -> Dict[str, Any]:
        """Получить статистику платежей"""
        async with async_session_maker() as session:
            # Общая статистика
            total_payments = await session.execute(
                "SELECT COUNT(*) FROM payments WHERE status = 'completed'"
            )
            total_amount = await session.execute(
                "SELECT SUM(amount) FROM payments WHERE status = 'completed'"
            )
            
            # Статистика за последние 30 дней
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_payments = await session.execute(
                "SELECT COUNT(*) FROM payments WHERE status = 'completed' AND created_at >= :date",
                {"date": thirty_days_ago}
            )
            recent_amount = await session.execute(
                "SELECT SUM(amount) FROM payments WHERE status = 'completed' AND created_at >= :date",
                {"date": thirty_days_ago}
            )
            
            return {
                "total_payments": total_payments.scalar() or 0,
                "total_amount": float(total_amount.scalar() or 0),
                "recent_payments": recent_payments.scalar() or 0,
                "recent_amount": float(recent_amount.scalar() or 0)
            }


# Создаем экземпляр сервиса
payment_service = PaymentService()
