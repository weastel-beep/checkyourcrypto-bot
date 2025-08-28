"""
Система ограничений бесплатных проверок
Гибридная модель: новые пользователи + баланс-зависимые лимиты
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple, Optional
import logging
from common.config import settings

logger = logging.getLogger(__name__)

class CheckLimits:
    def __init__(self):
        # Простое ограничение: 1 проверка в минуту
        self.MIN_INTERVAL_SECONDS = 60  # 1 минута
        
    def can_perform_free_check(self, user) -> Tuple[bool, Optional[int]]:
        """Проверить, может ли пользователь выполнить бесплатную проверку"""
        if not user.last_free_check:
            return True, None
        
        time_since_last = (datetime.now() - user.last_free_check).total_seconds()
        wait_time = self.MIN_INTERVAL_SECONDS - time_since_last
        
        if wait_time <= 0:
            return True, None
        else:
            return False, int(wait_time)
    
    def get_next_free_check_time(self, user) -> Optional[datetime]:
        """Получить время следующей доступной бесплатной проверки"""
        if not user.last_free_check:
            return None
        
        return user.last_free_check + timedelta(seconds=self.MIN_INTERVAL_SECONDS)
    
    def format_wait_time(self, wait_seconds: int) -> str:
        """Форматировать время ожидания в читаемый вид"""
        if wait_seconds < 60:
            return f"{wait_seconds} сек"
        else:
            minutes = wait_seconds // 60
            seconds = wait_seconds % 60
            if seconds == 0:
                return f"{minutes} мин"
            else:
                return f"{minutes} мин {seconds} сек"
    
    def get_user_status_info(self, user) -> dict:
        """Получить информацию о статусе пользователя (упрощенная версия)"""
        return {
            "status": "user",
            "status_text": "Пользователь",
            "next_check_time": self.get_next_free_check_time(user)
        }
    
    async def has_sufficient_balance(self, user, required_amount: Decimal, session) -> bool:
        """Проверить, достаточно ли баланса у пользователя"""
        return user.balance >= required_amount
    
    async def update_last_check_time(self, user, session):
        """Обновить время последней проверки пользователя"""
        user.last_free_check = datetime.now()
        await session.commit()

check_limits = CheckLimits()
