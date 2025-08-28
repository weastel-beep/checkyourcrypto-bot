"""
Сервис управления массовой рассылкой
"""
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .admin_models import MassMessage, MassSendSession, MassSendRecipient
from .models import User


class MassSendManager:
    """Менеджер массовой рассылки"""
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.session = None
        self.is_running = False
        self.is_paused = False
        self.is_cancelled = False
        self.current_batch = 0
        self.total_batches = 0
        
    def load_session(self):
        """Загружает сессию из базы данных"""
        try:
            self.session = MassSendSession.objects.get(id=self.session_id)
            return True
        except MassSendSession.DoesNotExist:
            return False
    
    def get_users_by_filter(self, user_filter: str) -> List[User]:
        """Получает пользователей по фильтру"""
        users = User.objects.filter(is_blocked=False)
        
        if user_filter == 'all':
            return list(users)
        elif user_filter == 'active':
            # Активные за последнюю неделю
            week_ago = timezone.now() - timedelta(days=7)
            return list(users.filter(last_activity__gte=week_ago))
        elif user_filter == 'new':
            # Новые за последнюю неделю
            week_ago = timezone.now() - timedelta(days=7)
            return list(users.filter(created_at__gte=week_ago))
        elif user_filter == 'balance':
            # С положительным балансом
            return list(users.filter(balance__gt=0))
        elif user_filter == 'language':
            # По языку (используем язык сообщения)
            return list(users.filter(language=self.session.message.language))
        
        return list(users)
    
    def check_already_sent(self, user: User) -> bool:
        """Проверяет, было ли уже отправлено сообщение пользователю"""
        return MassSendRecipient.objects.filter(
            session__message=self.session.message,
            user=user,
            status='SENT'
        ).exists()
    
    def create_recipients(self, users: List[User]):
        """Создает записи получателей"""
        recipients = []
        for user in users:
            if not self.check_already_sent(user):
                recipients.append(MassSendRecipient(
                    session=self.session,
                    user=user,
                    status='PENDING'
                ))
            else:
                recipients.append(MassSendRecipient(
                    session=self.session,
                    user=user,
                    status='SKIPPED'
                ))
        
        MassSendRecipient.objects.bulk_create(recipients, ignore_conflicts=True)
        
        # Обновляем статистику
        self.session.total_recipients = len(recipients)
        self.session.skipped_count = sum(1 for r in recipients if r.status == 'SKIPPED')
        self.session.save()
    
    async def send_message_to_user(self, recipient: MassSendRecipient) -> bool:
        """Отправляет сообщение пользователю"""
        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from common.metasleuth import send_telegram_message
            
            # Отправляем сообщение
            result = await send_telegram_message(
                user_id=recipient.user.tg_id,
                message=self.session.message.content,
                parse_mode='HTML'
            )
            
            if result.get('success'):
                recipient.mark_as_sent(result.get('message_id'))
                return True
            else:
                recipient.mark_as_failed(result.get('error', 'Неизвестная ошибка'))
                return False
                
        except Exception as e:
            recipient.mark_as_failed(str(e))
            return False
    
    async def send_batch(self, recipients: List[MassSendRecipient]) -> Dict[str, int]:
        """Отправляет пакет сообщений"""
        results = {'sent': 0, 'failed': 0, 'skipped': 0}
        
        for recipient in recipients:
            if self.is_cancelled:
                break
                
            while self.is_paused:
                await asyncio.sleep(1)
                if self.is_cancelled:
                    break
            
            if recipient.status == 'SKIPPED':
                results['skipped'] += 1
                continue
            
            success = await self.send_message_to_user(recipient)
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            # Задержка между сообщениями
            await asyncio.sleep(self.session.delay_between_messages)
        
        return results
    
    def update_progress(self, batch_results: Dict[str, int]):
        """Обновляет прогресс сессии"""
        with transaction.atomic():
            self.session.refresh_from_db()
            self.session.sent_count += batch_results['sent']
            self.session.failed_count += batch_results['failed']
            self.session.skipped_count += batch_results['skipped']
            self.session.estimated_completion = self.session.get_eta()
            self.session.save()
    
    async def run_sending(self):
        """Основной цикл отправки"""
        if not self.load_session():
            return False
        
        # Получаем пользователей
        users = self.get_users_by_filter(self.session.user_filter)
        self.create_recipients(users)
        
        # Обновляем статус
        self.session.status = 'RUNNING'
        self.session.started_at = timezone.now()
        self.session.save()
        
        self.is_running = True
        
        # Получаем получателей для отправки
        recipients = MassSendRecipient.objects.filter(
            session=self.session,
            status='PENDING'
        ).order_by('created_at')
        
        total_recipients = recipients.count()
        if total_recipients == 0:
            self.session.status = 'COMPLETED'
            self.session.completed_at = timezone.now()
            self.session.save()
            return True
        
        # Разбиваем на пакеты
        batch_size = self.session.batch_size
        total_batches = (total_recipients + batch_size - 1) // batch_size
        
        for i in range(0, total_recipients, batch_size):
            if self.is_cancelled:
                break
            
            batch_recipients = list(recipients[i:i + batch_size])
            batch_results = await self.send_batch(batch_recipients)
            
            self.update_progress(batch_results)
            
            # Задержка между пакетами
            if i + batch_size < total_recipients and not self.is_cancelled:
                await asyncio.sleep(self.session.delay_between_batches)
        
        # Завершаем сессию
        if self.is_cancelled:
            self.session.status = 'CANCELLED'
        else:
            self.session.status = 'COMPLETED'
        
        self.session.completed_at = timezone.now()
        self.session.save()
        
        self.is_running = False
        return True
    
    def pause(self):
        """Приостанавливает отправку"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.session.status = 'PAUSED'
            self.session.paused_at = timezone.now()
            self.session.save()
            return True
        return False
    
    def resume(self):
        """Возобновляет отправку"""
        if self.is_paused and not self.is_cancelled:
            self.is_paused = False
            self.session.status = 'RUNNING'
            self.session.save()
            return True
        return False
    
    def cancel(self):
        """Отменяет отправку"""
        if self.is_running or self.is_paused:
            self.is_cancelled = True
            self.session.status = 'CANCELLED'
            self.session.is_cancelled = True
            self.session.save()
            return True
        return False
    
    def get_status(self) -> Dict:
        """Возвращает статус сессии"""
        if not self.session:
            return {'error': 'Сессия не найдена'}
        
        return {
            'session_id': self.session.id,
            'status': self.session.status,
            'progress': self.session.progress_percentage,
            'total': self.session.total_recipients,
            'sent': self.session.sent_count,
            'failed': self.session.failed_count,
            'skipped': self.session.skipped_count,
            'remaining': self.session.remaining_count,
            'eta': self.session.estimated_completion.isoformat() if self.session.estimated_completion else None,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'is_cancelled': self.is_cancelled,
        }


class MassSendManagerFactory:
    """Фабрика для создания менеджеров рассылки"""
    
    @staticmethod
    def create_session(message_id: int, user_filter: str, created_by_id: int, 
                      batch_size: int = 50, delay_between_batches: int = 1, 
                      delay_between_messages: float = 0.1) -> MassSendSession:
        """Создает новую сессию рассылки"""
        from .admin_models import MassMessage, AdminUser
        
        message = MassMessage.objects.get(id=message_id)
        admin_user = AdminUser.objects.get(id=created_by_id)
        
        session = MassSendSession.objects.create(
            message=message,
            user_filter=user_filter,
            batch_size=batch_size,
            delay_between_batches=delay_between_batches,
            delay_between_messages=delay_between_messages,
            created_by=admin_user
        )
        
        return session
    
    @staticmethod
    def get_manager(session_id: int) -> MassSendManager:
        """Получает менеджер для существующей сессии"""
        return MassSendManager(session_id)
    
    @staticmethod
    def start_sending(session_id: int):
        """Запускает отправку в отдельном потоке"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            manager = MassSendManager(session_id)
            try:
                loop.run_until_complete(manager.run_sending())
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()
        return thread


# Глобальный кэш для хранения активных менеджеров
_active_managers = {}


def get_active_manager(session_id: int) -> Optional[MassSendManager]:
    """Получает активный менеджер из кэша"""
    return _active_managers.get(session_id)


def set_active_manager(session_id: int, manager: MassSendManager):
    """Сохраняет менеджер в кэш"""
    _active_managers[session_id] = manager


def remove_active_manager(session_id: int):
    """Удаляет менеджер из кэша"""
    _active_managers.pop(session_id, None)
