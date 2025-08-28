"""
Views для админки Check Your Crypto
"""
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Добавляем импорты моделей по одному
from .models import User, Check, Payment, Text, Setting
from .admin_models import AdminUser, AdminActionLog, SystemMetrics, MassMessage, BotText, UserMessage


def format_date(date):
    """Форматирует дату для отображения"""
    if date:
        return date.strftime('%d.%m.%Y %H:%M')
    return 'Не указано'


def test_view(request):
    """Тестовый view для диагностики"""
    return HttpResponse("Тест работает!")

@csrf_exempt
def admin_login(request):
    """Вход в админку"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('/api/panel/')
        else:
            # Создаем страницу логина с ошибкой
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Вход в админку - Check Your Crypto</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                    <div class="max-w-md w-full space-y-8">
                        <div>
                            <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                                Вход в админку
                            </h2>
                            <p class="mt-2 text-center text-sm text-gray-600">
                                Check Your Crypto
                            </p>
                        </div>
                        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            Неверные учетные данные
                        </div>
                        <form class="mt-8 space-y-6" method="POST">
                            <div class="rounded-md shadow-sm -space-y-px">
                                <div>
                                    <label for="username" class="sr-only">Имя пользователя</label>
                                    <input id="username" name="username" type="text" required 
                                           class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" 
                                           placeholder="Имя пользователя">
                                </div>
                                <div>
                                    <label for="password" class="sr-only">Пароль</label>
                                    <input id="password" name="password" type="password" required 
                                           class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" 
                                           placeholder="Пароль">
                                </div>
                            </div>
                            <div>
                                <button type="submit" 
                                        class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    Войти
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html)
    
    # Создаем простую страницу логина прямо в коде
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Вход в админку - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div class="max-w-md w-full space-y-8">
                <div>
                    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Вход в админку
                    </h2>
                    <p class="mt-2 text-center text-sm text-gray-600">
                        Check Your Crypto
                    </p>
                </div>
                <form class="mt-8 space-y-6" method="POST">
                    <div class="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label for="username" class="sr-only">Имя пользователя</label>
                            <input id="username" name="username" type="text" required 
                                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" 
                                   placeholder="Имя пользователя">
                        </div>
                        <div>
                            <label for="password" class="sr-only">Пароль</label>
                            <input id="password" name="password" type="password" required 
                                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" 
                                   placeholder="Пароль">
                        </div>
                    </div>
                    <div>
                        <button type="submit" 
                                class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Войти
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

def admin_logout(request):
    """Выход из админки"""
    logout(request)
    return redirect('/api/panel/login/')


@login_required
def admin_dashboard(request):
    """Дашборд админки с реальными метриками и нормальными графиками"""
    try:
        # Получаем реальные данные из базы
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Пользователи
        total_users = User.objects.count()
        new_users_today = User.objects.filter(created_at__date=today).count()
        new_users_week = User.objects.filter(created_at__gte=week_ago).count()
        active_users_week = User.objects.filter(updated_at__gte=week_ago).count()
        
        # Проверки
        total_checks = Check.objects.count()
        checks_today = Check.objects.filter(created_at__date=today).count()
        checks_week = Check.objects.filter(created_at__gte=week_ago).count()
        
        # Финансы
        total_revenue = Payment.objects.filter(status='COMPLETED').aggregate(
            total=Sum('amount'))['total'] or 0
        revenue_today = Payment.objects.filter(
            status='COMPLETED', created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_week = Payment.objects.filter(
            status='COMPLETED', created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Средние значения
        avg_check_amount = Payment.objects.filter(status='COMPLETED').aggregate(
            avg=Sum('amount') / Count('id'))['avg'] or 0
        
        # Данные для графиков (последние 7 дней)
        chart_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            users_count = User.objects.filter(created_at__date=date).count()
            checks_count = Check.objects.filter(created_at__date=date).count()
            revenue_amount = Payment.objects.filter(
                status='COMPLETED', created_at__date=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            chart_data.append({
                'date': date.strftime('%d.%m'),
                'users': users_count,
                'checks': checks_count,
                'revenue': float(revenue_amount)
            })
        
        chart_data.reverse()  # От старых к новым
        
    except Exception as e:
        # Если есть ошибка, используем нулевые значения
        total_users = 0
        new_users_today = 0
        active_users_week = 0
        checks_today = 0
        checks_week = 0
        revenue_today = 0
        revenue_week = 0
        total_revenue = 0
        avg_check_amount = 0
        chart_data = []
    
    # Подготавливаем данные для графиков в JSON формате
    import json
    chart_labels = json.dumps([item['date'] for item in chart_data])
    chart_users = json.dumps([item['users'] for item in chart_data])
    chart_checks = json.dumps([item['checks'] for item in chart_data])
    chart_revenue = json.dumps([item['revenue'] for item in chart_data])
    
    # Используем Django Template Engine для дашборда
    from django.template.loader import render_to_string
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'active_users_week': active_users_week,
        'total_checks': total_checks,
        'checks_today': checks_today,
        'checks_week': checks_week,
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'avg_check_amount': avg_check_amount,
        'chart_labels': chart_labels,
        'chart_users': chart_users,
        'chart_checks': chart_checks,
        'chart_revenue': chart_revenue,
        'now': now,
    }
    
    html = render_to_string('admin_app/panel/dashboard.html', context, request=request)
    return HttpResponse(html)



@login_required
def admin_users(request):
    """Управление пользователями"""
    try:
        # Получаем список пользователей с пагинацией
        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        
        users = User.objects.all().order_by('-created_at')
        
        if search:
            users = users.filter(
                Q(tg_id__icontains=search) |
                Q(language__icontains=search)
            )
        
        # Простая пагинация
        per_page = 20
        start = (int(page) - 1) * per_page
        end = start + per_page
        users_page = users[start:end]
        total_pages = (users.count() + per_page - 1) // per_page
        
        # Если нет пользователей, показываем заглушку
        if users.count() == 0:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Управление пользователями - Check Your Crypto</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen">
                    <!-- Header -->
                    <header class="bg-white shadow-sm border-b border-gray-200">
                        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div class="flex justify-between items-center py-6">
                                <div>
                                    <h1 class="text-2xl font-bold text-gray-900">Check Your Crypto</h1>
                                    <p class="text-sm text-gray-600">Панель администратора</p>
                                </div>
                                <div class="flex items-center space-x-4">
                                    <a href="/api/panel/" class="text-sm text-blue-600 hover:text-blue-800">Дашборд</a>
                                    <span class="text-sm text-gray-600">admin</span>
                                    <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                                </div>
                            </div>
                        </div>
                    </header>

                    <!-- Main Content -->
                    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                        <div class="px-4 py-6 sm:px-0">
                            <div class="flex justify-between items-center mb-8">
                                <h2 class="text-3xl font-bold text-gray-900">Управление пользователями</h2>
                                <div class="flex space-x-4">
                                    <form method="get" class="flex">
                                        <input type="text" name="search" value="{search}" placeholder="Поиск пользователей..." 
                                               class="px-4 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                        <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700">
                                            Поиск
                                        </button>
                                    </form>
                                </div>
                            </div>
                            
                            <!-- CSRF Token -->
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                            
                            <!-- Users Table -->
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Язык</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Баланс</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата регистрации</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            <tr class="hover:bg-gray-50">
                                                <td class="px-6 py-4 text-center text-sm text-gray-500" colspan="6">
                                                    Пользователей пока нет в базе данных. Возможно, бот еще не использовался или данные находятся в другой базе.
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html)
        
    except Exception as e:
        # Если есть ошибка, показываем упрощенную версию
        users_page = []
        total_pages = 1
        search = ''
        page = 1
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Управление пользователями - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <div>
                            <h1 class="text-2xl font-bold text-gray-900">Check Your Crypto</h1>
                            <p class="text-sm text-gray-600">Панель администратора</p>
                        </div>
                        <div class="flex items-center space-x-4">
                            <a href="/api/panel/" class="text-sm text-blue-600 hover:text-blue-800">Дашборд</a>
                            <span class="text-sm text-gray-600">admin</span>
                            <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="px-4 py-6 sm:px-0">
                    <div class="flex justify-between items-center mb-8">
                        <h2 class="text-3xl font-bold text-gray-900">Управление пользователями</h2>
                        <div class="flex space-x-4">
                            <form method="get" class="flex">
                                <input type="text" name="search" value="{search}" placeholder="Поиск пользователей..." 
                                       class="px-4 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700">
                                    Поиск
                                </button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- CSRF Token -->
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                    
                    <!-- Users Table -->
                    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telegram ID</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Язык</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Баланс</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата регистрации</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
    """
    
    for user in users_page:
                        html += f"""
                                    <tr class="hover:bg-gray-50">
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.tg_id}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.username or 'Не указан'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.language}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${user.balance:.2f}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.created_at.strftime('%d.%m.%Y %H:%M')}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <a href="/api/panel/users/{user.tg_id}/" class="text-blue-600 hover:text-blue-900">Просмотр</a>
                                        </td>
                                    </tr>
                """
    
    html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Pagination -->
                    <div class="mt-6 flex justify-center">
                        <nav class="flex space-x-2">
    """
    
    for p in range(1, total_pages + 1):
        active_class = "bg-blue-600 text-white" if p == int(page) else "bg-white text-gray-700 hover:bg-gray-50"
        html += f'<a href="?page={p}&search={search}" class="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium {active_class}">{p}</a>'
    
    html += """
                        </nav>
                    </div>
                </div>
            </main>
        </div>
        

    </body>
    </html>
    """
    return HttpResponse(html)


@login_required
def admin_user_detail(request, user_id):
    """Детали пользователя с полной функциональностью"""
    
    try:
        print(f"DEBUG: Начинаем загрузку пользователя {user_id}")
        
        # Получаем пользователя
        user = User.objects.get(tg_id=user_id)
        print(f"DEBUG: Пользователь найден: {user.tg_id}")
        
        # Получаем данные пользователя с обработкой ошибок
        try:
            # Проверки пользователя - ограничиваем до 5 для быстрой загрузки
            print(f"DEBUG: Начинаем запрос проверок для пользователя {user.tg_id}")
            # Сначала получаем базовые данные без JSONField
            checks_data = Check.objects.filter(user=user).values(
                'id', 'address', 'chain', 'type', 'created_at'
            ).order_by('-created_at')[:5]
            
            # Преобразуем в список для обработки
            checks = list(checks_data)
            print(f"DEBUG: Проверки загружены, количество: {len(checks)}")
            total_checks = Check.objects.filter(user=user).count()
            print(f"DEBUG: Найдено проверок: {total_checks}, загружаем: {len(checks)}")
        except Exception as e:
            print(f"DEBUG: Ошибка при получении проверок: {e}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            checks = []
            total_checks = 0
            
        try:
            # Платежи пользователя - ограничиваем до 5 для быстрой загрузки
            payments = Payment.objects.filter(user=user).order_by('-created_at')[:5]
            total_payments = Payment.objects.filter(user=user).count()
            # Упрощаем подсчет потраченного - без сложных фильтров
            total_spent = 0
            print(f"DEBUG: Найдено платежей: {total_payments}, загружаем: {len(payments)}")
        except Exception as e:
            print(f"DEBUG: Ошибка при получении платежей: {e}")
            payments = []
            total_payments = 0
            total_spent = 0
            
        try:
            # Сообщения пользователя - ограничиваем до 5 для быстрой загрузки
            messages = UserMessage.objects.filter(user_id=user_id).order_by('-created_at')[:5]
            total_messages = UserMessage.objects.filter(user_id=user_id).count()
            print(f"DEBUG: Найдено сообщений: {total_messages}, загружаем: {len(messages)}")
        except Exception as e:
            print(f"DEBUG: Ошибка при получении сообщений: {e}")
            messages = []
            total_messages = 0
            
        try:
            # Действия администраторов с этим пользователем - ограничиваем до 5 для быстрой загрузки
            admin_actions = AdminActionLog.objects.filter(target_user_id=user_id).order_by('-created_at')[:5]
            total_actions = AdminActionLog.objects.filter(target_user_id=user_id).count()
            print(f"DEBUG: Найдено действий: {total_actions}, загружаем: {len(admin_actions)}")
        except Exception as e:
            print(f"DEBUG: Ошибка при получении действий: {e}")
            admin_actions = []
            total_actions = 0
        
        # Используем Django Template Engine
        from django.template.loader import render_to_string
        
        context = {
            'user': user,
            'checks': checks,
            'payments': payments,
            'messages': messages,
            'admin_actions': admin_actions,
            'total_checks': total_checks,
            'total_payments': total_payments,
            'total_messages': total_messages,
            'total_actions': total_actions,
        }
        
        html = render_to_string('admin_app/panel/user_detail.html', context, request=request)
        return HttpResponse(html)
            
        # Генерируем HTML для таблиц
        def generate_checks_html():
            print(f"DEBUG: Начинаем генерацию HTML для проверок, количество: {len(checks)}")
            if not checks:
                return '<tr><td colspan="6" class="px-4 py-4 text-center text-gray-500">Нет проверок</td></tr>'
            
            html = ''
            for i, check in enumerate(checks):
                print(f"DEBUG: Обрабатываем проверку {i+1}/{len(checks)}, ID: {check['id']}")
                
                # Пока что показываем базовую информацию без result
                risk_level = 'Не определен'
                risk_score = 'N/A'
                risk_color = 'text-gray-600'
                
                # Тип проверки с иконкой (исправляем регистр)
                check_type_icon = '🆓' if check['type'].upper() == 'FREE' else '💰'
                check_type_text = 'Базовая' if check['type'].upper() == 'FREE' else 'Глубокий AI'
                
                # Сокращаем адрес для отображения
                address_display = check['address']
                if len(address_display) > 25:
                    address_display = address_display[:12] + '...' + address_display[-12:]
                
                html += f'''
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-4 text-sm text-gray-900 font-mono">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs text-gray-400">{check['chain'].upper()}</span>
                            <span>{address_display}</span>
                        </div>
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-900">
                        <div class="flex items-center space-x-1">
                            <span>{check_type_icon}</span>
                            <span>{check_type_text}</span>
                        </div>
                    </td>
                    <td class="px-4 py-4 text-sm {risk_color} font-medium">
                        {risk_level.upper()}
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-600">
                        {risk_score}
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-500">
                        {format_date(check['created_at'])}
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-500">
                        <button onclick="viewCheckDetails({check['id']})" 
                                class="text-blue-600 hover:text-blue-800 text-xs">
                            Детали
                        </button>
                    </td>
                </tr>
                '''
            return html
            
        def generate_payments_html():
            if not payments:
                return '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Нет платежей</td></tr>'
            
            html = ''
            for payment in payments:
                status_color = {
                    'completed': 'text-green-600',
                    'pending': 'text-yellow-600',
                    'failed': 'text-red-600'
                }.get(payment.status, 'text-gray-600')
                
                html += f'''
                <tr>
                    <td class="px-4 py-4 text-sm text-gray-900">{payment.id}</td>
                    <td class="px-4 py-4 text-sm text-gray-900">${payment.amount}</td>
                    <td class="px-4 py-4 text-sm {status_color}">{payment.status}</td>
                    <td class="px-4 py-4 text-sm text-gray-500">{format_date(payment.created_at)}</td>
                </tr>
                '''
            return html
            
        def generate_messages_html():
            if not messages:
                return '<tr><td colspan="5" class="px-4 py-4 text-center text-gray-500">Нет сообщений</td></tr>'
            
            html = ''
            for message in messages:
                # Статус с цветом
                status_colors = {
                    'pending': 'text-yellow-600',
                    'sent': 'text-blue-600',
                    'delivered': 'text-green-600',
                    'read': 'text-green-700',
                    'failed': 'text-red-600'
                }
                status_color = status_colors.get(message.status, 'text-gray-600')
                
                # Иконка типа сообщения
                type_icons = {
                    'personal': '👤',
                    'mass': '📢',
                    'system': '⚙️',
                    'support': '🆘'
                }
                type_icon = type_icons.get(message.message_type, '📨')
                
                # Сокращаем контент
                content_preview = message.content
                if len(content_preview) > 60:
                    content_preview = content_preview[:60] + '...'
                
                html += f'''
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-4 text-sm text-gray-900">
                        <div class="flex items-center space-x-2">
                            <span>{type_icon}</span>
                            <span>{message.subject or 'Без темы'}</span>
                        </div>
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-900">
                        <div class="max-w-xs truncate" title="{message.content}">
                            {content_preview}
                        </div>
                    </td>
                    <td class="px-4 py-4 text-sm {status_color} font-medium">
                        {message.get_status_display()}
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-500">
                        {format_date(message.created_at)}
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-500">
                        <button onclick="viewMessageDetails({message.id})" 
                                class="text-blue-600 hover:text-blue-800 text-xs">
                            Детали
                        </button>
                    </td>
                </tr>
                '''
            return html
            
        def generate_actions_html():
            if not admin_actions:
                return '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Нет действий</td></tr>'
            
            html = ''
            for action in admin_actions:
                html += f'''
                <tr>
                    <td class="px-4 py-4 text-sm text-gray-900">{action.admin.username if action.admin else 'Система'}</td>
                    <td class="px-4 py-4 text-sm text-gray-900">{action.get_action_type_display()}</td>
                    <td class="px-4 py-4 text-sm text-gray-900">{action.description}</td>
                    <td class="px-4 py-4 text-sm text-gray-500">{format_date(action.created_at)}</td>
                </tr>
                '''
            return html
            
        # Генерируем HTML для всех таблиц
        print("DEBUG: Генерируем HTML для таблиц...")
        try:
            checks_html = generate_checks_html()
            print("DEBUG: HTML для проверок сгенерирован")
        except Exception as e:
            print(f"DEBUG: Ошибка при генерации HTML проверок: {e}")
            checks_html = '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Ошибка загрузки</td></tr>'
            
        try:
            payments_html = generate_payments_html()
            print("DEBUG: HTML для платежей сгенерирован")
        except Exception as e:
            print(f"DEBUG: Ошибка при генерации HTML платежей: {e}")
            payments_html = '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Ошибка загрузки</td></tr>'
            
        try:
            messages_html = generate_messages_html()
            print("DEBUG: HTML для сообщений сгенерирован")
        except Exception as e:
            print(f"DEBUG: Ошибка при генерации HTML сообщений: {e}")
            messages_html = '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Ошибка загрузки</td></tr>'
            
        try:
            actions_html = generate_actions_html()
            print("DEBUG: HTML для действий сгенерирован")
        except Exception as e:
            print(f"DEBUG: Ошибка при генерации HTML действий: {e}")
            actions_html = '<tr><td colspan="4" class="px-4 py-4 text-center text-gray-500">Ошибка загрузки</td></tr>'
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Профиль пользователя {user.tg_id} - Check Your Crypto</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="min-h-screen">
                <!-- Header -->
                <header class="bg-white shadow-sm border-b border-gray-200">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div class="flex justify-between items-center py-6">
                            <div>
                                <h1 class="text-2xl font-bold text-gray-900">Check Your Crypto</h1>
                                <p class="text-sm text-gray-600">Панель администратора</p>
                            </div>
                            <div class="flex items-center space-x-4">
                                <a href="/api/panel/" class="text-sm text-blue-600 hover:text-blue-800">Дашборд</a>
                                <a href="/api/panel/users/" class="text-sm text-blue-600 hover:text-blue-800">Пользователи</a>
                                <span class="text-sm text-gray-600">admin</span>
                                <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                            </div>
                        </div>
                    </div>
                </header>

                <!-- Main Content -->
                <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    <div class="px-4 py-6 sm:px-0">
                        <!-- User Header -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h2 class="text-3xl font-bold text-gray-900">Пользователь {user.tg_id}</h2>
                                    <p class="text-sm text-gray-600 mt-1">Зарегистрирован: {format_date(user.created_at)}</p>
                                </div>
                                                                                <div class="flex space-x-3">
                                                    <button onclick="changeBalance({user.tg_id})" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                                        Изменить баланс
                                                    </button>
                                                    <button onclick="openMessageModal({user.tg_id})" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                                                        Отправить сообщение
                                                    </button>
                                                    {f'<button onclick="unblockUser({user.tg_id})" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Разблокировать</button>' if user.is_blocked else f'<button onclick="blockUser({user.tg_id})" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">Заблокировать</button>'}
                                                </div>
                            </div>
                        </div>

                        <!-- Basic Info -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">Основная информация</h3>
                            <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Telegram ID</dt>
                                    <dd class="text-sm text-gray-900">{user.tg_id}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Username</dt>
                                    <dd class="text-sm text-gray-900">{user.username or 'Не указан'}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Язык</dt>
                                    <dd class="text-sm text-gray-900">{user.language.upper()}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Баланс</dt>
                                    <dd class="text-sm text-gray-900">${user.balance}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Реферальный код</dt>
                                    <dd class="text-sm text-gray-900">{user.referral_code or 'Не указан'}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Реферер</dt>
                                    <dd class="text-sm text-gray-900">{user.referrer_id or 'Нет'}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Дата регистрации</dt>
                                    <dd class="text-sm text-gray-900">{format_date(user.created_at)}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Последнее обновление</dt>
                                    <dd class="text-sm text-gray-900">{format_date(user.updated_at)}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Статус</dt>
                                    <dd class="text-sm {f'text-red-600 font-medium' if user.is_blocked else 'text-green-600 font-medium'}">{'🚫 Заблокирован' if user.is_blocked else '✅ Активен'}</dd>
                                </div>
                            </dl>
                        </div>

                        <!-- Quick Stats -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div class="flex items-center">
                                    <div class="p-3 bg-green-100 rounded-lg">
                                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                    <div class="ml-4">
                                        <p class="text-sm font-medium text-gray-600">Проверок</p>
                                        <p class="text-2xl font-bold text-gray-900">{total_checks}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div class="flex items-center">
                                    <div class="p-3 bg-purple-100 rounded-lg">
                                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
                                        </svg>
                                    </div>
                                    <div class="ml-4">
                                        <p class="text-sm font-medium text-gray-600">Платежей</p>
                                        <p class="text-2xl font-bold text-gray-900">{total_payments}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div class="flex items-center">
                                    <div class="p-3 bg-yellow-100 rounded-lg">
                                        <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                                        </svg>
                                    </div>
                                    <div class="ml-4">
                                        <p class="text-sm font-medium text-gray-600">Сообщений</p>
                                        <p class="text-2xl font-bold text-gray-900">{total_messages}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- History Tabs -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 mt-6">
                            <div class="border-b border-gray-200">
                                <nav class="flex space-x-8 px-6">
                                    <button onclick="showTab('checks')" class="py-4 px-1 border-b-2 border-blue-500 text-blue-600 font-medium text-sm">
                                        Проверки ({total_checks})
                                    </button>
                                    <button onclick="showTab('payments')" class="py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm">
                                        Платежи ({total_payments})
                                    </button>
                                    <button onclick="showTab('messages')" class="py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm">
                                        Сообщения ({total_messages})
                                    </button>
                                    <button onclick="showTab('activity')" class="py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm">
                                        Активность
                                    </button>
                                </nav>
                            </div>

                            <!-- Checks Tab -->
                            <div id="checks-tab" class="p-6">
                                <h3 class="text-lg font-medium text-gray-900 mb-4">Последние проверки</h3>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Адрес / Сеть</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Тип проверки</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Уровень риска</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Счетчик</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {checks_html}
                                        </tbody>
                                    </table>
                                    {f'<div class="mt-4 text-center"><button onclick="loadMoreChecks({user.tg_id})" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Показать больше проверок ({total_checks - 5} еще)</button></div>' if total_checks > 5 and checks else ''}
                                </div>
                            </div>

                            <!-- Payments Tab -->
                            <div id="payments-tab" class="p-6 hidden">
                                <h3 class="text-lg font-medium text-gray-900 mb-4">Последние платежи</h3>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID платежа</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сумма</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {payments_html}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- Messages Tab -->
                            <div id="messages-tab" class="p-6 hidden">
                                <h3 class="text-lg font-medium text-gray-900 mb-4">История сообщений</h3>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Тема / Тип</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Содержание</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {messages_html}
                                        </tbody>
                                    </table>
                                    {f'<div class="mt-4 text-center"><button onclick="loadMoreMessages({user.tg_id})" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Показать больше сообщений ({total_messages - 5} еще)</button></div>' if total_messages > 5 else ''}
                                </div>
                            </div>

                            <!-- Activity Tab -->
                            <div id="activity-tab" class="p-6 hidden">
                                <h3 class="text-lg font-medium text-gray-900 mb-4">Действия администраторов</h3>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Администратор</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действие</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Описание</th>
                                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {actions_html}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>

                                        <!-- CSRF Token -->
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">

                            <!-- Message Modal -->
                            <div id="messageModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full hidden z-50">
                                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                                    <div class="mt-3">
                                        <div class="flex items-center justify-between mb-4">
                                            <h3 class="text-lg font-medium text-gray-900">Отправить сообщение</h3>
                                            <button onclick="closeMessageModal()" class="text-gray-400 hover:text-gray-600">
                                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                                </svg>
                                            </button>
                                        </div>
                                        
                                        <form id="messageForm" class="space-y-4">
                                            <div>
                                                <label for="messageSubject" class="block text-sm font-medium text-gray-700 mb-1">
                                                    Тема сообщения
                                                </label>
                                                <input type="text" id="messageSubject" name="subject" 
                                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                       placeholder="Введите тему сообщения (необязательно)">
                                            </div>
                                            
                                            <div>
                                                <label for="messageContent" class="block text-sm font-medium text-gray-700 mb-1">
                                                    Текст сообщения <span class="text-red-500">*</span>
                                                </label>
                                                <textarea id="messageContent" name="content" rows="4" required
                                                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                          placeholder="Введите текст сообщения..."></textarea>
                                            </div>
                                            
                                            <div class="flex justify-end space-x-3 pt-4">
                                                <button type="button" onclick="closeMessageModal()" 
                                                        class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500">
                                                    Отмена
                                                </button>
                                                <button type="submit" id="sendMessageBtn"
                                                        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    Отправить
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>

                            <script>
            function changeBalance(userId) {
                const newBalance = prompt(`Введите новый баланс для пользователя ${{userId}}:`);
                if (newBalance !== null && !isNaN(newBalance)) {
                    if (confirm(`Изменить баланс пользователя ${{userId}} на $` + newBalance + `?`)) {
                        fetch(`/api/panel/users/${{userId}}/balance/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                            },
                            body: JSON.stringify({
                                balance: parseFloat(newBalance)
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                alert(data.message);
                                location.reload();
                            } else {
                                alert('Ошибка: ' + data.message);
                            }
                        })
                        .catch(error => {
                            console.error('Ошибка:', error);
                            alert('Произошла ошибка при изменении баланса: ' + error.message);
                        });
                    }
                }
            }

            function blockUser(userId) {
                if (confirm(`Заблокировать пользователя ${{userId}}? Пользователь не сможет использовать бота.`)) {
                    fetch(`/api/panel/users/${{userId}}/block/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('✅ ' + data.message);
                            location.reload();
                        } else {
                            alert('❌ Ошибка: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        alert('❌ Произошла ошибка при блокировке: ' + error.message);
                    });
                }
            }

            function unblockUser(userId) {
                if (confirm(`Разблокировать пользователя ${{userId}}? Пользователь снова сможет использовать бота.`)) {
                    fetch(`/api/panel/users/${{userId}}/unblock/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('✅ ' + data.message);
                            location.reload();
                        } else {
                            alert('❌ Ошибка: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        alert('❌ Произошла ошибка при разблокировке: ' + error.message);
                    });
                }
            }

            let currentUserId = null;

            function openMessageModal(userId) {
                currentUserId = userId;
                document.getElementById('messageModal').classList.remove('hidden');
                document.getElementById('messageForm').reset();
            }

            function closeMessageModal() {
                document.getElementById('messageModal').classList.add('hidden');
                currentUserId = null;
            }

            // Обработчик отправки формы
            document.getElementById('messageForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const subject = document.getElementById('messageSubject').value;
                const content = document.getElementById('messageContent').value;
                const sendBtn = document.getElementById('sendMessageBtn');
                
                if (!content.trim()) {
                    alert('Текст сообщения не может быть пустым');
                    return;
                }
                
                // Показываем состояние загрузки
                sendBtn.disabled = true;
                sendBtn.textContent = 'Отправка...';
                
                fetch(`/api/panel/users/${{currentUserId}}/message/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                    },
                    body: JSON.stringify({
                        subject: subject,
                        content: content
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('✅ Сообщение отправлено успешно!');
                        closeMessageModal();
                        location.reload();
                    } else {
                        alert('❌ Ошибка: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    alert('❌ Произошла ошибка при отправке сообщения: ' + error.message);
                })
                .finally(() => {
                    // Восстанавливаем кнопку
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Отправить';
                });
            });

            // Закрытие модального окна при клике вне его
            document.getElementById('messageModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    closeMessageModal();
                }
            });

            function viewCheckDetails(checkId) {
                // Показываем детали проверки в модальном окне
                alert('Просмотр деталей проверки ' + checkId + '. В будущем здесь будет модальное окно с полной информацией.');
            }

            function viewMessageDetails(messageId) {
                // Показываем детали сообщения
                alert('Просмотр деталей сообщения ' + messageId + '. В будущем здесь будет модальное окно с полной информацией.');
            }

            function loadMoreChecks(userId) {
                // Загружаем больше проверок
                alert('Загрузка дополнительных проверок для пользователя ' + userId + '. В будущем здесь будет AJAX запрос.');
            }

            function loadMoreMessages(userId) {
                // Загружаем больше сообщений
                alert('Загрузка дополнительных сообщений для пользователя ' + userId + '. В будущем здесь будет AJAX запрос.');
            }

            function showTab(tabName) {
                // Скрываем все вкладки
                document.getElementById('checks-tab').classList.add('hidden');
                document.getElementById('payments-tab').classList.add('hidden');
                document.getElementById('messages-tab').classList.add('hidden');
                document.getElementById('activity-tab').classList.add('hidden');
                
                // Убираем активные стили со всех кнопок
                const buttons = document.querySelectorAll('nav button');
                buttons.forEach(btn => {
                    btn.classList.remove('border-blue-500', 'text-blue-600');
                    btn.classList.add('border-transparent', 'text-gray-500');
                });
                
                // Показываем нужную вкладку
                document.getElementById(tabName + '-tab').classList.remove('hidden');
                
                // Добавляем активные стили к кнопке
                const activeButton = document.querySelector(`button[onclick="showTab('${{tabName}}')"]`);
                activeButton.classList.remove('border-transparent', 'text-gray-500');
                activeButton.classList.add('border-blue-500', 'text-blue-600');
            }
            </script>
        </body>
        </html>
        """.format(
            user=user,
            total_checks=total_checks,
            total_payments=total_payments,
            total_messages=total_messages,
            total_actions=total_actions,
            checks_html=checks_html,
            payments_html=payments_html,
            messages_html=messages_html,
            actions_html=actions_html,
            format_date=format_date
        )
        
        print(f"DEBUG: HTML сгенерирован успешно, размер: {len(html)} символов")
        return HttpResponse(html)
        
    except User.DoesNotExist:
        return HttpResponse("Пользователь не найден", status=404)
    except Exception as e:
        print(f"DEBUG: Ошибка в admin_user_detail: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return HttpResponse(f"Ошибка при загрузке данных: {str(e)}", status=500)


@login_required
@require_http_methods(["POST"])
def admin_user_block(request, user_id):
    """Блокировка пользователя"""
    user = get_object_or_404(User, tg_id=user_id)
    user.is_blocked = True
    user.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='user_block',
        description=f'Блокировка пользователя {user.tg_id}',
        target_user_id=user.tg_id
    )
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["POST"])
def admin_user_unblock(request, user_id):
    """Разблокировка пользователя"""
    user = get_object_or_404(User, tg_id=user_id)
    user.is_blocked = False
    user.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='user_unblock',
        description=f'Разблокировка пользователя {user.tg_id}',
        target_user_id=user.tg_id
    )
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["POST"])
def admin_balance_change(request, user_id):
    """Изменение баланса пользователя"""
    user = get_object_or_404(User, tg_id=user_id)
    amount = float(request.POST.get('amount', 0))
    
    user.balance += amount
    user.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='balance_change',
        description=f'Изменение баланса пользователя {user.tg_id} на {amount}',
        target_user_id=user.tg_id
    )
    
    return JsonResponse({'status': 'success', 'new_balance': float(user.balance)})


