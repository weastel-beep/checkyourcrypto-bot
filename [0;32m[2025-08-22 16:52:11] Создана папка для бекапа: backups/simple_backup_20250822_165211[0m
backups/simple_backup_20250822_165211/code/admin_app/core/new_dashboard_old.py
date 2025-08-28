"""
Новый современный дашборд Check Your Crypto
"""
import json
from datetime import datetime
from typing import Dict, Any

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .dashboard_metrics import dashboard_metrics


@login_required
def new_dashboard(request):
    """Новый современный дашборд"""
    try:
        # Получаем все метрики
        basic_stats = dashboard_metrics.get_basic_stats()
        performance = dashboard_metrics.get_performance_metrics()
        analytics = dashboard_metrics.get_analytics_data()
        system_health = dashboard_metrics.get_system_health()
        business_metrics = dashboard_metrics.get_business_metrics()
        
        context = {
            'basic_stats': basic_stats,
            'performance': performance,
            'analytics': analytics,
            'system_health': system_health,
            'business_metrics': business_metrics,
            'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render(request, 'panel/new_dashboard.html', context)
        
    except Exception as e:
        # Fallback на простой дашборд при ошибке
        return render(request, 'panel/fallback_dashboard.html', {'error': str(e)})


@login_required
def dashboard_api(request):
    """API для получения данных дашборда"""
    try:
        # Получаем все метрики
        data = {
            'basic_stats': dashboard_metrics.get_basic_stats(),
            'performance': dashboard_metrics.get_performance_metrics(),
            'analytics': dashboard_metrics.get_analytics_data(),
            'system_health': dashboard_metrics.get_system_health(),
            'business_metrics': dashboard_metrics.get_business_metrics(),
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def generate_dashboard_html(context: Dict[str, Any]) -> str:
    """Генерация HTML дашборда"""
    
    def get_status_color(status: str) -> str:
        """Получение цвета статуса"""
        colors = {
            'good': 'text-green-600',
            'warning': 'text-yellow-600',
            'critical': 'text-red-600',
            'error': 'text-red-600',
            'healthy': 'text-green-600',
            'offline': 'text-red-600',
            'online': 'text-green-600',
            'unknown': 'text-gray-600'
        }
        return colors.get(status, 'text-gray-600')
    
    def get_status_bg_color(status: str) -> str:
        """Получение цвета фона статуса"""
        colors = {
            'good': 'bg-green-100',
            'warning': 'bg-yellow-100',
            'critical': 'bg-red-100',
            'error': 'bg-red-100',
            'healthy': 'bg-green-100',
            'offline': 'bg-red-100',
            'online': 'bg-green-100',
            'unknown': 'bg-gray-100'
        }
        return colors.get(status, 'bg-gray-100')
    
    basic_stats = context['basic_stats']
    performance = context['performance']
    system_health = context['system_health']
    business_metrics = context['business_metrics']
    
    # Подготавливаем данные для HTML
    bot_status = system_health['components']['bot']['status']
    db_status = system_health['components']['database']['status']
    api_status = system_health['components']['api']['status']
    
    bot_bg_color = get_status_bg_color(bot_status)
    bot_text_color = get_status_color(bot_status)
    db_bg_color = get_status_bg_color(db_status)
    db_text_color = get_status_color(db_status)
    api_bg_color = get_status_bg_color(api_status)
    api_text_color = get_status_color(api_status)
    
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Check Your Crypto - Дашборд</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Автообновление каждые 30 секунд
            setInterval(() => {
                fetch('/api/panel/dashboard/api/')
                    .then(response => response.json())
                    .then(data => {
                        updateDashboard(data);
                    })
                    .catch(error => console.error('Error:', error));
            }, 30000);
            
            function updateDashboard(data) {
                // Обновление статистик
                document.getElementById('total-users').textContent = data.basic_stats.users.total;
                document.getElementById('new-users-today').textContent = data.basic_stats.users.new_today;
                document.getElementById('total-checks').textContent = data.basic_stats.checks.total;
                document.getElementById('checks-today').textContent = data.basic_stats.checks.today;
                document.getElementById('total-revenue').textContent = '$' + data.basic_stats.revenue.total.toFixed(2);
                document.getElementById('revenue-today').textContent = '$' + data.basic_stats.revenue.today.toFixed(2);
                
                // Обновление статусов
                updateStatus('bot-status', data.system_health.components.bot.status);
                updateStatus('db-status', data.system_health.components.database.status);
                updateStatus('api-status', data.system_health.components.api.status);
                
                // Обновление времени
                document.getElementById('last-updated').textContent = new Date().toLocaleString('ru-RU');
            }
            
            function updateStatus(elementId, status) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ' + getStatusClass(status);
                    element.textContent = status;
                }
            }
            
            function getStatusClass(status) {
                const classes = {
                    'good': 'bg-green-100 text-green-800',
                    'warning': 'bg-yellow-100 text-yellow-800',
                    'critical': 'bg-red-100 text-red-800',
                    'error': 'bg-red-100 text-red-800',
                    'healthy': 'bg-green-100 text-green-800',
                    'offline': 'bg-red-100 text-red-800',
                    'online': 'bg-green-100 text-green-800',
                    'unknown': 'bg-gray-100 text-gray-800'
                };
                return classes[status] || classes['unknown'];
            }
        </script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <div>
                            <h1 class="text-2xl font-bold text-gray-900">Check Your Crypto</h1>
                            <p class="text-sm text-gray-600">Современная панель администратора</p>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="text-sm text-gray-600">Последнее обновление: <span id="last-updated">""" + context['last_updated'] + """</span></span>
                            <span class="text-sm text-gray-600">admin</span>
                            <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="px-4 py-6 sm:px-0">
                    
                    <!-- System Health Overview -->
                    <div class="mb-8">
                        <h2 class="text-lg font-semibold text-gray-900 mb-4">Состояние системы</h2>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-white rounded-lg shadow p-4">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium text-gray-600">Бот</span>
                                    <span id="bot-status" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium """ + bot_bg_color + " " + bot_text_color + """">
                                        """ + bot_status + """
                                    </span>
                                </div>
                            </div>
                            <div class="bg-white rounded-lg shadow p-4">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium text-gray-600">База данных</span>
                                    <span id="db-status" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium """ + db_bg_color + " " + db_text_color + """">
                                        """ + db_status + """
                                    </span>
                                </div>
                            </div>
                            <div class="bg-white rounded-lg shadow p-4">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium text-gray-600">API</span>
                                    <span id="api-status" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium """ + api_bg_color + " " + api_text_color + """">
                                        """ + api_status + """
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Key Metrics -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <!-- Users -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <div class="flex items-center">
                                <div class="p-3 bg-blue-100 rounded-lg">
                                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                                    </svg>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-600">Всего пользователей</p>
                                    <p id="total-users" class="text-2xl font-bold text-gray-900">{basic_stats['users']['total']}</p>
                                    <p class="text-sm text-green-600">+{basic_stats['users']['new_today']} сегодня</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Checks -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <div class="flex items-center">
                                <div class="p-3 bg-green-100 rounded-lg">
                                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-600">Всего проверок</p>
                                    <p id="total-checks" class="text-2xl font-bold text-gray-900">{basic_stats['checks']['total']}</p>
                                    <p class="text-sm text-green-600">+{basic_stats['checks']['today']} сегодня</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Revenue -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <div class="flex items-center">
                                <div class="p-3 bg-yellow-100 rounded-lg">
                                    <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                    </svg>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-600">Общий доход</p>
                                    <p id="total-revenue" class="text-2xl font-bold text-gray-900">${basic_stats['revenue']['total']:.2f}</p>
                                    <p class="text-sm text-green-600">+${basic_stats['revenue']['today']:.2f} сегодня</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Performance -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <div class="flex items-center">
                                <div class="p-3 bg-purple-100 rounded-lg">
                                    <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                    </svg>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-600">Время ответа</p>
                                    <p class="text-2xl font-bold {get_status_color(performance['response_time']['status'])}">{performance['response_time']['avg_ms']}ms</p>
                                    <p class="text-sm text-gray-600">Среднее</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Performance & Business Metrics -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                        <!-- Performance Metrics -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">Производительность</h3>
                            <div class="space-y-4">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Ошибки сегодня</span>
                                    <span class="text-sm font-medium {get_status_color(performance['errors']['status'])}">{performance['errors']['count_today']} ({performance['errors']['rate_percent']}%)</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">CPU</span>
                                    <span class="text-sm font-medium">{performance['system']['cpu_usage']}%</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Память</span>
                                    <span class="text-sm font-medium">{performance['system']['memory_usage']}%</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Диск</span>
                                    <span class="text-sm font-medium">{performance['system']['disk_usage']}%</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Аптайм</span>
                                    <span class="text-sm font-medium">{performance['system']['uptime_hours']:.1f}ч</span>
                                </div>
                            </div>
                        </div>

                        <!-- Business Metrics -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">Бизнес метрики</h3>
                            <div class="space-y-4">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Конверсия</span>
                                    <span class="text-sm font-medium {get_status_color('good' if business_metrics['conversion']['rate_percent'] > 5 else 'warning')}">{business_metrics['conversion']['rate_percent']}%</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">LTV</span>
                                    <span class="text-sm font-medium {get_status_color(business_metrics['ltv']['status'])}">${business_metrics['ltv']['avg_revenue_per_user']:.2f}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Churn Rate</span>
                                    <span class="text-sm font-medium {get_status_color(business_metrics['churn']['status'])}">{business_metrics['churn']['rate_percent']}%</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">ARPU</span>
                                    <span class="text-sm font-medium {get_status_color(business_metrics['arpu']['status'])}">${business_metrics['arpu']['value']:.2f}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Платящие пользователи</span>
                                    <span class="text-sm font-medium">{business_metrics['conversion']['paying_users']} / {business_metrics['conversion']['total_users']}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Alerts -->
                    {f'''
                    <div class="mb-8">
                        <h2 class="text-lg font-semibold text-gray-900 mb-4">Алерты</h2>
                        <div class="space-y-2">
                            {''.join([f'''
                            <div class="bg-{'red' if alert['severity'] == 'critical' else 'yellow'}-50 border border-{'red' if alert['severity'] == 'critical' else 'yellow'}-200 rounded-md p-4">
                                <div class="flex">
                                    <div class="flex-shrink-0">
                                        <svg class="h-5 w-5 text-{'red' if alert['severity'] == 'critical' else 'yellow'}-400" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <div class="ml-3">
                                        <p class="text-sm text-{'red' if alert['severity'] == 'critical' else 'yellow'}-800">{alert['message']}</p>
                                    </div>
                                </div>
                            </div>
                            ''' for alert in system_health['alerts']])}
                            {f'<p class="text-sm text-gray-600">Алертов нет</p>' if not system_health['alerts'] else ''}
                        </div>
                    </div>
                    '''}

                    <!-- Growth Rates -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-sm font-medium text-gray-600 mb-2">Рост пользователей</h3>
                            <p class="text-2xl font-bold {get_status_color('good' if basic_stats['users']['growth_rate'] > 0 else 'warning')}">{basic_stats['users']['growth_rate']}%</p>
                            <p class="text-sm text-gray-600">за неделю</p>
                        </div>
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-sm font-medium text-gray-600 mb-2">Рост проверок</h3>
                            <p class="text-2xl font-bold {get_status_color('good' if basic_stats['checks']['growth_rate'] > 0 else 'warning')}">{basic_stats['checks']['growth_rate']}%</p>
                            <p class="text-sm text-gray-600">за неделю</p>
                        </div>
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-sm font-medium text-gray-600 mb-2">Рост дохода</h3>
                            <p class="text-2xl font-bold {get_status_color('good' if basic_stats['revenue']['growth_rate'] > 0 else 'warning')}">{basic_stats['revenue']['growth_rate']}%</p>
                            <p class="text-sm text-gray-600">за неделю</p>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <a href="/api/panel/users/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                                </svg>
                                Пользователи
                            </a>
                            <a href="/api/panel/checks/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                Проверки
                            </a>
                            <a href="/api/panel/payments/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                </svg>
                                Платежи
                            </a>
                            <a href="/api/panel/settings/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                                Настройки
                            </a>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_fallback_dashboard_html(error: str) -> str:
    """Генерация fallback дашборда при ошибке"""
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Check Your Crypto - Ошибка дашборда</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center">
            <div class="max-w-md w-full bg-white rounded-lg shadow-md p-6">
                <div class="text-center">
                    <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">Ошибка загрузки дашборда</h3>
                    <p class="mt-1 text-sm text-gray-500">{error}</p>
                    <div class="mt-6">
                        <a href="/api/panel/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                            Попробовать снова
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
