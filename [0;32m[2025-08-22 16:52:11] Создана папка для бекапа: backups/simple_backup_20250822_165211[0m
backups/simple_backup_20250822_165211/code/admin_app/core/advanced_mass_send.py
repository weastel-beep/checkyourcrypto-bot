"""
Продвинутая система массовой рассылки для больших объемов
"""
import asyncio
import threading
import queue
import time
from typing import List, Dict, Optional
from aiogram import Bot
from django.conf import settings
from django.db import transaction
from .models import User
from .admin_models import MassMessage
from asgiref.sync import sync_to_async


class AdvancedMassSender:
    """Продвинутый отправитель массовых сообщений"""
    
    def __init__(self, message_id: int, batch_size: int = 100, delay_between_batches: float = 2.0):
        self.message_id = message_id
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.bot = None
        self.message = None
        self.is_cancelled = False
        self.progress_callback = None
        
    async def initialize(self):
        """Инициализация"""
        self.bot = Bot(token=settings.BOT_TOKEN)
        self.message = await sync_to_async(MassMessage.objects.get)(id=self.message_id)
        
        if self.message.status == 'SENDING':
            raise Exception("Сообщение уже отправляется")
            
        self.message.status = 'SENDING'
        await sync_to_async(self.message.save)()
        
    async def get_users_batch(self, offset: int) -> List[User]:
        """Получаем батч пользователей"""
        users = await sync_to_async(list)(
            User.objects.filter(is_blocked=False)[offset:offset + self.batch_size]
        )
        return users
        
    async def get_total_users_count(self) -> int:
        """Получаем общее количество пользователей"""
        return await sync_to_async(User.objects.filter(is_blocked=False).count)()
        
    async def send_batch(self, users: List[User]) -> Dict[str, int]:
        """Отправляем батч пользователей"""
        success_count = 0
        failed_count = 0
        
        # Создаем задачи для параллельной отправки
        tasks = []
        for user in users:
            task = self.send_to_user(user)
            tasks.append(task)
            
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
            else:
                success_count += 1
                
        return {"success": success_count, "failed": failed_count}
        
    async def send_to_user(self, user: User) -> bool:
        """Отправляем сообщение одному пользователю"""
        try:
            await self.bot.send_message(
                chat_id=user.tg_id,
                text=self.message.content
            )
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки пользователю {user.tg_id}: {e}")
            return False
            
    async def update_progress(self, processed: int, total: int, success: int, failed: int):
        """Обновляем прогресс"""
        if self.progress_callback:
            await self.progress_callback(processed, total, success, failed)
            
        # Обновляем в базе каждые 100 пользователей
        if processed % 100 == 0:
            self.message.sent_count = success
            self.message.failed_count = failed
            await sync_to_async(self.message.save)()
            
    async def run(self) -> Dict[str, int]:
        """Основной метод отправки"""
        try:
            await self.initialize()
            
            total_users = await self.get_total_users_count()
            offset = 0
            total_success = 0
            total_failed = 0
            processed = 0
            
            print(f"🚀 Начинаем продвинутую отправку сообщения {self.message_id}")
            print(f"📊 Всего пользователей: {total_users}")
            print(f"📦 Размер батча: {self.batch_size}")
            print(f"⏱️ Задержка между батчами: {self.delay_between_batches}с")
            
            while offset < total_users and not self.is_cancelled:
                # Получаем батч пользователей
                users = await self.get_users_batch(offset)
                if not users:
                    break
                    
                # Отправляем батч
                batch_result = await self.send_batch(users)
                total_success += batch_result["success"]
                total_failed += batch_result["failed"]
                processed += len(users)
                
                # Обновляем прогресс
                await self.update_progress(processed, total_users, total_success, total_failed)
                
                print(f"📊 Батч {offset//self.batch_size + 1}: {len(users)} пользователей, "
                      f"успешно: {batch_result['success']}, ошибок: {batch_result['failed']}")
                
                offset += self.batch_size
                
                # Задержка между батчами (кроме последнего)
                if offset < total_users and not self.is_cancelled:
                    await asyncio.sleep(self.delay_between_batches)
                    
            # Финальное обновление
            self.message.sent_count = total_success
            self.message.failed_count = total_failed
            self.message.total_users = total_users
            self.message.status = 'COMPLETED' if not self.is_cancelled else 'CANCELLED'
            await sync_to_async(self.message.save)()
            
            print(f"🎉 Отправка завершена! Обработано: {processed}, "
                  f"Успешно: {total_success}, Ошибок: {total_failed}")
                  
            return {
                "success": total_success,
                "failed": total_failed,
                "total": total_users,
                "processed": processed
            }
            
        except Exception as e:
            print(f"❌ Ошибка в продвинутой отправке: {e}")
            if self.message:
                self.message.status = 'FAILED'
                await sync_to_async(self.message.save)()
            raise
            
    def cancel(self):
        """Отмена отправки"""
        self.is_cancelled = True
        print("🛑 Отправка отменена пользователем")


async def send_advanced_mass_message(message_id: int, batch_size: int = 100, 
                                   delay_between_batches: float = 2.0) -> Dict[str, int]:
    """Продвинутая отправка массового сообщения"""
    sender = AdvancedMassSender(message_id, batch_size, delay_between_batches)
    return await sender.run()


def send_advanced_mass_message_sync(message_id: int, batch_size: int = 100, 
                                   delay_between_batches: float = 2.0) -> Dict[str, int]:
    """Синхронная обертка для продвинутой отправки"""
    result_queue = queue.Queue()
    
    def run_async():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    send_advanced_mass_message(message_id, batch_size, delay_between_batches)
                )
                result_queue.put(('success', result))
            except Exception as e:
                result_queue.put(('error', str(e)))
            finally:
                loop.close()
        except Exception as e:
            result_queue.put(('error', f"Ошибка создания loop: {str(e)}"))
    
    thread = threading.Thread(target=run_async)
    thread.daemon = True
    thread.start()
    
    try:
        status, result = result_queue.get(timeout=3600)  # 1 час таймаут
        if status == 'error':
            raise Exception(result)
        return result
    except queue.Empty:
        raise Exception("Таймаут отправки (1 час)")


# Функция для автоматического выбора стратегии
def send_mass_message_smart(message_id: int) -> Dict[str, int]:
    """Умная отправка - выбирает стратегию в зависимости от количества пользователей"""
    try:
        # Получаем количество пользователей
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = false")
            total_users = cursor.fetchone()[0]
        
        print(f"📊 Обнаружено {total_users} пользователей")
        
        if total_users <= 1000:
            # Для малых объемов используем простую отправку
            print("🔄 Используем простую стратегию отправки")
            from .simple_send import send_mass_message_sync
            return send_mass_message_sync(message_id)
        else:
            # Для больших объемов используем продвинутую отправку
            print("🚀 Используем продвинутую стратегию отправки")
            
            # Автоматически подбираем параметры
            if total_users <= 10000:
                batch_size = 50
                delay = 1.0
            elif total_users <= 50000:
                batch_size = 100
                delay = 2.0
            else:
                batch_size = 200
                delay = 3.0
                
            print(f"⚙️ Параметры: батч={batch_size}, задержка={delay}с")
            return send_advanced_mass_message_sync(message_id, batch_size, delay)
            
    except Exception as e:
        print(f"❌ Ошибка в умной отправке: {e}")
        # Fallback к простой отправке
        from .simple_send import send_mass_message_sync
        return send_mass_message_sync(message_id)