@login_required
def admin_messages(request):
    """Страница массовых сообщений"""
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    # Получаем все сообщения
    messages = MassMessage.objects.all().order_by('-created_at')
    
    # Подсчитываем статистику
    total_messages = messages.count()
    sent_messages = messages.filter(status='COMPLETED').count()
    scheduled_messages = messages.filter(status='SCHEDULED').count()
    
    # Используем Django Template Engine
    from django.template.loader import render_to_string
    
    context = {
        'messages': messages,
        'total_messages': total_messages,
        'sent_messages': sent_messages,
        'scheduled_messages': scheduled_messages,
    }
    
    html = render_to_string('admin_app/panel/messages.html', context, request=request)
    return HttpResponse(html)


@login_required
def admin_texts(request):
    """Управление многоязычными текстами бота"""
    import json
    
    # Автоматически импортируем тексты из бота при первом открытии
    try:
        from .text_importer import TextImporter
        from .models import BotText
        # Импортируем тексты только если их нет
        if not BotText.objects.exists():
            TextImporter.import_all_texts()
    except Exception as e:
        print(f"Ошибка автоматического импорта текстов: {e}")
    
    # Получаем все тексты из базы данных
    all_texts = {}
    categories = ['welcome', 'main_menu', 'check', 'check_choice', 'check_result', 'payment', 'error', 'help', 'settings', 'insufficient_balance', 'user_blocked']
    
    for category in categories:
        category_texts = BotText.objects.filter(category=category, is_active=True)
        all_texts[category] = {}
        for text in category_texts:
            all_texts[category][text.language] = text.content
    
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Управление текстами - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/ace.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/mode-text.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/theme-chrome.js"></script>
        <meta name="csrf-token" content="""" + csrf_token + """">
                        <script>
                    // Передаем данные текстов прямо в JavaScript
                    window.allTextsData = """ + json.dumps(all_texts, ensure_ascii=False) + """;
                    console.log('=== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ===');
                    console.log('Загруженные тексты:', window.allTextsData);
                    console.log('Тип данных:', typeof window.allTextsData);
                    console.log('Доступные категории:', Object.keys(window.allTextsData || {}));
                    console.log('Тексты welcome:', window.allTextsData?.welcome);
                    
                    // Проверяем загрузку Ace.js
                    window.addEventListener('load', function() {
                        console.log('=== ПРОВЕРКА ACE.JS ===');
                        console.log('typeof ace:', typeof ace);
                        if (typeof ace !== 'undefined') {
                            console.log('✅ Ace.js загружен успешно!');
                        } else {
                            console.log('❌ Ace.js НЕ загружен!');
                        }
                    });
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
                            <p class="text-sm text-gray-600">Панель администратора</p>
                        </div>
                        <div class="flex items-center space-x-4">
                            <a href="/api/panel/" class="text-sm text-blue-600 hover:text-blue-800">Дашборд</a>
                            <a href="/api/panel/users/" class="text-sm text-blue-600 hover:text-blue-800">Пользователи</a>
                            <a href="/api/panel/messages/" class="text-sm text-blue-600 hover:text-blue-800">Сообщения</a>
                            <span class="text-sm text-gray-600">admin</span>
                            <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="px-4 py-6 sm:px-0">
                    <!-- Header Controls -->
                    <div class="flex justify-between items-center mb-8">
                        <div>
                            <h2 class="text-3xl font-bold text-gray-900">Управление текстами</h2>
                            <p class="text-sm text-gray-600 mt-2">Выберите категорию для редактирования текстов на всех языках</p>
                        </div>
                        <div class="flex space-x-4">
                            <button onclick="saveAllTexts()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                                💾 Сохранить все
                            </button>
                        </div>
                    </div>
                    
                    <!-- Text Editor -->
                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <!-- Text Categories Sidebar -->
                        <div class="lg:col-span-1">
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 class="text-lg font-semibold text-gray-900 mb-4">Категории текстов</h3>
                                <div class="space-y-2">
                                    <button onclick="loadCategory('welcome')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        👋 Приветственные
                                    </button>
                                    <button onclick="loadCategory('main_menu')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        🏠 Главное меню
                                    </button>
                                    <button onclick="loadCategory('check')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        🔍 Проверки
                                    </button>
                                    <button onclick="loadCategory('check_choice')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        ⚡ Выбор проверки
                                    </button>
                                    <button onclick="loadCategory('check_result')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        📊 Результат проверки
                                    </button>
                                    <button onclick="loadCategory('payment')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        💰 Платежи
                                    </button>
                                    <button onclick="loadCategory('error')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        ❌ Ошибки
                                    </button>
                                    <button onclick="loadCategory('help')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        ❓ Помощь
                                    </button>
                                    <button onclick="loadCategory('settings')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        ⚙️ Настройки
                                    </button>
                                    <button onclick="loadCategory('insufficient_balance')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        💳 Недостаточно средств
                                    </button>
                                    <button onclick="loadCategory('user_blocked')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        🚫 Блокировка
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Editor Area -->
                        <div class="lg:col-span-3">
                            <div id="editorContainer" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div class="text-center">
                                    <div class="text-6xl mb-4">📝</div>
                                    <h3 class="text-xl font-semibold text-gray-900 mb-2">Редактирование текстов</h3>
                                    <p class="text-gray-600 mb-6">
                                        Выберите категорию текста слева для начала редактирования.<br>
                                        Тексты автоматически импортируются из бота.
                                    </p>
                                    <div class="bg-blue-50 rounded-lg p-4">
                                        <h4 class="font-medium text-blue-900 mb-2">💡 Как использовать:</h4>
                                        <ul class="text-sm text-blue-700 space-y-1">
                                            <li>• Кликните на любую категорию слева</li>
                                            <li>• Редактируйте тексты на всех языках</li>
                                            <li>• Сохраняйте изменения индивидуально или все сразу</li>
                                            <li>• Используйте кнопку "Импорт из бота" для обновления</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <script>
        let editors = {};
        let currentCategory = '';
        let textsData = {};

        function loadCategory(category) {
            console.log('=== НАЧАЛО loadCategory ===');
            console.log('Категория:', category);
            console.log('window.allTextsData:', window.allTextsData);
            
            currentCategory = category;
            
            // Показываем загрузку
            const container = document.getElementById('editorContainer');
            if (!container) {
                console.error('Элемент editorContainer не найден!');
                return;
            }
            
            container.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p class="text-gray-600">Загрузка текстов...</p>
                </div>
            `;
            
            // Используем данные из window.allTextsData
            setTimeout(() => {
                console.log('=== ПРОВЕРКА ДАННЫХ ===');
                console.log('Загружаем категорию:', category);
                console.log('window.allTextsData:', window.allTextsData);
                console.log('Тип window.allTextsData:', typeof window.allTextsData);
                
                if (window.allTextsData && window.allTextsData[category]) {
                    textsData = window.allTextsData[category];
                    const languages = Object.keys(textsData);
                    console.log('Найдены языки:', languages);
                    console.log('Тексты:', textsData);
                    console.log('Тип textsData:', typeof textsData);
                    renderLanguageBlocks(languages, textsData);
                } else {
                    console.log('Тексты не найдены для категории:', category);
                    console.log('Проверяем все категории:', Object.keys(window.allTextsData || {}));
                    showNotification('❌ Тексты для категории ' + category + ' не найдены', 'error');
                }
            }, 100);
        }

        function renderLanguageBlocks(languages, texts) {
            const container = document.getElementById('editorContainer');
            container.innerHTML = '';

            languages.forEach(langCode => {
                const langName = getLanguageName(langCode);
                const langFlag = getLanguageFlag(langCode);
                const text = texts[langCode] || '';
                
                console.log(`Рендерим ${langCode}:`, text.substring(0, 100) + '...');

                const block = document.createElement('div');
                block.className = 'mb-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6';
                block.innerHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center space-x-2">
                            <span class="text-2xl">${langFlag}</span>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">${langName}</h3>
                                <p class="text-sm text-gray-600">${langCode.toUpperCase()}</p>
                            </div>
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="saveText('${langCode}')" class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                                💾 Сохранить
                            </button>
                        </div>
                    </div>
                    <div id="editor-${langCode}" style="height: 300px; border: 1px solid #e5e7eb; border-radius: 0.5rem;"></div>
                    <div class="mt-3 flex justify-between items-center text-sm text-gray-600">
                        <span>Символов: <span id="charCount-${langCode}">0</span></span>
                        <span>Строк: <span id="lineCount-${langCode}">0</span></span>
                    </div>
                `;

                container.appendChild(block);

                // Инициализируем редактор
                setTimeout(() => {
                    initializeEditor(langCode, text);
                }, 100);
            });
        }

        function initializeEditor(langCode, text) {
            console.log(`=== ИНИЦИАЛИЗАЦИЯ РЕДАКТОРА ${langCode} ===`);
            console.log(`Текст:`, text.substring(0, 100) + '...');
            
            const editorElement = document.getElementById(`editor-${langCode}`);
            if (!editorElement) {
                console.error(`❌ Элемент editor-${langCode} не найден`);
                return;
            }
            console.log(`✅ Элемент editor-${langCode} найден`);

            // Проверяем, что Ace.js загружен
            if (typeof ace === 'undefined') {
                console.error('❌ Ace.js не загружен!');
                return;
            }
            console.log('✅ Ace.js загружен');

            try {
                // Удаляем старый редактор если есть
                if (editors[langCode]) {
                    console.log(`🗑️ Удаляем старый редактор для ${langCode}`);
                    editors[langCode].destroy();
                }

                const editor = ace.edit(editorElement);
                console.log(`✅ Ace редактор создан для ${langCode}`);
                
                editor.setTheme('ace/theme/chrome');
                editor.session.setMode('ace/mode/text');
                editor.setOptions({
                    fontSize: '14px',
                    showPrintMargin: false,
                    showGutter: false,
                    highlightActiveLine: false,
                    enableBasicAutocompletion: false,
                    enableLiveAutocompletion: false,
                    readOnly: false  // Явно разрешаем редактирование
                });

                console.log(`📝 Устанавливаем значение для ${langCode}:`, text.length, 'символов');
                editor.setValue(text || '');
                editors[langCode] = editor;

                // Обновляем счетчики
                updateCounters(langCode);

                // Слушаем изменения
                editor.session.on('change', () => {
                    updateCounters(langCode);
                });

                // Проверяем, что редактор активен
                console.log(`🔍 Проверяем активность редактора ${langCode}:`);
                console.log('- readOnly:', editor.getReadOnly());
                console.log('- focused:', editor.isFocused());
                console.log('- value length:', editor.getValue().length);

                console.log(`✅ Редактор ${langCode} успешно инициализирован`);
            } catch (error) {
                console.error(`❌ Ошибка инициализации редактора ${langCode}:`, error);
            }
        }

        function updateCounters(langCode) {
            const editor = editors[langCode];
            if (!editor) return;

            const text = editor.getValue();
            const charCount = text.length;
            const lineCount = text.split('\\n').length;

            document.getElementById(`charCount-${langCode}`).textContent = charCount;
            document.getElementById(`lineCount-${langCode}`).textContent = lineCount;
        }

        function saveText(langCode) {
            console.log(`=== СОХРАНЕНИЕ ТЕКСТА ${langCode} ===`);
            
            const editor = editors[langCode];
            if (!editor) {
                console.error(`❌ Редактор для ${langCode} не найден`);
                showNotification(`❌ Редактор для ${langCode} не найден`, 'error');
                return;
            }

            const content = editor.getValue();
            console.log(`📝 Контент для сохранения (${langCode}):`, content.substring(0, 100) + '...');
            console.log(`📊 Длина контента:`, content.length);
            
            const requestData = {
                category: currentCategory,
                language: langCode,
                content: content
            };
            console.log(`📤 Отправляем данные:`, requestData);
            
            fetch('/api/panel/texts/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                console.log(`📥 Ответ сервера:`, response.status, response.statusText);
                return response.json();
            })
            .then(data => {
                console.log(`📥 Данные ответа:`, data);
                if (data.success) {
                    showNotification(`✅ Текст ${langCode.toUpperCase()} сохранен!`, 'success');
                } else {
                    showNotification('❌ Ошибка сохранения: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка сохранения:', error);
                showNotification('❌ Ошибка сети при сохранении', 'error');
            });
        }

        function saveAllTexts() {
            const textsToSave = {};
            
            Object.keys(editors).forEach(langCode => {
                const editor = editors[langCode];
                if (editor) {
                    textsToSave[langCode] = editor.getValue();
                }
            });

            if (Object.keys(textsToSave).length === 0) {
                showNotification('❌ Нет текстов для сохранения', 'error');
                return;
            }

            fetch('/api/panel/texts/save-all/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    category: currentCategory,
                    texts: textsToSave
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('✅ Все тексты сохранены!', 'success');
                } else {
                    showNotification('❌ Ошибка сохранения: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка сохранения:', error);
                showNotification('❌ Ошибка сети при сохранении', 'error');
            });
        }

        function importBotTexts() {
            fetch('/api/panel/texts/import/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('✅ Тексты импортированы из бота!', 'success');
                    if (currentCategory) {
                        loadCategory(currentCategory);
                    }
                } else {
                    showNotification('❌ Ошибка импорта: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка импорта:', error);
                showNotification('❌ Ошибка сети при импорте', 'error');
            });
        }

        function getLanguageName(code) {
            const names = {
                'ru': 'Русский',
                'en': 'English'
            };
            return names[code] || code.toUpperCase();
        }

        function getLanguageFlag(code) {
            const flags = {
                'ru': '🇷🇺',
                'en': '🇺🇸'
            };
            return flags[code] || '🌐';
        }

        function showNotification(message, type) {
            const notification = document.createElement('div');
            let bgColor = 'bg-blue-600';
            if (type === 'success') bgColor = 'bg-green-600';
            else if (type === 'error') bgColor = 'bg-red-600';
            
            notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white font-medium z-50 ${bgColor}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        function getCookie(name) {
            // Для CSRF токена используем meta тег
            if (name === 'csrftoken') {
                return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            }
            
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html)


# API endpoints
@login_required
def api_dashboard_stats(request):
    """API для получения статистики дашборда"""
    total_users = User.objects.count()
    checks_today = Check.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    revenue_today = Payment.objects.filter(
        status='completed',
        created_at__date=timezone.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    new_users = User.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    active_users = User.objects.filter(
        last_activity__date=timezone.now().date()
    ).count()
    
    checks_week = Check.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_month = Payment.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    avg_check = Payment.objects.filter(
        status='completed'
    ).aggregate(avg=Sum('amount') / Count('id'))['avg'] or 0
    
    stats = {
        'total_users': total_users,
        'checks_today': checks_today,
        'revenue_today': float(revenue_today),
        'bot_status': 'Онлайн',
        'new_users': new_users,
        'active_users': active_users,
        'checks_week': checks_week,
        'total_revenue': float(total_revenue),
        'revenue_month': float(revenue_month),
        'avg_check': float(avg_check)
    }
    
    return JsonResponse(stats)


@login_required
def api_users_list(request):
    """API для получения списка пользователей"""
    users = User.objects.all().order_by('-created_at')
    
    data = []
    for user in users:
        data.append({
            'id': user.tg_id,
            'language': user.language,
            'balance': float(user.balance),
            'created_at': user.created_at.isoformat(),
            'last_activity': user.last_activity.isoformat() if user.last_activity else None,
            'is_blocked': getattr(user, 'is_blocked', False)
        })
    
    return JsonResponse({'users': data})


@login_required
@require_http_methods(["POST"])
def api_user_action(request, user_id):
    """API для действий с пользователем"""
    action = request.POST.get('action')
    user = get_object_or_404(User, tg_id=user_id)
    
    if action == 'block':
        user.is_blocked = True
        user.save()
        action_type = 'user_block'
        description = f'Блокировка пользователя {user_id}'
    elif action == 'unblock':
        user.is_blocked = False
        user.save()
        action_type = 'user_unblock'
        description = f'Разблокировка пользователя {user_id}'
    else:
        return JsonResponse({'status': 'error', 'message': 'Неизвестное действие'})
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type=action_type,
        description=description,
        target_user_id=user_id
    )
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["POST"])
def api_change_user_balance(request, user_id):
    """API для изменения баланса пользователя"""
    try:
        print(f"DEBUG: Получен запрос на изменение баланса для пользователя {user_id}")
        
        # Получаем данные из запроса
        data = json.loads(request.body)
        new_balance = data.get('balance')
        
        print(f"DEBUG: Новый баланс: {new_balance}")
        
        if new_balance is None:
            print("DEBUG: Ошибка - не указан новый баланс")
            return JsonResponse({'status': 'error', 'message': 'Не указан новый баланс'}, status=400)
        
        # Проверяем, что баланс - это число и конвертируем в Decimal
        try:
            from decimal import Decimal
            new_balance = Decimal(str(new_balance))
            if new_balance < 0:
                print("DEBUG: Ошибка - отрицательный баланс")
                return JsonResponse({'status': 'error', 'message': 'Баланс не может быть отрицательным'}, status=400)
        except (ValueError, TypeError):
            print("DEBUG: Ошибка - некорректное значение баланса")
            return JsonResponse({'status': 'error', 'message': 'Некорректное значение баланса'}, status=400)
        
        # Находим пользователя
        try:
            user = User.objects.get(tg_id=user_id)
            print(f"DEBUG: Пользователь найден: {user.tg_id}, текущий баланс: {user.balance}")
        except User.DoesNotExist:
            print(f"DEBUG: Пользователь {user_id} не найден")
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
        
        # Сохраняем старый баланс для логирования
        old_balance = float(user.balance)
        
        # Обновляем баланс
        user.balance = new_balance
        user.save()
        
        print(f"DEBUG: Баланс обновлен с {old_balance} на {float(user.balance)}")
        
        # Логируем действие
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='balance_change',
            description=f'Изменение баланса пользователя {user_id} с ${old_balance} на ${float(user.balance)}',
            target_user_id=user_id
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Баланс пользователя {user_id} изменен на ${float(user.balance)}',
            'new_balance': float(user.balance)
        })
        
    except Exception as e:
        print(f"DEBUG: Ошибка при изменении баланса: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при изменении баланса: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_block_user(request, user_id):
    """API для блокировки пользователя"""
    try:
        user = User.objects.get(tg_id=user_id)
        user.is_blocked = True
        user.save()
        
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='user_block',
            description=f'Блокировка пользователя {user_id}',
            target_user_id=user_id
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Пользователь {user_id} заблокирован'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Пользователь не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при блокировке: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_unblock_user(request, user_id):
    """API для разблокировки пользователя"""
    try:
        user = User.objects.get(tg_id=user_id)
        user.is_blocked = False
        user.save()
        
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='user_unblock',
            description=f'Разблокировка пользователя {user_id}',
            target_user_id=user_id
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Пользователь {user_id} разблокирован'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Пользователь не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при разблокировке: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_send_user_message(request, user_id):
    """API для отправки сообщения пользователю"""
    try:
        data = json.loads(request.body)
        subject = data.get('subject', '')
        content = data.get('content', '')
        
        if not content.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'Текст сообщения не может быть пустым'
            }, status=400)
        
        # Создаем сообщение
        message = UserMessage.objects.create(
            user_id=user_id,
            subject=subject,
            content=content,
            message_type='personal',
            status='pending',
            sent_by=request.user
        )
        
        # Логируем действие
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='send_message',
            description=f'Отправка сообщения пользователю {user_id}: {subject}',
            target_user_id=user_id
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Сообщение отправлено пользователю {user_id}'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Пользователь не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при отправке сообщения: {str(e)}'
        }, status=500)


