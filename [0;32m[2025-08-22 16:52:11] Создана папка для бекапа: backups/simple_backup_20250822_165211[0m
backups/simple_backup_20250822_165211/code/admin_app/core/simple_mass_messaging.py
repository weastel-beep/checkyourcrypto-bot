"""
Упрощенный сервис массовых сообщений на Django ORM
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from aiogram import Bot
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.db import models

from .admin_models import MassMessage
from .models import User

logger = logging.getLogger(__name__)


class SimpleMassMessagingService:
    """Упрощенный сервис для массовой рассылки на Django ORM"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    def create_mass_message(
        self,
        title: str,
        content: str,
        language: str = "ru",
        min_balance: Optional[Decimal] = None,
        max_balance: Optional[Decimal] = None,
        user_language: Optional[str] = None,
        is_active_only: bool = True,
        scheduled_at: Optional[datetime] = None,
        created_by_id: int = 1  # По умолчанию используем первого админа
    ) -> MassMessage:
        """Создать новое массовое сообщение"""
        try:
            with transaction.atomic():
                # Получаем объект AdminUser
                from .admin_models import AdminUser
                try:
                    admin_user = AdminUser.objects.get(id=created_by_id)
                except AdminUser.DoesNotExist:
                    admin_user = AdminUser.objects.first()  # Используем первого админа
                
                mass_message = MassMessage.objects.create(
                    title=title,
                    content=content,
                    language=language,
                    min_balance=min_balance,
                    max_balance=max_balance,
                    user_language=user_language or "ru",
                    is_active_only=is_active_only,
                    scheduled_at=scheduled_at,
                    status='DRAFT' if not scheduled_at else 'SCHEDULED',
                    created_by=admin_user
                )
                
                logger.info(f"Создано массовое сообщение ID: {mass_message.id}")
                return mass_message
        except Exception as e:
            logger.error(f"Ошибка создания массового сообщения: {e}")
            raise
    
    def get_users_for_mass_message(self, mass_message: MassMessage) -> List[User]:
        """Получить список пользователей для массового сообщения"""
        try:
            # Базовый queryset
            users = User.objects.filter(is_blocked=False)
            
            # Фильтр по языку
            if mass_message.user_language:
                users = users.filter(language=mass_message.user_language)
            
            # Фильтр по балансу
            if mass_message.min_balance is not None:
                users = users.filter(balance__gte=mass_message.min_balance)
            if mass_message.max_balance is not None:
                users = users.filter(balance__lte=mass_message.max_balance)
            
            # Фильтр по активности
            if mass_message.is_active_only:
                active_date = timezone.now() - timedelta(days=30)
                users = users.filter(
                    models.Q(updated_at__gte=active_date) |
                    models.Q(last_free_check__gte=active_date)
                )
            
            user_list = list(users)
            logger.info(f"Найдено {len(user_list)} пользователей для массового сообщения {mass_message.id}")
            return user_list
            
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []
    
    def prepare_mass_message(self, mass_message_id: int) -> Dict[str, int]:
        """Подготовить массовое сообщение (подсчитать получателей)"""
        try:
            mass_message = MassMessage.objects.get(id=mass_message_id)
            
            if mass_message.status not in ['DRAFT', 'SCHEDULED']:
                raise ValueError(f"Сообщение {mass_message_id} не готово к подготовке")
            
            # Получаем пользователей
            users = self.get_users_for_mass_message(mass_message)
            
            # Обновляем статистику
            mass_message.total_users = len(users)
            mass_message.status = 'SCHEDULED'
            mass_message.save()
            
            logger.info(f"Подготовлено массовое сообщение {mass_message_id}: {len(users)} получателей")
            
            return {
                "total_users": len(users),
                "status": "prepared"
            }
            
        except Exception as e:
            logger.error(f"Ошибка подготовки массового сообщения {mass_message_id}: {e}")
            raise
    
    async def send_mass_message(self, mass_message_id: int, batch_size: int = 50) -> Dict[str, int]:
        """Отправить массовое сообщение"""
        try:
            # Используем sync_to_async для работы с Django ORM
            from asgiref.sync import sync_to_async
            
            # Получаем сообщение асинхронно
            mass_message = await sync_to_async(MassMessage.objects.get)(id=mass_message_id)
            
            if mass_message.status not in ['SCHEDULED', 'SENDING']:
                raise ValueError(f"Сообщение {mass_message_id} не готово к отправке")
            
            # Обновляем статус асинхронно
            mass_message.status = 'SENDING'
            await sync_to_async(mass_message.save)()
            
            # Получаем пользователей асинхронно
            users = await sync_to_async(self.get_users_for_mass_message)(mass_message)
            total_recipients = len(users)
            
            if total_recipients == 0:
                logger.warning(f"Нет получателей для массового сообщения {mass_message_id}")
                mass_message = await sync_to_async(MassMessage.objects.get)(id=mass_message_id)
                mass_message.status = 'COMPLETED'
                mass_message.sent_at = timezone.now()
                await sync_to_async(mass_message.save)()
                return {"success": 0, "failed": 0}
            
            success_count = 0
            failed_count = 0
            
            logger.info(f"Начинаем отправку массового сообщения {mass_message_id} для {total_recipients} получателей")
            
            # Отправляем сообщения батчами
            for i in range(0, total_recipients, batch_size):
                batch = users[i:i + batch_size]
                
                # Создаем задачи для отправки
                tasks = []
                for user in batch:
                    task = self._send_to_user(mass_message, user)
                    tasks.append(task)
                
                # Выполняем задачи параллельно
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Обрабатываем результаты
                for user, result in zip(batch, results):
                    if isinstance(result, Exception):
                        failed_count += 1
                        logger.error(f"Ошибка отправки пользователю {user.id}: {result}")
                    else:
                        success_count += 1
                
                # Небольшая задержка между батчами
                await asyncio.sleep(1)
            
            # Обновляем статистику асинхронно
            mass_message = await sync_to_async(MassMessage.objects.get)(id=mass_message_id)
            mass_message.sent_count = success_count
            mass_message.failed_count = failed_count
            mass_message.sent_at = timezone.now()
            mass_message.status = 'COMPLETED'
            await sync_to_async(mass_message.save)()
            
            logger.info(f"Массовое сообщение {mass_message_id} завершено: {success_count} успешно, {failed_count} ошибок")
            
            return {
                "success": success_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Ошибка отправки массового сообщения {mass_message_id}: {e}")
            
            # Обновляем статус на FAILED
            try:
                mass_message = await sync_to_async(MassMessage.objects.get)(id=mass_message_id)
                mass_message.status = 'FAILED'
                await sync_to_async(mass_message.save)()
            except:
                pass
            
            raise
    
    async def _send_to_user(self, mass_message: MassMessage, user: User) -> bool:
        """Отправить сообщение конкретному пользователю"""
        try:
            # Отправляем сообщение через Telegram API
            await self.bot.send_message(
                chat_id=user.user_id,
                text=mass_message.content,
                parse_mode='HTML'
            )
            
            logger.debug(f"Сообщение отправлено пользователю {user.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {user.user_id}: {e}")
            return False
    
    def get_scheduled_messages(self) -> List[MassMessage]:
        """Получить запланированные сообщения"""
        try:
            now = timezone.now()
            return list(MassMessage.objects.filter(
                status='SCHEDULED',
                scheduled_at__lte=now
            ))
        except Exception as e:
            logger.error(f"Ошибка получения запланированных сообщений: {e}")
            return []
    
    def process_scheduled_messages(self) -> Dict[str, int]:
        """Обработать запланированные сообщения (синхронная версия)"""
        scheduled_messages = self.get_scheduled_messages()
        
        total_processed = 0
        total_success = 0
        total_failed = 0
        
        for message in scheduled_messages:
            try:
                # Подготавливаем сообщение если еще не подготовлено
                if message.total_users == 0:
                    self.prepare_mass_message(message.id)
                
                # Отправляем сообщение
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.send_mass_message(message.id))
                    total_processed += 1
                    total_success += result["success"]
                    total_failed += result["failed"]
                finally:
                    loop.close()
                
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
    """Инициализировать сервис массовых сообщений"""
    global mass_messaging_service
    mass_messaging_service = SimpleMassMessagingService(bot)
    return mass_messaging_service


def get_mass_messaging_service() -> SimpleMassMessagingService:
    """Получить экземпляр сервиса массовых сообщений"""
    if mass_messaging_service is None:
        raise RuntimeError("Сервис массовых сообщений не инициализирован")
    return mass_messaging_service
