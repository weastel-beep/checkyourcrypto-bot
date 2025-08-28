"""
Система мониторинга прогресса массовой рассылки
"""
import json
import time
from typing import Dict, Optional
from django.core.cache import cache
from django.conf import settings


class MassSendMonitor:
    """Монитор прогресса массовой рассылки"""
    
    CACHE_PREFIX = "mass_send_progress_"
    CACHE_TTL = 3600  # 1 час
    
    @classmethod
    def update_progress(cls, message_id: int, processed: int, total: int, 
                       success: int, failed: int, status: str = "sending"):
        """Обновляем прогресс отправки"""
        progress_data = {
            "message_id": message_id,
            "processed": processed,
            "total": total,
            "success": success,
            "failed": failed,
            "status": status,
            "percentage": round((processed / total * 100) if total > 0 else 0, 2),
            "timestamp": time.time(),
            "estimated_time_remaining": cls._calculate_eta(processed, total, success, failed)
        }
        
        cache_key = f"{cls.CACHE_PREFIX}{message_id}"
        cache.set(cache_key, json.dumps(progress_data), cls.CACHE_TTL)
        
    @classmethod
    def get_progress(cls, message_id: int) -> Optional[Dict]:
        """Получаем текущий прогресс"""
        cache_key = f"{cls.CACHE_PREFIX}{message_id}"
        data = cache.get(cache_key)
        
        if data:
            return json.loads(data)
        return None
        
    @classmethod
    def clear_progress(cls, message_id: int):
        """Очищаем прогресс"""
        cache_key = f"{cls.CACHE_PREFIX}{message_id}"
        cache.delete(cache_key)
        
    @classmethod
    def _calculate_eta(cls, processed: int, total: int, success: int, failed: int) -> Optional[int]:
        """Рассчитываем оставшееся время"""
        if processed == 0 or total == 0:
            return None
            
        # Средняя скорость обработки (пользователей в секунду)
        # Предполагаем, что каждый пользователь занимает ~0.1 секунды
        avg_time_per_user = 0.1
        
        remaining_users = total - processed
        eta_seconds = remaining_users * avg_time_per_user
        
        return int(eta_seconds)


def get_mass_send_stats() -> Dict:
    """Получаем общую статистику массовых рассылок"""
    try:
        from .admin_models import MassMessage
        
        # Статистика по статусам
        stats = {
            "total_messages": MassMessage.objects.count(),
            "draft": MassMessage.objects.filter(status="DRAFT").count(),
            "sending": MassMessage.objects.filter(status="SENDING").count(),
            "completed": MassMessage.objects.filter(status="COMPLETED").count(),
            "failed": MassMessage.objects.filter(status="FAILED").count(),
            "cancelled": MassMessage.objects.filter(status="CANCELLED").count(),
        }
        
        # Общая статистика отправки
        completed_messages = MassMessage.objects.filter(status="COMPLETED")
        total_sent = sum(msg.sent_count for msg in completed_messages)
        total_failed = sum(msg.failed_count for msg in completed_messages)
        
        stats.update({
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": round((total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0, 2)
        })
        
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return {}


def format_duration(seconds: int) -> str:
    """Форматируем длительность"""
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}м {seconds % 60}с"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}ч {minutes}м"


def get_user_count_estimate() -> Dict:
    """Получаем оценку количества пользователей"""
    try:
        from .models import User
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_blocked=False).count()
        blocked_users = User.objects.filter(is_blocked=True).count()
        
        return {
            "total": total_users,
            "active": active_users,
            "blocked": blocked_users,
            "active_percentage": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
        }
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики пользователей: {e}")
        return {}
