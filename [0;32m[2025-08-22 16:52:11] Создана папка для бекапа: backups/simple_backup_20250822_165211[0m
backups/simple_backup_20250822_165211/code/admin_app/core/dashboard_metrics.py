"""
Метрики дашборда Check Your Crypto
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal

from django.db.models import Count, Sum, Q, Avg, Max, Min
from django.utils import timezone
from django.core.cache import cache

from .models import User, Check, Payment, Setting
from .admin_models import SystemMetrics, AdminActionLog


class DashboardMetrics:
    """Класс для сбора метрик дашборда"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 минут
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Базовые статистики"""
        cache_key = "dashboard_basic_stats"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Пользователи
            total_users = User.objects.count()
            new_users_today = User.objects.filter(created_at__date=today).count()
            new_users_week = User.objects.filter(created_at__gte=week_ago).count()
            new_users_month = User.objects.filter(created_at__gte=month_ago).count()
            
            # Активность
            active_users_today = User.objects.filter(last_activity__date=today).count()
            active_users_week = User.objects.filter(last_activity__gte=week_ago).count()
            
            # Проверки
            total_checks = Check.objects.count()
            checks_today = Check.objects.filter(created_at__date=today).count()
            checks_week = Check.objects.filter(created_at__gte=week_ago).count()
            checks_month = Check.objects.filter(created_at__gte=month_ago).count()
            
            # Финансы
            total_revenue = Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount'))['total'] or 0
            revenue_today = Payment.objects.filter(
                status='completed', created_at__date=today
            ).aggregate(total=Sum('amount'))['total'] or 0
            revenue_week = Payment.objects.filter(
                status='completed', created_at__gte=week_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            revenue_month = Payment.objects.filter(
                status='completed', created_at__gte=month_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Средние значения
            avg_check_amount = Payment.objects.filter(status='completed').aggregate(
                avg=Avg('amount'))['avg'] or 0
            avg_checks_per_user = total_checks / total_users if total_users > 0 else 0
            
            stats = {
                'users': {
                    'total': total_users,
                    'new_today': new_users_today,
                    'new_week': new_users_week,
                    'new_month': new_users_month,
                    'active_today': active_users_today,
                    'active_week': active_users_week,
                    'growth_rate': self._calculate_growth_rate(new_users_week, new_users_month)
                },
                'checks': {
                    'total': total_checks,
                    'today': checks_today,
                    'week': checks_week,
                    'month': checks_month,
                    'avg_per_user': round(avg_checks_per_user, 2),
                    'growth_rate': self._calculate_growth_rate(checks_week, checks_month)
                },
                'revenue': {
                    'total': float(total_revenue),
                    'today': float(revenue_today),
                    'week': float(revenue_week),
                    'month': float(revenue_month),
                    'avg_check': float(avg_check_amount),
                    'growth_rate': self._calculate_growth_rate(revenue_week, revenue_month)
                }
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
            return stats
            
        except Exception as e:
            return self._get_default_stats()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Метрики производительности"""
        cache_key = "dashboard_performance"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Время ответа API
            recent_checks = Check.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')[:100]
            
            avg_response_time = 0
            if recent_checks:
                response_times = []
                for check in recent_checks:
                    if hasattr(check, 'response_time') and check.response_time:
                        response_times.append(check.response_time)
                
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
            
            # Ошибки
            error_count_today = Check.objects.filter(
                created_at__date=timezone.now().date(),
                status='error'
            ).count()
            
            error_rate = 0
            if checks_today := Check.objects.filter(
                created_at__date=timezone.now().date()
            ).count():
                error_rate = (error_count_today / checks_today) * 100
            
            # Использование ресурсов
            system_metrics = SystemMetrics.objects.order_by('-timestamp').first()
            
            performance = {
                'response_time': {
                    'avg_ms': round(avg_response_time * 1000, 2),
                    'status': 'good' if avg_response_time < 1.0 else 'warning' if avg_response_time < 3.0 else 'critical'
                },
                'errors': {
                    'count_today': error_count_today,
                    'rate_percent': round(error_rate, 2),
                    'status': 'good' if error_rate < 5 else 'warning' if error_rate < 10 else 'critical'
                },
                'system': {
                    'cpu_usage': getattr(system_metrics, 'cpu_usage', 0),
                    'memory_usage': getattr(system_metrics, 'memory_usage', 0),
                    'disk_usage': getattr(system_metrics, 'disk_usage', 0),
                    'uptime_hours': getattr(system_metrics, 'uptime_hours', 0)
                }
            }
            
            cache.set(cache_key, performance, self.cache_timeout)
            return performance
            
        except Exception as e:
            return self._get_default_performance()
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Аналитические данные"""
        cache_key = "dashboard_analytics"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Топ адресов
            top_addresses = Check.objects.values('address').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # Топ пользователей
            top_users = User.objects.annotate(
                check_count=Count('checks')
            ).order_by('-check_count')[:10]
            
            # Статистика по времени
            hourly_stats = self._get_hourly_stats()
            daily_stats = self._get_daily_stats()
            
            # География (если есть данные)
            geography_stats = self._get_geography_stats()
            
            analytics = {
                'top_addresses': list(top_addresses),
                'top_users': [
                    {
                        'tg_id': user.tg_id,
                        'username': user.username,
                        'check_count': user.check_count,
                        'balance': float(user.balance)
                    }
                    for user in top_users
                ],
                'hourly_stats': hourly_stats,
                'daily_stats': daily_stats,
                'geography': geography_stats
            }
            
            cache.set(cache_key, analytics, self.cache_timeout)
            return analytics
            
        except Exception as e:
            return self._get_default_analytics()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Здоровье системы"""
        try:
            # Статус компонентов
            bot_status = self._check_bot_status()
            database_status = self._check_database_status()
            api_status = self._check_api_status()
            
            # Последние ошибки
            recent_errors = self._get_recent_errors()
            
            # Алерты
            alerts = self._get_active_alerts()
            
            health = {
                'components': {
                    'bot': bot_status,
                    'database': database_status,
                    'api': api_status
                },
                'recent_errors': recent_errors,
                'alerts': alerts,
                'overall_status': self._calculate_overall_status(bot_status, database_status, api_status)
            }
            
            return health
            
        except Exception as e:
            return self._get_default_health()
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Бизнес метрики"""
        try:
            # Конверсия
            total_visitors = User.objects.count()
            paying_users = User.objects.filter(payments__status='completed').distinct().count()
            conversion_rate = (paying_users / total_visitors * 100) if total_visitors > 0 else 0
            
            # LTV (Lifetime Value)
            avg_revenue_per_user = Payment.objects.filter(
                status='completed'
            ).aggregate(avg=Avg('amount'))['avg'] or 0
            
            # Churn rate (примерно)
            inactive_users = User.objects.filter(
                last_activity__lt=timezone.now() - timedelta(days=30)
            ).count()
            churn_rate = (inactive_users / total_visitors * 100) if total_visitors > 0 else 0
            
            # ARPU (Average Revenue Per User)
            total_revenue = Payment.objects.filter(
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            arpu = total_revenue / total_visitors if total_visitors > 0 else 0
            
            business = {
                'conversion': {
                    'rate_percent': round(conversion_rate, 2),
                    'paying_users': paying_users,
                    'total_users': total_visitors
                },
                'ltv': {
                    'avg_revenue_per_user': float(avg_revenue_per_user),
                    'status': 'good' if avg_revenue_per_user > 10 else 'warning'
                },
                'churn': {
                    'rate_percent': round(churn_rate, 2),
                    'inactive_users': inactive_users,
                    'status': 'good' if churn_rate < 20 else 'warning' if churn_rate < 40 else 'critical'
                },
                'arpu': {
                    'value': float(arpu),
                    'status': 'good' if arpu > 5 else 'warning'
                }
            }
            
            return business
            
        except Exception as e:
            return self._get_default_business()
    
    def _calculate_growth_rate(self, current: int, previous: int) -> float:
        """Расчет темпа роста"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
    
    def _get_hourly_stats(self) -> List[Dict[str, Any]]:
        """Статистика по часам"""
        stats = []
        now = timezone.now()
        
        for i in range(24):
            hour_start = now.replace(hour=i, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            checks_count = Check.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end
            ).count()
            
            users_count = User.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end
            ).count()
            
            stats.append({
                'hour': i,
                'checks': checks_count,
                'users': users_count
            })
        
        return stats
    
    def _get_daily_stats(self) -> List[Dict[str, Any]]:
        """Статистика по дням"""
        stats = []
        now = timezone.now()
        
        for i in range(30):
            date = now.date() - timedelta(days=i)
            
            checks_count = Check.objects.filter(
                created_at__date=date
            ).count()
            
            users_count = User.objects.filter(
                created_at__date=date
            ).count()
            
            revenue = Payment.objects.filter(
                status='completed',
                created_at__date=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'checks': checks_count,
                'users': users_count,
                'revenue': float(revenue)
            })
        
        return list(reversed(stats))
    
    def _get_geography_stats(self) -> Dict[str, Any]:
        """Географическая статистика"""
        # Пока возвращаем заглушку
        return {
            'top_countries': [],
            'total_countries': 0
        }
    
    def _check_bot_status(self) -> Dict[str, Any]:
        """Проверка статуса бота"""
        try:
            # Проверяем последнюю активность
            last_check = Check.objects.order_by('-created_at').first()
            
            if last_check and (timezone.now() - last_check.created_at).seconds < 300:  # 5 минут
                return {'status': 'online', 'last_activity': last_check.created_at}
            else:
                return {'status': 'offline', 'last_activity': last_check.created_at if last_check else None}
                
        except Exception:
            return {'status': 'unknown', 'last_activity': None}
    
    def _check_database_status(self) -> Dict[str, Any]:
        """Проверка статуса базы данных"""
        try:
            # Простой тест подключения
            User.objects.count()
            return {'status': 'healthy', 'connection': 'ok'}
        except Exception:
            return {'status': 'error', 'connection': 'failed'}
    
    def _check_api_status(self) -> Dict[str, Any]:
        """Проверка статуса API"""
        try:
            # Проверяем последние API вызовы
            recent_api_calls = Check.objects.filter(
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            if recent_api_calls > 0:
                return {'status': 'healthy', 'recent_calls': recent_api_calls}
            else:
                return {'status': 'warning', 'recent_calls': 0}
                
        except Exception:
            return {'status': 'error', 'recent_calls': 0}
    
    def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Получение последних ошибок"""
        try:
            recent_errors = Check.objects.filter(
                status='error',
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')[:10]
            
            return [
                {
                    'id': check.id,
                    'address': check.address,
                    'error': getattr(check, 'error_message', 'Unknown error'),
                    'timestamp': check.created_at
                }
                for check in recent_errors
            ]
        except Exception:
            return []
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Получение активных алертов"""
        alerts = []
        
        # Проверяем различные условия для алертов
        try:
            # Алерт на высокую нагрузку
            recent_checks = Check.objects.filter(
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            if recent_checks > 100:  # Больше 100 проверок за 5 минут
                alerts.append({
                    'type': 'high_load',
                    'message': f'Высокая нагрузка: {recent_checks} проверок за 5 минут',
                    'severity': 'warning'
                })
            
            # Алерт на ошибки
            error_rate = self.get_performance_metrics()['errors']['rate_percent']
            if error_rate > 10:
                alerts.append({
                    'type': 'high_error_rate',
                    'message': f'Высокий процент ошибок: {error_rate}%',
                    'severity': 'critical'
                })
            
            # Алерт на низкую конверсию
            business_metrics = self.get_business_metrics()
            conversion_rate = business_metrics['conversion']['rate_percent']
            if conversion_rate < 1:
                alerts.append({
                    'type': 'low_conversion',
                    'message': f'Низкая конверсия: {conversion_rate}%',
                    'severity': 'warning'
                })
                
        except Exception:
            pass
        
        return alerts
    
    def _calculate_overall_status(self, bot_status: Dict, db_status: Dict, api_status: Dict) -> str:
        """Расчет общего статуса системы"""
        statuses = [bot_status['status'], db_status['status'], api_status['status']]
        
        if 'error' in statuses:
            return 'critical'
        elif 'warning' in statuses:
            return 'warning'
        else:
            return 'healthy'
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Дефолтные статистики при ошибке"""
        return {
            'users': {'total': 0, 'new_today': 0, 'new_week': 0, 'new_month': 0, 'active_today': 0, 'active_week': 0, 'growth_rate': 0},
            'checks': {'total': 0, 'today': 0, 'week': 0, 'month': 0, 'avg_per_user': 0, 'growth_rate': 0},
            'revenue': {'total': 0.0, 'today': 0.0, 'week': 0.0, 'month': 0.0, 'avg_check': 0.0, 'growth_rate': 0}
        }
    
    def _get_default_performance(self) -> Dict[str, Any]:
        """Дефолтные метрики производительности"""
        return {
            'response_time': {'avg_ms': 0, 'status': 'unknown'},
            'errors': {'count_today': 0, 'rate_percent': 0, 'status': 'unknown'},
            'system': {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': 0, 'uptime_hours': 0}
        }
    
    def _get_default_analytics(self) -> Dict[str, Any]:
        """Дефолтные аналитические данные"""
        return {
            'top_addresses': [],
            'top_users': [],
            'hourly_stats': [],
            'daily_stats': [],
            'geography': {'top_countries': [], 'total_countries': 0}
        }
    
    def _get_default_health(self) -> Dict[str, Any]:
        """Дефолтное состояние здоровья системы"""
        return {
            'components': {
                'bot': {'status': 'unknown', 'last_activity': None},
                'database': {'status': 'unknown', 'connection': 'unknown'},
                'api': {'status': 'unknown', 'recent_calls': 0}
            },
            'recent_errors': [],
            'alerts': [],
            'overall_status': 'unknown'
        }
    
    def _get_default_business(self) -> Dict[str, Any]:
        """Дефолтные бизнес метрики"""
        return {
            'conversion': {'rate_percent': 0, 'paying_users': 0, 'total_users': 0},
            'ltv': {'avg_revenue_per_user': 0.0, 'status': 'unknown'},
            'churn': {'rate_percent': 0, 'inactive_users': 0, 'status': 'unknown'},
            'arpu': {'value': 0.0, 'status': 'unknown'}
        }


# Глобальный экземпляр
dashboard_metrics = DashboardMetrics()