@login_required
def test_message_api(request, user_id):
    """Тестовый API для проверки отправки сообщений"""
    return JsonResponse({
        'status': 'success',
        'message': f'API для пользователя {user_id} работает корректно'
    })


# Дополнительные функции для массовых сообщений
@login_required
def admin_create_message(request):
    """Создание нового массового сообщения"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = MassMessage.objects.create(
                title=data.get('title', ''),
                content=data.get('content', ''),
                target_language=data.get('target_language', 'all'),
                status='DRAFT',
                created_by=request.user
            )
            return JsonResponse({'status': 'success', 'message_id': message.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})


@login_required
def admin_send_message(request, message_id):
    """Отправка массового сообщения"""
    try:
        message = MassMessage.objects.get(id=message_id)
        message.status = 'SENDING'
        message.save()
        
        # Здесь должна быть логика отправки через Telegram API
        # Пока просто помечаем как отправленное
        message.status = 'COMPLETED'
        message.save()
        
        return JsonResponse({'status': 'success'})
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'})


@login_required
def admin_start_mass_send(request, message_id):
    """Запуск массовой рассылки"""
    try:
        message = MassMessage.objects.get(id=message_id)
        message.status = 'SENDING'
        message.save()
        
        # Логируем действие
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='mass_send_start',
            description=f'Запуск массовой рассылки: {message.title}',
            target_user_id=None
        )
        
        return JsonResponse({'status': 'success'})
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'})


@login_required
def admin_get_message(request, message_id):
    """Получение информации о сообщении"""
    try:
        message = MassMessage.objects.get(id=message_id)
        return JsonResponse({
            'id': message.id,
            'title': message.title,
            'content': message.content,
            'status': message.status,
            'created_at': message.created_at.isoformat()
        })
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'})


@login_required
def admin_edit_message(request, message_id):
    """Редактирование сообщения"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = MassMessage.objects.get(id=message_id)
            message.title = data.get('title', message.title)
            message.content = data.get('content', message.content)
            message.save()
            return JsonResponse({'status': 'success'})
        except MassMessage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})


