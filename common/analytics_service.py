"""
Сервис для сбора и анализа данных
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from common.database import async_session_maker
from common.models import User, CheckHistory, Payment, Notification

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для аналитики"""

    @staticmethod
    async def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        async with async_session_maker() as session:
            # Общая статистика проверок
            total_checks = await session.execute(
                "SELECT COUNT(*) FROM check_history WHERE user_id = :user_id", {"user_id": user_id}
            )

            paid_checks = await session.execute(
                "SELECT COUNT(*) FROM check_history WHERE user_id = :user_id AND check_type = 'paid'", {"user_id": user_id}
            )

            free_checks = await session.execute(
                "SELECT COUNT(*) FROM check_history WHERE user_id = :user_id AND check_type = 'free'", {"user_id": user_id}
            )

            # Статистика платежей
            total_payments = await session.execute(
                "SELECT COUNT(*) FROM payments WHERE user_id = :user_id AND status = 'completed'", {"user_id": user_id}
            )

            total_spent = await session.execute(
                "SELECT SUM(amount) FROM payments WHERE user_id = :user_id AND status = 'completed'", {"user_id": user_id}
            )

            # Статистика за последние 30 дней
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_checks = await session.execute(
                "SELECT COUNT(*) FROM check_history WHERE user_id = :user_id AND created_at >= :date",
                {"user_id": user_id, "date": thirty_days_ago},
            )

            recent_payments = await session.execute(
                "SELECT COUNT(*) FROM payments WHERE user_id = :user_id AND status = 'completed' AND created_at >= :date",
                {"user_id": user_id, "date": thirty_days_ago},
            )

            return {
                "total_checks": total_checks.scalar() or 0,
                "paid_checks": paid_checks.scalar() or 0,
                "free_checks": free_checks.scalar() or 0,
                "total_payments": total_payments.scalar() or 0,
                "total_spent": float(total_spent.scalar() or 0),
                "recent_checks": recent_checks.scalar() or 0,
                "recent_payments": recent_payments.scalar() or 0,
            }

    @staticmethod
    async def get_global_stats() -> Dict[str, Any]:
        """Получить глобальную статистику"""
        async with async_session_maker() as session:
            # Общая статистика пользователей
            total_users = await session.execute("SELECT COUNT(*) FROM users")
            active_users = await session.execute(
                "SELECT COUNT(*) FROM users WHERE last_activity >= :date", {"date": datetime.utcnow() - timedelta(days=7)}
            )

            # Статистика проверок
            total_checks = await session.execute("SELECT COUNT(*) FROM check_history")
            paid_checks = await session.execute("SELECT COUNT(*) FROM check_history WHERE check_type = 'paid'")

            # Статистика платежей
            total_revenue = await session.execute("SELECT SUM(amount) FROM payments WHERE status = 'completed'")

            # Статистика за последние 30 дней
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_users = await session.execute(
                "SELECT COUNT(*) FROM users WHERE created_at >= :date", {"date": thirty_days_ago}
            )

            recent_checks = await session.execute(
                "SELECT COUNT(*) FROM check_history WHERE created_at >= :date", {"date": thirty_days_ago}
            )

            recent_revenue = await session.execute(
                "SELECT SUM(amount) FROM payments WHERE status = 'completed' AND created_at >= :date",
                {"date": thirty_days_ago},
            )

            return {
                "total_users": total_users.scalar() or 0,
                "active_users": active_users.scalar() or 0,
                "total_checks": total_checks.scalar() or 0,
                "paid_checks": paid_checks.scalar() or 0,
                "total_revenue": float(total_revenue.scalar() or 0),
                "new_users_30d": new_users.scalar() or 0,
                "recent_checks_30d": recent_checks.scalar() or 0,
                "recent_revenue_30d": float(recent_revenue.scalar() or 0),
            }

    @staticmethod
    async def get_popular_chains() -> List[Dict[str, Any]]:
        """Получить популярные блокчейны"""
        async with async_session_maker() as session:
            chains = await session.execute(
                """
                SELECT chain, COUNT(*) as count 
                FROM check_history 
                GROUP BY chain 
                ORDER BY count DESC 
                LIMIT 10
            """
            )

            return [{"chain": row[0], "count": row[1]} for row in chains.fetchall()]

    @staticmethod
    async def get_risk_distribution() -> Dict[str, int]:
        """Получить распределение рисков"""
        async with async_session_maker() as session:
            # Получаем все проверки с рисками
            checks = await session.execute(
                """
                SELECT result_data->>'screening' as screening_data
                FROM check_history 
                WHERE result_data IS NOT NULL
            """
            )

            risk_distribution = {"low": 0, "medium": 0, "high": 0}

            for row in checks.fetchall():
                if row[0]:
                    # Здесь нужно парсить JSON из result_data
                    # Пока что возвращаем заглушку
                    pass

            return risk_distribution

    @staticmethod
    async def get_daily_stats(days: int = 30) -> List[Dict[str, Any]]:
        """Получить ежедневную статистику"""
        async with async_session_maker() as session:
            start_date = datetime.utcnow() - timedelta(days=days)

            daily_stats = await session.execute(
                """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as checks,
                    COUNT(CASE WHEN check_type = 'paid' THEN 1 END) as paid_checks
                FROM check_history 
                WHERE created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date
            """,
                {"start_date": start_date},
            )

            return [{"date": row[0].isoformat(), "checks": row[1], "paid_checks": row[2]} for row in daily_stats.fetchall()]

    @staticmethod
    async def get_user_retention() -> Dict[str, float]:
        """Получить метрики удержания пользователей"""
        async with async_session_maker() as session:
            # Пользователи, которые вернулись через день
            day1_retention = await session.execute(
                """
                SELECT COUNT(DISTINCT u1.tg_id) * 100.0 / COUNT(DISTINCT u2.tg_id) as retention
                FROM users u1
                LEFT JOIN users u2 ON u1.tg_id = u2.tg_id
                WHERE u1.last_activity >= u1.created_at + INTERVAL '1 day'
            """
            )

            # Пользователи, которые вернулись через неделю
            week1_retention = await session.execute(
                """
                SELECT COUNT(DISTINCT u1.tg_id) * 100.0 / COUNT(DISTINCT u2.tg_id) as retention
                FROM users u1
                LEFT JOIN users u2 ON u1.tg_id = u2.tg_id
                WHERE u1.last_activity >= u1.created_at + INTERVAL '7 days'
            """
            )

            return {
                "day1_retention": float(day1_retention.scalar() or 0),
                "week1_retention": float(week1_retention.scalar() or 0),
            }


# Создаем экземпляр сервиса
analytics_service = AnalyticsService()
