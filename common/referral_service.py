"""
Сервис для реферальной программы
"""
import logging
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from common.database import async_session_maker
from common.models import User, ReferralCode, ReferralReward
from common.services import UserService

logger = logging.getLogger(__name__)


class ReferralService:
    """Сервис для работы с реферальной программой"""

    @staticmethod
    async def generate_referral_code(user_id: int) -> str:
        """Генерировать реферальный код для пользователя"""
        # Генерируем уникальный код
        code = secrets.token_urlsafe(8).upper()[:8]

        async with async_session_maker() as session:
            # Проверяем уникальность
            existing = await session.execute("SELECT id FROM referral_codes WHERE code = :code", {"code": code})

            if existing.fetchone():
                # Если код уже существует, генерируем новый
                return await ReferralService.generate_referral_code(user_id)

            # Создаем реферальный код
            referral_code = ReferralCode(user_id=user_id, code=code, created_at=datetime.utcnow(), is_active=True)
            session.add(referral_code)
            await session.commit()

            logger.info(f"Создан реферальный код {code} для пользователя {user_id}")
            return code

    @staticmethod
    async def get_user_referral_code(user_id: int) -> Optional[str]:
        """Получить реферальный код пользователя"""
        async with async_session_maker() as session:
            code = await session.execute(
                "SELECT code FROM referral_codes WHERE user_id = :user_id AND is_active = true", {"user_id": user_id}
            )
            result = code.fetchone()
            return result[0] if result else None

    @staticmethod
    async def get_user_by_referral_code(code: str) -> Optional[int]:
        """Получить пользователя по реферальному коду"""
        async with async_session_maker() as session:
            user = await session.execute(
                "SELECT user_id FROM referral_codes WHERE code = :code AND is_active = true", {"code": code}
            )
            result = user.fetchone()
            return result[0] if result else None

    @staticmethod
    async def process_referral(referrer_id: int, referred_id: int) -> bool:
        """Обработать реферальную регистрацию"""
        async with async_session_maker() as session:
            # Проверяем, что пользователь еще не был рефералом
            existing = await session.execute(
                "SELECT id FROM users WHERE tg_id = :referred_id AND referred_by IS NOT NULL", {"referred_id": referred_id}
            )

            if existing.fetchone():
                logger.warning(f"Пользователь {referred_id} уже был рефералом")
                return False

            # Обновляем пользователя
            await session.execute(
                "UPDATE users SET referred_by = :referrer_id WHERE tg_id = :referred_id",
                {"referrer_id": referrer_id, "referred_id": referred_id},
            )

            # Создаем запись о награде
            reward = ReferralReward(
                referrer_id=referrer_id,
                referred_id=referred_id,
                reward_type="registration",
                amount=Decimal("1.00"),  # $1 за регистрацию
                status="pending",
                created_at=datetime.utcnow(),
            )
            session.add(reward)
            await session.commit()

            logger.info(f"Обработана реферальная регистрация: {referrer_id} -> {referred_id}")
            return True

    @staticmethod
    async def process_payment_reward(referred_id: int, payment_amount: Decimal) -> bool:
        """Обработать награду за платеж реферала"""
        async with async_session_maker() as session:
            # Получаем реферера
            referrer = await session.execute(
                "SELECT referred_by FROM users WHERE tg_id = :referred_id", {"referred_id": referred_id}
            )
            result = referrer.fetchone()

            if not result or not result[0]:
                return False

            referrer_id = result[0]

            # Рассчитываем награду (10% от платежа)
            reward_amount = payment_amount * Decimal("0.10")

            # Создаем запись о награде
            reward = ReferralReward(
                referrer_id=referrer_id,
                referred_id=referred_id,
                reward_type="payment",
                amount=reward_amount,
                status="pending",
                created_at=datetime.utcnow(),
            )
            session.add(reward)
            await session.commit()

            logger.info(f"Создана награда за платеж: {referrer_id} получит ${reward_amount}")
            return True

    @staticmethod
    async def get_user_referrals(user_id: int) -> List[Dict[str, Any]]:
        """Получить список рефералов пользователя"""
        async with async_session_maker() as session:
            referrals = await session.execute(
                """
                SELECT 
                    u.tg_id,
                    u.username,
                    u.created_at,
                    u.last_activity,
                    COUNT(ch.id) as checks_count,
                    SUM(CASE WHEN ch.check_type = 'paid' THEN 1 ELSE 0 END) as paid_checks
                FROM users u
                LEFT JOIN check_history ch ON u.tg_id = ch.user_id
                WHERE u.referred_by = :user_id
                GROUP BY u.tg_id, u.username, u.created_at, u.last_activity
                ORDER BY u.created_at DESC
            """,
                {"user_id": user_id},
            )

            return [
                {
                    "user_id": row[0],
                    "username": row[1],
                    "created_at": row[2],
                    "last_activity": row[3],
                    "checks_count": row[4] or 0,
                    "paid_checks": row[5] or 0,
                }
                for row in referrals.fetchall()
            ]

    @staticmethod
    async def get_user_rewards(user_id: int) -> List[Dict[str, Any]]:
        """Получить награды пользователя"""
        async with async_session_maker() as session:
            rewards = await session.execute(
                """
                SELECT 
                    rr.id,
                    rr.reward_type,
                    rr.amount,
                    rr.status,
                    rr.created_at,
                    u.username as referred_username
                FROM referral_rewards rr
                LEFT JOIN users u ON rr.referred_id = u.tg_id
                WHERE rr.referrer_id = :user_id
                ORDER BY rr.created_at DESC
            """,
                {"user_id": user_id},
            )

            return [
                {
                    "id": row[0],
                    "type": row[1],
                    "amount": float(row[2]),
                    "status": row[3],
                    "created_at": row[4],
                    "referred_username": row[5],
                }
                for row in rewards.fetchall()
            ]

    @staticmethod
    async def get_referral_stats(user_id: int) -> Dict[str, Any]:
        """Получить статистику реферальной программы"""
        async with async_session_maker() as session:
            # Общее количество рефералов
            total_referrals = await session.execute(
                "SELECT COUNT(*) FROM users WHERE referred_by = :user_id", {"user_id": user_id}
            )

            # Активные рефералы (за последние 30 дней)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_referrals = await session.execute(
                "SELECT COUNT(*) FROM users WHERE referred_by = :user_id AND last_activity >= :date",
                {"user_id": user_id, "date": thirty_days_ago},
            )

            # Общая сумма наград
            total_rewards = await session.execute(
                "SELECT SUM(amount) FROM referral_rewards WHERE referrer_id = :user_id AND status = 'completed'",
                {"user_id": user_id},
            )

            # Ожидающие награды
            pending_rewards = await session.execute(
                "SELECT SUM(amount) FROM referral_rewards WHERE referrer_id = :user_id AND status = 'pending'",
                {"user_id": user_id},
            )

            return {
                "total_referrals": total_referrals.scalar() or 0,
                "active_referrals": active_referrals.scalar() or 0,
                "total_rewards": float(total_rewards.scalar() or 0),
                "pending_rewards": float(pending_rewards.scalar() or 0),
            }

    @staticmethod
    async def payout_rewards(user_id: int) -> bool:
        """Выплатить награды пользователю"""
        async with async_session_maker() as session:
            # Получаем все ожидающие награды
            pending_rewards = await session.execute(
                "SELECT SUM(amount) FROM referral_rewards WHERE referrer_id = :user_id AND status = 'pending'",
                {"user_id": user_id},
            )

            total_amount = pending_rewards.scalar() or 0

            if total_amount <= 0:
                return False

            # Обновляем статус наград
            await session.execute(
                "UPDATE referral_rewards SET status = 'completed', completed_at = :now WHERE referrer_id = :user_id AND status = 'pending'",
                {"user_id": user_id, "now": datetime.utcnow()},
            )

            # Пополняем баланс пользователя
            user = await session.get(User, user_id)
            if user:
                user.balance += total_amount
                user.updated_at = datetime.utcnow()

            await session.commit()

            logger.info(f"Выплачены реферальные награды пользователю {user_id}: ${total_amount}")
            return True


# Создаем экземпляр сервиса
referral_service = ReferralService()