@login_required
def admin_delete_message(request, message_id):
    """Удаление сообщения"""
    try:
        message = MassMessage.objects.get(id=message_id)
        message.delete()
        return JsonResponse({'status': 'success'})
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'})


# Функции для управления массовой рассылкой
@login_required
def admin_mass_send_sessions(request):
    """Список сессий массовой рассылки"""
    sessions = MassMessage.objects.filter(status__in=['SENDING', 'COMPLETED']).order_by('-created_at')
    data = []
    for session in sessions:
        data.append({
            'id': session.id,
            'title': session.title,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'sent_count': getattr(session, 'sent_count', 0),
            'total_count': getattr(session, 'total_count', 0)
        })
    return JsonResponse({'sessions': data})


@login_required
def admin_mass_send_status(request, session_id):
    """Статус массовой рассылки"""
    try:
        session = MassMessage.objects.get(id=session_id)
        return JsonResponse({
            'id': session.id,
            'status': session.status,
            'sent_count': getattr(session, 'sent_count', 0),
            'total_count': getattr(session, 'total_count', 0),
            'progress': getattr(session, 'progress', 0)
        })
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'})


@login_required
def admin_mass_send_control(request, session_id):
    """Управление массовой рассылкой"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            session = MassMessage.objects.get(id=session_id)
            
            if action == 'pause':
                session.status = 'PAUSED'
            elif action == 'resume':
                session.status = 'SENDING'
            elif action == 'stop':
                session.status = 'STOPPED'
            
            session.save()
            return JsonResponse({'status': 'success'})
        except MassMessage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})


@login_required
def admin_mass_send_details(request, session_id):
    """Детали массовой рассылки"""
    try:
        session = MassMessage.objects.get(id=session_id)
        return JsonResponse({
            'id': session.id,
            'title': session.title,
            'content': session.content,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'sent_count': getattr(session, 'sent_count', 0),
            'total_count': getattr(session, 'total_count', 0),
            'progress': getattr(session, 'progress', 0),
            'errors': getattr(session, 'errors', [])
        })
    except MassMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'})


@login_required
def admin_text_category(request):
    """Управление категориями текстов"""
    categories = [
        {'id': 'welcome', 'name': 'Приветственные', 'icon': '👋'},
        {'id': 'main_menu', 'name': 'Главное меню', 'icon': '🏠'},
        {'id': 'check', 'name': 'Проверки', 'icon': '🔍'},
        {'id': 'check_choice', 'name': 'Выбор проверки', 'icon': '⚡'},
        {'id': 'check_result', 'name': 'Результат проверки', 'icon': '📊'},
        {'id': 'payment', 'name': 'Платежи', 'icon': '💰'},
        {'id': 'error', 'name': 'Ошибки', 'icon': '❌'},
        {'id': 'help', 'name': 'Помощь', 'icon': '❓'},
        {'id': 'settings', 'name': 'Настройки', 'icon': '⚙️'},
        {'id': 'insufficient_balance', 'name': 'Недостаточно средств', 'icon': '💳'},
        {'id': 'user_blocked', 'name': 'Блокировка', 'icon': '🚫'}
    ]
    return JsonResponse({'categories': categories})


def test_texts_page(request):
    """Тестовая страница для проверки текстов"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тест текстов - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center">
            <div class="max-w-md w-full space-y-8">
                <div>
                    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Тест текстов
                    </h2>
                    <p class="mt-2 text-center text-sm text-gray-600">
                        Check Your Crypto
                    </p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <p class="text-center text-gray-600">
                        Страница для тестирования системы текстов
                    </p>
                    <div class="mt-4 text-center">
                        <a href="/api/panel/" class="text-blue-600 hover:text-blue-800">
                            Вернуться в админку
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


