"""
Простая отправка массовых сообщений
"""
import asyncio
from aiogram import Bot
from django.conf import settings
from .models import User
from .admin_models import MassMessage


async def send_simple_mass_message(message_id: int):
    """Простая отправка массового сообщения"""
    try:
        # Получаем сообщение - используем sync_to_async для Django ORM
        from asgiref.sync import sync_to_async
        
        message = await sync_to_async(MassMessage.objects.get)(id=message_id)
        
        # Проверяем статус - разрешаем повторную отправку
        if message.status == 'SENDING':
            raise Exception("Сообщение уже отправляется. Подождите завершения.")
        
        # Получаем всех пользователей
        users = await sync_to_async(list)(User.objects.filter(is_blocked=False))
        
        # Создаем бота
        bot = Bot(token=settings.BOT_TOKEN)
        
        # Устанавливаем статус отправки
        message.status = 'SENDING'
        await sync_to_async(message.save)()
        
        # Отправляем всем с задержкой для больших объемов
        success_count = 0
        failed_count = 0
        total_users = len(users)
        
        print(f"🚀 Начинаем отправку сообщения {message_id} для {total_users} пользователей")
        
        for i, user in enumerate(users):
            try:
                await bot.send_message(
                    chat_id=user.tg_id,
                    text=message.content
                )
                success_count += 1
                
                # Прогресс каждые 10 пользователей
                if (i + 1) % 10 == 0 or (i + 1) == total_users:
                    print(f"📊 Прогресс: {i + 1}/{total_users} ({success_count} успешно, {failed_count} ошибок)")
                
                # Небольшая задержка для больших объемов (чтобы не спамить Telegram API)
                if total_users > 50 and (i + 1) % 20 == 0:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Ошибка отправки пользователю {user.tg_id}: {e}")
        
        # Обновляем статистику
        message.sent_count = success_count
        message.failed_count = failed_count
        message.total_users = total_users
        message.status = 'COMPLETED'
        await sync_to_async(message.save)()
        
        print(f"🎉 Отправка завершена! Успешно: {success_count}, Ошибок: {failed_count}")
        
        return {
            "success": success_count,
            "failed": failed_count
        }
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        # Обновляем статус на ошибку
        try:
            from asgiref.sync import sync_to_async
            message = await sync_to_async(MassMessage.objects.get)(id=message_id)
            message.status = 'FAILED'
            await sync_to_async(message.save)()
        except:
            pass
        raise


def send_mass_message_sync(message_id: int):
    """Синхронная обертка для отправки"""
    import threading
    import queue
    
    result_queue = queue.Queue()
    
    def run_async():
        try:
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(send_simple_mass_message(message_id))
                result_queue.put(('success', result))
            except Exception as e:
                result_queue.put(('error', str(e)))
            finally:
                loop.close()
        except Exception as e:
            result_queue.put(('error', f"Ошибка создания loop: {str(e)}"))
    
    # Запускаем в отдельном потоке
    thread = threading.Thread(target=run_async)
    thread.daemon = True
    thread.start()
    
    try:
        status, result = result_queue.get(timeout=60)  # 60 секунд таймаут
        if status == 'error':
            raise Exception(result)
        return result
    except queue.Empty:
        raise Exception("Таймаут отправки (60 секунд)")
