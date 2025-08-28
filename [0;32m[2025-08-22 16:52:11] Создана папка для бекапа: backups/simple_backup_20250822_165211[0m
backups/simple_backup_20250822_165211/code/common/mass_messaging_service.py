"""
Сервис для массовой рассылки сообщений пользователям
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from common.database import async_session_maker
from common.models import (
    User, MassMessage, MassMessageRecipient, MassMessageStatus, 
    OutboxStatus, Outbox
)
from common.config import settings

logger = logging.getLogger(__name__)


class MassMessagingService:
    """Сервис для работы с массовой рассылкой"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def create_mass_message(
        self,
        title: str,
        content: str,
        language: str = "ru",
        min_balance: Optional[Decimal] = None,
        max_balance: Optional[Decimal] = None,
        user_language: Optional[str] = None,
        is_active_only: bool = True,
        scheduled_at: Optional[datetime] = None
    ) -> MassMessage:
        """Создать новое массовое сообщение"""
        async with async_session_maker() as session:
            mass_message = MassMessage(
                title=title,
                content=content,
                language=language,
                min_balance=min_balance,
                max_balance=max_balance,
                user_language=user_language or "ru",
                is_active_only=is_active_only,
                scheduled_at=scheduled_at,
                status=MassMessageStatus.SCHEDULED if scheduled_at else MassMessageStatus.DRAFT
            )
            
            session.add(mass_message)
            await session.commit()
            await session.refresh(mass_message)
            
            logger.info(f"Создано массовое сообщение ID: {mass_message.id}")
            return mass_message
    
    async def get_users_for_mass_message(self, mass_message: MassMessage) -> List[User]:
        """Получить список пользователей для массового сообщения"""
        async with async_session_maker() as session:
            query = select(User)
            
            # Базовые фильтры
            filters = []
            
            # Фильтр по языку
            if mass_message.user_language:
                filters.append(User.language == mass_message.user_language)
            
            # Фильтр по балансу
            if mass_message.min_balance is not None:
                filters.append(User.balance >= mass_message.min_balance)
            if mass_message.max_balance is not None:
                filters.append(User.balance <= mass_message.max_balance)
            
            # Фильтр по активности
            if mass_message.is_active_only:
                # Пользователи, которые были активны за последние 30 дней
                active_date = datetime.utcnow() - timedelta(days=30)
                filters.append(
                    or_(
                        User.updated_at >= active_date,
                        User.last_free_check >= active_date
                    )
                )
            
            # Фильтр заблокированных пользователей
            filters.append(User.is_blocked == False)
            
            if filters:
                query = query.where(and_(*filters))
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            logger.info(f"Найдено {len(users)} пользователей для массового сообщения {mass_message.id}")
            return users
    
    async def prepare_mass_message(self, mass_message_id: int) -> bool:
        """Подготовить массовое сообщение (создать получателей)"""
        async with async_session_maker() as session:
            # Получаем массовое сообщение
            mass_message = await session.get(MassMessage, mass_message_id)
            if not mass_message:
                logger.error(f"Массовое сообщение {mass_message_id} не найдено")
                return False
            
            if mass_message.status not in [MassMessageStatus.DRAFT, MassMessageStatus.SCHEDULED]:
                logger.error(f"Массовое сообщение {mass_message_id} не может быть подготовлено")
                return False
            
            # Получаем пользователей
            users = await self.get_users_for_mass_message(mass_message)
            
            # Создаем записи получателей
            recipients = []
            for user in users:
                recipient = MassMessageRecipient(
                    mass_message_id=mass_message_id,
                    user_id=user.tg_id,
                    status=OutboxStatus.PENDING
                )
                recipients.append(recipient)
            
            # Обновляем статистику
            mass_message.total_users = len(users)
            mass_message.status = MassMessageStatus.SCHEDULED
            
            session.add_all(recipients)
            await session.commit()
            
            logger.info(f"Подготовлено массовое сообщение {mass_message_id} для {len(users)} пользователей")
            return True
    
    async def send_mass_message(self, mass_message_id: int, batch_size: int = 50) -> Dict[str, int]:
        """Отправить массовое сообщение"""
        async with async_session_maker() as session:
            # Получаем массовое сообщение
            mass_message = await session.get(MassMessage, mass_message_id)
            if not mass_message:
                logger.error(f"Массовое сообщение {mass_message_id} не найдено")
                return {"success": 0, "failed": 0, "total": 0}
            
            if mass_message.status != MassMessageStatus.SCHEDULED:
                logger.error(f"Массовое сообщение {mass_message_id} не готово к отправке")
                return {"success": 0, "failed": 0, "total": 0}
            
            # Обновляем статус
            mass_message.status = MassMessageStatus.SENDING
            await session.commit()
            
            # Получаем получателей
            query = select(MassMessageRecipient).where(
                and_(
                    MassMessageRecipient.mass_message_id == mass_message_id,
                    MassMessageRecipient.status == OutboxStatus.PENDING
                )
            )
            result = await session.execute(query)
            recipients = result.scalars().all()
            
            total_recipients = len(recipients)
            success_count = 0
            failed_count = 0
            
            logger.info(f"Начинаем отправку массового сообщения {mass_message_id} для {total_recipients} получателей")
            
            # Отправляем сообщения батчами
            for i in range(0, total_recipients, batch_size):
                batch = recipients[i:i + batch_size]
                
                # Создаем задачи для отправки
                tasks = []
                for recipient in batch:
                    task = self._send_to_recipient(mass_message, recipient)
                    tasks.append(task)
                
                # Выполняем задачи параллельно
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Обрабатываем результаты
                for recipient, result in zip(batch, results):
                    if isinstance(result, Exception):
                        recipient.status = OutboxStatus.FAILED
                        recipient.error_message = str(result)
                        failed_count += 1
                        logger.error(f"Ошибка отправки пользователю {recipient.user_id}: {result}")
                    else:
                        recipient.status = OutboxStatus.SENT
                        recipient.sent_at = datetime.utcnow()
                        success_count += 1
                
                # Сохраняем результаты батча
                await session.commit()
                
                # Небольшая задержка между батчами
                await asyncio.sleep(1)
            
            # Обновляем статистику
            mass_message.sent_count = success_count
            mass_message.failed_count = failed_count
            mass_message.sent_at = datetime.utcnow()
            mass_message.status = MassMessageStatus.COMPLETED
            
            await session.commit()
            
            logger.info(f"Массовое сообщение {mass_message_id} завершено: успешно {success_count}, неудачно {failed_count}")
            
            return {
                "success": success_count,
                "failed": failed_count,
                "total": total_recipients
            }
    
    async def _send_to_recipient(self, mass_message: MassMessage, recipient: MassMessageRecipient) -> bool:
        """Отправить сообщение конкретному получателю"""
        try:
            # Формируем текст сообщения
            message_text = f"📢 **{mass_message.title}**\n\n{mass_message.content}"
            
            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=recipient.user_id,
                text=message_text,
                parse_mode="Markdown"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {recipient.user_id}: {e}")
            raise e
    
    async def schedule_mass_message(
        self,
        mass_message_id: int,
        scheduled_at: datetime
    ) -> bool:
        """Запланировать массовое сообщение"""
        async with async_session_maker() as session:
            mass_message = await session.get(MassMessage, mass_message_id)
            if not mass_message:
                return False
            
            mass_message.scheduled_at = scheduled_at
            mass_message.status = MassMessageStatus.SCHEDULED
            await session.commit()
            
            logger.info(f"Массовое сообщение {mass_message_id} запланировано на {scheduled_at}")
            return True
    
    async def cancel_mass_message(self, mass_message_id: int) -> bool:
        """Отменить массовое сообщение"""
        async with async_session_maker() as session:
            mass_message = await session.get(MassMessage, mass_message_id)
            if not mass_message:
                return False
            
            if mass_message.status in [MassMessageStatus.SENDING, MassMessageStatus.COMPLETED]:
                logger.warning(f"Нельзя отменить массовое сообщение {mass_message_id} в статусе {mass_message.status}")
                return False
            
            mass_message.status = MassMessageStatus.CANCELLED
            await session.commit()
            
            logger.info(f"Массовое сообщение {mass_message_id} отменено")
            return True
    
    async def get_mass_message_stats(self, mass_message_id: int) -> Dict[str, Any]:
        """Получить статистику массового сообщения"""
        async with async_session_maker() as session:
            mass_message = await session.get(MassMessage, mass_message_id)
            if not mass_message:
                return {}
            
            # Получаем статистику по получателям
            query = select(
                MassMessageRecipient.status,
                func.count(MassMessageRecipient.id)
            ).where(
                MassMessageRecipient.mass_message_id == mass_message_id
            ).group_by(MassMessageRecipient.status)
            
            result = await session.execute(query)
            status_stats = dict(result.fetchall())
            
            return {
                "id": mass_message.id,
                "title": mass_message.title,
                "status": mass_message.status.value,
                "total_users": mass_message.total_users,
                "sent_count": mass_message.sent_count,
                "failed_count": mass_message.failed_count,
                "scheduled_at": mass_message.scheduled_at,
                "sent_at": mass_message.sent_at,
                "created_at": mass_message.created_at,
                "status_breakdown": status_stats
            }
    
    async def get_scheduled_messages(self) -> List[MassMessage]:
        """Получить запланированные сообщения"""
        async with async_session_maker() as session:
            query = select(MassMessage).where(
                and_(
                    MassMessage.status == MassMessageStatus.SCHEDULED,
                    MassMessage.scheduled_at <= datetime.utcnow()
                )
            )
            result = await session.execute(query)
            return result.scalars().all()
    
    async def process_scheduled_messages(self) -> Dict[str, int]:
        """Обработать запланированные сообщения"""
        scheduled_messages = await self.get_scheduled_messages()
        
        total_processed = 0
        total_success = 0
        total_failed = 0
        
        for message in scheduled_messages:
            try:
                # Подготавливаем сообщение если еще не подготовлено
                if message.total_users == 0:
                    await self.prepare_mass_message(message.id)
                
                # Отправляем сообщение
                result = await self.send_mass_message(message.id)
                
                total_processed += 1
                total_success += result["success"]
                total_failed += result["failed"]
                
            except Exception as e:
                logger.error(f"Ошибка обработки запланированного сообщения {message.id}: {e}")
                total_failed += 1
        
        logger.info(f"Обработано запланированных сообщений: {total_processed}, успешно: {total_success}, неудачно: {total_failed}")
        
        return {
            "processed": total_processed,
            "success": total_success,
            "failed": total_failed
        }


# Создаем экземпляр сервиса (будет инициализирован с ботом)
mass_messaging_service = None


def init_mass_messaging_service(bot: Bot):
    """Инициализировать сервис массовой рассылки"""
    global mass_messaging_service
    mass_messaging_service = MassMessagingService(bot)
    logger.info("Сервис массовой рассылки инициализирован")