@login_required
@require_http_methods(["POST"])
def api_send_user_message(request, user_id):
    """API для отправки персонального сообщения пользователю"""
    try:
        print(f"DEBUG: Получен запрос на отправку сообщения пользователю {user_id}")
        
        # Получаем данные из запроса (поддерживаем и JSON и FormData)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            subject = data.get('subject', '')
            content = data.get('content', '')
        else:
            # FormData
            subject = request.POST.get('subject', '')
            content = request.POST.get('content', '')
        
        print(f"DEBUG: Тема: {subject}, Контент: {content[:50]}...")
        
        if not content or content.strip() == '':
            print("DEBUG: Ошибка - пустой контент сообщения")
            return JsonResponse({'status': 'error', 'message': 'Текст сообщения не может быть пустым'}, status=400)
        
        # Проверяем, существует ли пользователь
        try:
            user = User.objects.get(tg_id=user_id)
            print(f"DEBUG: Пользователь найден: {user.tg_id}")
        except User.DoesNotExist:
            print(f"DEBUG: Пользователь {user_id} не найден")
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
        
        # Создаем запись в базе данных
        try:
            from .admin_models import UserMessage
            message = UserMessage.objects.create(
                user_id=user_id,
                message_type='personal',
                subject=subject,
                content=content,
                language=user.language,
                sent_by=request.user,
                status='pending'
            )
            print(f"DEBUG: Сообщение создано в БД с ID: {message.id}")
        except Exception as e:
            print(f"DEBUG: Ошибка при создании записи в БД: {e}")
            return JsonResponse({'status': 'error', 'message': 'Ошибка при сохранении сообщения'}, status=500)
        
        # Отправляем сообщение через Telegram Bot API (синхронно)
        try:
            import os
            import requests
            
            bot_token = os.getenv('BOT_TOKEN')
            if not bot_token:
                print("DEBUG: BOT_TOKEN не найден в переменных окружения")
                return JsonResponse({'status': 'error', 'message': 'Ошибка конфигурации бота'}, status=500)
            
            # Формируем текст сообщения
            message_text = f"📨 **Сообщение от администрации**\n\n"
            if subject:
                message_text += f"**Тема:** {subject}\n\n"
            message_text += f"{content}"
            
            # Отправляем сообщение через HTTP API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': user_id,
                'text': message_text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ok'):
                # Обновляем статус сообщения
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                
                sent_message_id = response_data['result']['message_id']
                print(f"DEBUG: Сообщение успешно отправлено через Telegram, message_id: {sent_message_id}")
                
                # Логируем действие администратора
                try:
                    from .admin_models import AdminActionLog
                    AdminActionLog.objects.create(
                        admin=request.user,
                        action_type='personal_message_send',
                        description=f'Отправлено сообщение пользователю {user_id}: {subject or "Без темы"}',
                        target_user_id=user_id
                    )
                except Exception as e:
                    print(f"DEBUG: Ошибка при логировании действия: {e}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Сообщение успешно отправлено пользователю {user_id}',
                    'message_id': message.id
                })
            else:
                # Ошибка от Telegram API
                error_description = response_data.get('description', 'Неизвестная ошибка')
                print(f"DEBUG: Ошибка Telegram API: {error_description}")
                message.status = 'failed'
                message.error_message = error_description
                message.save()
                return JsonResponse({'status': 'error', 'message': f'Ошибка отправки: {error_description}'}, status=400)
            
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Ошибка сети при отправке: {e}")
            message.status = 'failed'
            message.error_message = str(e)
            message.save()
            return JsonResponse({'status': 'error', 'message': f'Ошибка сети: {str(e)}'}, status=500)
            
        except Exception as e:
            print(f"DEBUG: Общая ошибка при отправке: {e}")
            message.status = 'failed'
            message.error_message = str(e)
            message.save()
            return JsonResponse({'status': 'error', 'message': f'Ошибка отправки: {str(e)}'}, status=500)
        
    except json.JSONDecodeError as e:
        print(f"DEBUG: Ошибка JSON: {e}")
        return JsonResponse({'status': 'error', 'message': 'Некорректный JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'Ошибка сервера: {str(e)}'}, status=500)


@login_required
def test_message_api(request, user_id):
    """Тестовая функция для диагностики API сообщений"""
    return JsonResponse({
        'status': 'success',
        'message': f'Тест API для пользователя {user_id} работает!',
        'user_id': user_id
    })

@login_required
def admin_text_category(request):
    """Редактирование текстов категории на всех языках"""
    category = request.GET.get('category', 'welcome')
    
    # Автоматически импортируем тексты из бота только если их нет
    try:
        from .text_importer import TextImporter
        from .models import BotText
        if not BotText.objects.exists():
            TextImporter.import_all_texts()
    except Exception as e:
        print(f"Ошибка автоматического импорта текстов: {e}")
    
    category_names = {
        'welcome': 'Приветственные сообщения',
        'main_menu': 'Главное меню',
        'check': 'Сообщения проверки',
        'check_choice': 'Выбор типа проверки',
        'check_result': 'Результат проверки',
        'payment': 'Платежные сообщения',
        'error': 'Сообщения об ошибках',
        'help': 'Справка и помощь',
        'settings': 'Настройки',
        'insufficient_balance': 'Недостаточно средств',
        'user_blocked': 'Пользователь заблокирован'
    }
    
    category_name = category_names.get(category, category)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>""" + category_name + """ - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/ace@1.23.0/build/src/ace.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/ace@1.23.0/build/src/mode-text.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/ace@1.23.0/build/src/theme-chrome.js"></script>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <div>
                            <h1 class="text-2xl font-bold text-gray-900">Check Your Crypto</h1>
                            <p class="text-sm text-gray-600">Редактирование текстов: """ + category_name + """</p>
                        </div>
                        <div class="flex items-center space-x-4">
                            <a href="/api/panel/" class="text-sm text-blue-600 hover:text-blue-800">Дашборд</a>
                            <a href="/api/panel/texts/" class="text-sm text-blue-600 hover:text-blue-800">Все тексты</a>
                            <a href="/api/panel/users/" class="text-sm text-blue-600 hover:text-blue-800">Пользователи</a>
                            <span class="text-sm text-gray-600">admin</span>
                            <a href="/api/panel/logout/" class="text-sm text-red-600 hover:text-red-800">Выйти</a>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="px-4 py-6 sm:px-0">
                    <!-- Header Controls -->
                    <div class="flex justify-between items-center mb-8">
                        <div>
                            <h2 class="text-3xl font-bold text-gray-900">""" + category_name + """</h2>
                            <p class="text-sm text-gray-600 mt-2">Редактирование текстов на всех языках</p>
                        </div>
                        <div class="flex space-x-4">
                            <button onclick="autoTranslateAll()" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
                                🔄 Автоперевод всех
                            </button>
                            <button onclick="saveAllTexts()" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
                                💾 Сохранить все
                            </button>
                        </div>
                    </div>

                    <!-- Language Blocks -->
                    <div id="languageBlocks" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Блоки языков будут загружены динамически -->
                    </div>

                    <!-- Variables Help -->
                    <div class="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">Доступные переменные</h3>
                        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{address}</code>
                                <p class="text-xs text-gray-600 mt-1">Адрес для проверки</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{balance}</code>
                                <p class="text-xs text-gray-600 mt-1">Баланс пользователя</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{amount}</code>
                                <p class="text-xs text-gray-600 mt-1">Сумма платежа</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{username}</code>
                                <p class="text-xs text-gray-600 mt-1">Имя пользователя</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{result}</code>
                                <p class="text-xs text-gray-600 mt-1">Результат проверки</p>
                            </div>
                            <div class="bg-gray-50 p-3 rounded-lg">
                                <code class="text-sm font-mono text-blue-600">{error}</code>
                                <p class="text-xs text-gray-600 mt-1">Текст ошибки</p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <script>
        let editors = {};
        let currentCategory = '""" + category + """';
        let textsData = {};

        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            loadCategoryTexts();
        });

        function loadCategoryTexts() {
            fetch('/api/texts/category/?category=' + currentCategory)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        textsData = data.texts;
                        renderLanguageBlocks(data.languages, data.texts);
                    } else {
                        showNotification('❌ Ошибка загрузки текстов: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Ошибка загрузки текстов:', error);
                    showNotification('❌ Ошибка сети при загрузке', 'error');
                });
        }
        </script>
    </body>
    </html>
    """

    return HttpResponse(html)

@csrf_exempt
def test_texts_page(request):
    """Тестовая страница для проверки загрузки текстов без авторизации"""
    # Получаем все тексты из базы данных
    from .models import BotText
    all_texts = {}
    categories = ['welcome', 'main_menu', 'check', 'check_choice', 'check_result', 'payment', 'error', 'help', 'settings', 'insufficient_balance', 'user_blocked']
    
    for category in categories:
        category_texts = BotText.objects.filter(category=category, is_active=True)
        all_texts[category] = {}
        for text in category_texts:
            all_texts[category][text.language] = text.content
    
    import json
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тест загрузки текстов - Check Your Crypto</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/ace.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/mode-text.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.23.0/theme-chrome.js"></script>
        <script>
            // Передаем данные текстов прямо в JavaScript
            window.allTextsData = """ + json.dumps(all_texts, ensure_ascii=False) + """;
            console.log('=== ТЕСТОВАЯ СТРАНИЦА ===');
            console.log('Загруженные тексты:', window.allTextsData);
            console.log('Тип данных:', typeof window.allTextsData);
            console.log('Доступные категории:', Object.keys(window.allTextsData || {}));
            console.log('Тексты welcome:', window.allTextsData?.welcome);
            
            // Проверяем загрузку Ace.js
            window.addEventListener('load', function() {
                console.log('=== ПРОВЕРКА ACE.JS ===');
                console.log('typeof ace:', typeof ace);
                if (typeof ace !== 'undefined') {
                    console.log('✅ Ace.js загружен успешно!');
                } else {
                    console.log('❌ Ace.js НЕ загружен!');
                }
            });
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
                            <p class="text-sm text-gray-600">Тестовая страница загрузки текстов</p>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="px-4 py-6 sm:px-0">
                    <!-- Header Controls -->
                    <div class="flex justify-between items-center mb-8">
                        <div>
                            <h2 class="text-3xl font-bold text-gray-900">Тест загрузки текстов</h2>
                            <p class="text-sm text-gray-600 mt-2">Проверка загрузки текстов без авторизации</p>
                        </div>
                    </div>
                    
                    <!-- Text Editor -->
                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <!-- Text Categories Sidebar -->
                        <div class="lg:col-span-1">
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 class="text-lg font-semibold text-gray-900 mb-4">Категории текстов</h3>
                                <div class="space-y-2">
                                    <button onclick="loadCategory('welcome')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        👋 Приветственные
                                    </button>
                                    <button onclick="loadCategory('main_menu')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        🏠 Главное меню
                                    </button>
                                    <button onclick="loadCategory('check')" class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm font-medium text-gray-700 transition-colors">
                                        🔍 Проверки
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Editor Area -->
                        <div class="lg:col-span-3">
                            <div id="editorContainer" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div class="text-center py-8">
                                    <p class="text-gray-600">Выберите категорию для загрузки текстов</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <script>
        let editors = {};
        let currentCategory = '';
        let textsData = {};

        function loadCategory(category) {
            console.log('=== НАЧАЛО loadCategory ===');
            console.log('Категория:', category);
            console.log('window.allTextsData:', window.allTextsData);
            
            currentCategory = category;
            
            // Показываем загрузку
            const container = document.getElementById('editorContainer');
            if (!container) {
                console.error('Элемент editorContainer не найден!');
                return;
            }
            
            container.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p class="text-gray-600">Загрузка текстов...</p>
                </div>
            `;
            
            // Используем данные из window.allTextsData
            setTimeout(() => {
                console.log('=== ПРОВЕРКА ДАННЫХ ===');
                console.log('Загружаем категорию:', category);
                console.log('window.allTextsData:', window.allTextsData);
                console.log('Тип window.allTextsData:', typeof window.allTextsData);
                
                if (window.allTextsData && window.allTextsData[category]) {
                    textsData = window.allTextsData[category];
                    const languages = Object.keys(textsData);
                    console.log('Найдены языки:', languages);
                    console.log('Тексты:', textsData);
                    console.log('Тип textsData:', typeof textsData);
                    renderLanguageBlocks(languages, textsData);
                } else {
                    console.log('Тексты не найдены для категории:', category);
                    console.log('Проверяем все категории:', Object.keys(window.allTextsData || {}));
                    container.innerHTML = '<div class="text-center py-8"><p class="text-red-600">❌ Тексты для категории ' + category + ' не найдены</p></div>';
                }
            }, 100);
        }

        function renderLanguageBlocks(languages, texts) {
            const container = document.getElementById('editorContainer');
            container.innerHTML = '';

            languages.forEach(langCode => {
                const langName = getLanguageName(langCode);
                const langFlag = getLanguageFlag(langCode);
                const text = texts[langCode] || '';
                
                console.log(`Рендерим ${langCode}:`, text.substring(0, 100) + '...');

                const block = document.createElement('div');
                block.className = 'mb-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6';
                block.innerHTML = `
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center space-x-2">
                            <span class="text-2xl">${langFlag}</span>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">${langName}</h3>
                                <p class="text-sm text-gray-600">${langCode.toUpperCase()}</p>
                            </div>
                        </div>
                    </div>
                    <div id="editor-${langCode}" style="height: 300px; border: 1px solid #e5e7eb; border-radius: 0.5rem;"></div>
                    <div class="mt-3 flex justify-between items-center text-sm text-gray-600">
                        <span>Символов: <span id="charCount-${langCode}">0</span></span>
                        <span>Строк: <span id="lineCount-${langCode}">0</span></span>
                    </div>
                `;

                container.appendChild(block);

                // Инициализируем редактор
                setTimeout(() => {
                    initializeEditor(langCode, text);
                }, 500);
            });
        }

        function initializeEditor(langCode, text) {
            console.log(`Инициализируем редактор для ${langCode}:`, text.substring(0, 100) + '...');
            
            const editorElement = document.getElementById(`editor-${langCode}`);
            if (!editorElement) {
                console.error(`Элемент editor-${langCode} не найден`);
                return;
            }

            // Проверяем, что Ace.js загружен
            if (typeof ace === 'undefined') {
                console.error('Ace.js не загружен!');
                return;
            }

            try {
                const editor = ace.edit(editorElement);
                editor.setTheme('ace/theme/chrome');
                editor.session.setMode('ace/mode/text');
                editor.setOptions({
                    fontSize: '14px',
                    showPrintMargin: false,
                    showGutter: false,
                    highlightActiveLine: false,
                    enableBasicAutocompletion: false,
                    enableLiveAutocompletion: false
                });

                console.log(`Устанавливаем значение для ${langCode}:`, text.length, 'символов');
                editor.setValue(text || '');
                editors[langCode] = editor;

                // Обновляем счетчики
                updateCounters(langCode);

                // Слушаем изменения
                editor.session.on('change', () => {
                    updateCounters(langCode);
                });

                console.log(`Редактор ${langCode} успешно инициализирован`);
            } catch (error) {
                console.error(`Ошибка инициализации редактора ${langCode}:`, error);
            }
        }

        function updateCounters(langCode) {
            const editor = editors[langCode];
            if (!editor) return;

            const text = editor.getValue();
            const charCount = text.length;
            const lineCount = text.split('\\n').length;

            document.getElementById(`charCount-${langCode}`).textContent = charCount;
            document.getElementById(`lineCount-${langCode}`).textContent = lineCount;
        }

        function getLanguageName(code) {
            const names = {
                'ru': 'Русский',
                'en': 'English'
            };
            return names[code] || code.toUpperCase();
        }

        function getLanguageFlag(code) {
            const flags = {
                'ru': '🇷🇺',
                'en': '🇺🇸'
            };
            return flags[code] || '🌐';
        }
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
@login_required
def admin_create_message(request):
    """Создание массового сообщения через веб-интерфейс"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '')
            content = request.POST.get('content', '')
            user_filter = request.POST.get('user_filter', 'all')
            send_type = request.POST.get('send_type', 'immediate')
            scheduled_at = request.POST.get('scheduled_at', None)
            
            if not title or not content or not user_filter:
                return JsonResponse({'success': False, 'error': 'Заполните все обязательные поля'})
            
            # Создаем сообщение напрямую в базе данных
            from .admin_models import MassMessage
            
            # Получаем объект AdminUser
            from .admin_models import AdminUser
            try:
                admin_user = AdminUser.objects.get(id=request.user.id if hasattr(request.user, 'id') else 1)
            except AdminUser.DoesNotExist:
                admin_user = AdminUser.objects.first()  # Используем первого админа
            
            # Определяем статус в зависимости от типа отправки
            status = 'SCHEDULED' if send_type == 'scheduled' and scheduled_at else 'DRAFT'
            
            message = MassMessage.objects.create(
                title=title,
                content=content,
                user_filter=user_filter,
                language='ru',
                status=status,
                user_language='ru',
                is_active_only=True,
                scheduled_at=scheduled_at if scheduled_at else None,
                created_by=admin_user
            )
            
            # Создаем сообщение в статусе DRAFT
            return JsonResponse({
                'success': True, 
                'message': 'Сообщение создано! Теперь вы можете отправить его.',
                'message_id': message.id
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@csrf_exempt
@login_required
def admin_send_message(request, message_id):
    """Отправка массового сообщения через веб-интерфейс"""
    if request.method == 'POST':
        try:
            # Получаем сообщение
            from .admin_models import MassMessage
            
            try:
                message = MassMessage.objects.get(id=message_id)
            except MassMessage.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Сообщение не найдено'})
            
            # Прямая отправка через Telegram API
            import asyncio
            import sys
            import os
            from datetime import datetime
            
            # Добавляем путь к модулям
            sys.path.insert(0, '/app')
            
            try:
                
                # ПРОСТАЯ ОТПРАВКА В ОТДЕЛЬНОМ ПОТОКЕ
                import threading
                import queue
                
                result_queue = queue.Queue()
                
                def send_in_thread():
                    try:
                        from .advanced_mass_send import send_mass_message_smart
                        result = send_mass_message_smart(message_id)
                        result_queue.put(('success', result))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                # Запускаем в отдельном потоке
                thread = threading.Thread(target=send_in_thread)
                thread.daemon = True
                thread.start()
                
                # Ждем результат
                try:
                    status, result = result_queue.get(timeout=60)
                    if status == 'success':
                        return JsonResponse({
                            'success': True, 
                            'message': f'Сообщение отправлено! Успешно: {result["success"]}, Ошибок: {result["failed"]}'
                        })
                    else:
                        return JsonResponse({'success': False, 'error': result})
                except queue.Empty:
                    return JsonResponse({'success': False, 'error': 'Таймаут отправки (60 секунд)'})
                    
            except ImportError as e:
                # Если не удалось импортировать модули, обновляем статус на ошибку
                message.status = 'FAILED'
                message.save()
                return JsonResponse({'success': False, 'error': f'Ошибка импорта: {str(e)}'})
            except Exception as e:
                # Если произошла другая ошибка, обновляем статус на ошибку
                message.status = 'FAILED'
                message.save()
                return JsonResponse({'success': False, 'error': str(e)})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_get_message(request, message_id):
    """Получение данных массового сообщения для редактирования"""
    if request.method == 'GET':
        try:
            from .admin_models import MassMessage
            message = MassMessage.objects.get(id=message_id)
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'title': message.title,
                    'content': message.content,
                    'user_filter': message.user_filter,
                    'status': message.status,
                    'created_at': message.created_at.isoformat() if message.created_at else None,
                    'scheduled_at': message.scheduled_at.isoformat() if message.scheduled_at else None,
                }
            })
        except MassMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сообщение не найдено'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_edit_message(request, message_id):
    """Редактирование массового сообщения"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            user_filter = request.POST.get('user_filter', 'all')
            
            if not title or not content:
                return JsonResponse({'success': False, 'error': 'Заголовок и содержание обязательны'})
            
            from .admin_models import MassMessage
            message = MassMessage.objects.get(id=message_id)
            
            # Разрешаем редактирование любых сообщений
            pass
            
            message.title = title
            message.content = content
            message.user_filter = user_filter
            message.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Сообщение обновлено!'
            })
                
        except MassMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сообщение не найдено'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@csrf_exempt
@login_required
def admin_delete_message(request, message_id):
    """Удаление массового сообщения через веб-интерфейс"""
    if request.method == 'POST':
        try:
            # Удаляем сообщение из базы данных
            from .admin_models import MassMessage
            message = MassMessage.objects.get(id=message_id)
            
            # Разрешаем удаление любых сообщений
            pass
            
            message.delete()
            
            return JsonResponse({'success': True, 'message': 'Сообщение удалено успешно'})
                
        except MassMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сообщение не найдено'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

@login_required
def admin_start_mass_send(request, message_id):
    """Запуск массовой рассылки с новой системой управления"""
    if request.method == 'POST':
        try:
            from .mass_send_manager import MassSendManagerFactory
            
            # Получаем параметры
            user_filter = request.POST.get('user_filter', 'all')
            batch_size = int(request.POST.get('batch_size', 50))
            delay_between_batches = int(request.POST.get('delay_between_batches', 1))
            delay_between_messages = float(request.POST.get('delay_between_messages', 0.1))
            
            # Создаем сессию
            session = MassSendManagerFactory.create_session(
                message_id=message_id,
                user_filter=user_filter,
                created_by_id=request.user.id,
                batch_size=batch_size,
                delay_between_batches=delay_between_batches,
                delay_between_messages=delay_between_messages
            )
            
            # Запускаем отправку в отдельном потоке
            MassSendManagerFactory.start_sending(session.id)
            
            return JsonResponse({
                'success': True,
                'message': f'Рассылка запущена! Сессия ID: {session.id}',
                'session_id': session.id
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_mass_send_status(request, session_id):
    """Получение статуса массовой рассылки"""
    if request.method == 'GET':
        try:
            from .admin_models import MassSendSession
            from .mass_send_manager import get_active_manager
            
            session = MassSendSession.objects.get(id=session_id)
            
            # Получаем активный менеджер
            manager = get_active_manager(session_id)
            
            status_data = {
                'session_id': session.id,
                'message_title': session.message.title,
                'status': session.status,
                'progress': session.progress_percentage,
                'total': session.total_recipients,
                'sent': session.sent_count,
                'failed': session.failed_count,
                'skipped': session.skipped_count,
                'remaining': session.remaining_count,
                'eta': session.estimated_completion.isoformat() if session.estimated_completion else None,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'paused_at': session.paused_at.isoformat() if session.paused_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'can_pause': session.status == 'RUNNING',
                'can_resume': session.status == 'PAUSED',
                'can_cancel': session.status in ['PENDING', 'RUNNING', 'PAUSED'],
            }
            
            return JsonResponse({
                'success': True,
                'status': status_data
            })
                
        except MassSendSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сессия не найдена'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_mass_send_control(request, session_id):
    """Управление массовой рассылкой (пауза/возобновление/отмена)"""
    if request.method == 'POST':
        try:
            from .admin_models import MassSendSession
            from .mass_send_manager import get_active_manager, set_active_manager
            
            action = request.POST.get('action')
            session = MassSendSession.objects.get(id=session_id)
            
            if action == 'pause':
                if session.status == 'RUNNING':
                    manager = get_active_manager(session_id)
                    if manager:
                        manager.pause()
                        set_active_manager(session_id, manager)
                    return JsonResponse({'success': True, 'message': 'Рассылка приостановлена'})
                else:
                    return JsonResponse({'success': False, 'error': 'Рассылка не выполняется'})
            
            elif action == 'resume':
                if session.status == 'PAUSED':
                    manager = get_active_manager(session_id)
                    if manager:
                        manager.resume()
                        set_active_manager(session_id, manager)
                    return JsonResponse({'success': True, 'message': 'Рассылка возобновлена'})
                else:
                    return JsonResponse({'success': False, 'error': 'Рассылка не приостановлена'})
            
            elif action == 'cancel':
                if session.status in ['PENDING', 'RUNNING', 'PAUSED']:
                    manager = get_active_manager(session_id)
                    if manager:
                        manager.cancel()
                    return JsonResponse({'success': True, 'message': 'Рассылка отменена'})
                else:
                    return JsonResponse({'success': False, 'error': 'Рассылка не может быть отменена'})
            
            else:
                return JsonResponse({'success': False, 'error': 'Неизвестное действие'})
                
        except MassSendSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сессия не найдена'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_mass_send_details(request, session_id):
    """Детальная информация о массовой рассылке"""
    if request.method == 'GET':
        try:
            from .admin_models import MassSendSession, MassSendRecipient
            
            session = MassSendSession.objects.get(id=session_id)
            
            # Получаем статистику по статусам
            recipients_stats = MassSendRecipient.objects.filter(session=session).values('status').annotate(
                count=models.Count('id')
            )
            
            # Получаем последние ошибки
            recent_errors = MassSendRecipient.objects.filter(
                session=session,
                status='FAILED'
            ).order_by('-updated_at')[:10]
            
            details = {
                'session_id': session.id,
                'message_title': session.message.title,
                'message_content': session.message.content[:100] + '...' if len(session.message.content) > 100 else session.message.content,
                'status': session.status,
                'progress': session.progress_percentage,
                'total': session.total_recipients,
                'sent': session.sent_count,
                'failed': session.failed_count,
                'skipped': session.skipped_count,
                'remaining': session.remaining_count,
                'eta': session.estimated_completion.isoformat() if session.estimated_completion else None,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'paused_at': session.paused_at.isoformat() if session.paused_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'settings': {
                    'batch_size': session.batch_size,
                    'delay_between_batches': session.delay_between_batches,
                    'delay_between_messages': session.delay_between_messages,
                    'max_retries': session.max_retries,
                },
                'recipients_stats': list(recipients_stats),
                'recent_errors': [
                    {
                        'user_id': r.user.tg_id,
                        'error': r.error_message,
                        'retry_count': r.retry_count,
                        'updated_at': r.updated_at.isoformat()
                    }
                    for r in recent_errors
                ]
            }
            
            return JsonResponse({
                'success': True,
                'details': details
            })
                
        except MassSendSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Сессия не найдена'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def admin_mass_send_sessions(request):
    """Список всех сессий массовой рассылки"""
    if request.method == 'GET':
        try:
            from .admin_models import MassSendSession
            
            sessions = MassSendSession.objects.all().order_by('-created_at')[:50]
            
            sessions_data = []
            for session in sessions:
                sessions_data.append({
                    'id': session.id,
                    'message_title': session.message.title,
                    'status': session.status,
                    'progress': session.progress_percentage,
                    'total': session.total_recipients,
                    'sent': session.sent_count,
                    'failed': session.failed_count,
                    'skipped': session.skipped_count,
                    'created_at': session.created_at.isoformat(),
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'created_by': session.created_by.username,
                })
            
            return JsonResponse({
                'success': True,
                'sessions': sessions_data
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})
