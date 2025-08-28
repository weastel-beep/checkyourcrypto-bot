"""
Сервис для отправки уведомлений пользователям
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.database import async_session_maker
from common.models import User, Notification, NotificationType
from common.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для работы с уведомлениями"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def send_notification(
        self, 
        user_id: int, 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO,
        keyboard: Optional[InlineKeyboardMarkup] = None
    ) -> bool:
        """Отправить уведомление пользователю"""
        try:
            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Сохраняем уведомление в базу
            async with async_session_maker() as session:
                notification = Notification(
                    user_id=user_id,
                    message=message,
                    notification_type=notification_type,
                    sent_at=datetime.utcnow()
                )
                session.add(notification)
                await session.commit()
            
            logger.info(f"Уведомление отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
            return False
    
    async def send_bulk_notification(
        self, 
        user_ids: List[int], 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO
    ) -> Dict[str, int]:
        """Отправить массовое уведомление"""
        results = {"success": 0, "failed": 0}
        
        for user_id in user_ids:
            success = await self.send_notification(user_id, message, notification_type)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Массовое уведомление: успешно {results['success']}, неудачно {results['failed']}")
        return results
    
    async def send_payment_success(self, user_id: int, amount: float) -> bool:
        """Уведомление об успешном платеже"""
        message = f"""💰 **Платеж успешно обработан!**

✅ Сумма: ${amount}
💳 Баланс пополнен

Спасибо за доверие! 🚀"""
        
        return await self.send_notification(user_id, message, NotificationType.SUCCESS)
    
    async def send_low_balance_warning(self, user_id: int, balance: float) -> bool:
        """Предупреждение о низком балансе"""
        message = f"""⚠️ **Низкий баланс**

💰 Текущий баланс: ${balance}
💳 Пополните баланс для продолжения работы

Используйте кнопку "Пополнить" в главном меню."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Пополнить", callback_data="topup")]
        ])
        
        return await self.send_notification(user_id, message, NotificationType.WARNING, keyboard)
    
    async def send_new_feature_announcement(self, feature_name: str, description: str) -> Dict[str, int]:
        """Анонс новой функции всем пользователям"""
        async with async_session_maker() as session:
            # Получаем всех активных пользователей
            users = await session.execute(
                "SELECT tg_id FROM users WHERE is_active = true"
            )
            user_ids = [user[0] for user in users.fetchall()]
        
        message = f"""🎉 **Новая функция: {feature_name}**

{description}

Попробуйте прямо сейчас! 🚀"""
        
        return await self.send_bulk_notification(user_ids, message, NotificationType.ANNOUNCEMENT)
    
    async def get_user_notifications(self, user_id: int, limit: int = 20) -> List[Notification]:
        """Получить историю уведомлений пользователя"""
        async with async_session_maker() as session:
            notifications = await session.execute(
                "SELECT * FROM notifications WHERE user_id = :user_id ORDER BY sent_at DESC LIMIT :limit",
                {"user_id": user_id, "limit": limit}
            )
            return notifications.fetchall()
    
    async def mark_as_read(self, notification_id: int) -> bool:
        """Отметить уведомление как прочитанное"""
        async with async_session_maker() as session:
            notification = await session.get(Notification, notification_id)
            if notification:
                notification.read_at = datetime.utcnow()
                await session.commit()
                return True
            return False


# Создаем экземпляр сервиса (будет инициализирован с ботом)
notification_service = None
