"""
Views for core app
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User, Check, Payment, Setting, Text, PaymentMethod, Referral, Outbox


@csrf_exempt
@require_http_methods(["GET"])
def stats(request):
    """Статистика приложения"""
    # Получаем статистику за последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)
    
    stats_data = {
        "status": "ok",
        "service": "checkyourcrypto-admin",
        "version": "1.0.0",
        "stats": {
            "total_users": User.objects.count(),
            "total_checks": Check.objects.count(),
            "total_payments": Payment.objects.count(),
            "new_users_week": User.objects.filter(created_at__gte=week_ago).count(),
            "checks_week": Check.objects.filter(created_at__gte=week_ago).count(),
            "revenue_week": Payment.objects.filter(
                created_at__gte=week_ago, 
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            "checks_by_type": dict(Check.objects.values('type').annotate(count=Count('id')).values_list('type', 'count')),
            "checks_by_chain": dict(Check.objects.values('chain').annotate(count=Count('id')).values_list('chain', 'count')[:10]),
        }
    }
    
    return JsonResponse(stats_data)


@login_required
def dashboard(request):
    """Dashboard для админа"""
    # Статистика за сегодня
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    # Статистика за неделю
    week_ago = timezone.now() - timedelta(days=7)
    
    context = {
        'today_stats': {
            'new_users': User.objects.filter(created_at__range=(today_start, today_end)).count(),
            'checks': Check.objects.filter(created_at__range=(today_start, today_end)).count(),
            'payments': Payment.objects.filter(created_at__range=(today_start, today_end)).count(),
            'revenue': Payment.objects.filter(
                created_at__range=(today_start, today_end),
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
        },
        'week_stats': {
            'new_users': User.objects.filter(created_at__gte=week_ago).count(),
            'checks': Check.objects.filter(created_at__gte=week_ago).count(),
            'payments': Payment.objects.filter(created_at__gte=week_ago).count(),
            'revenue': Payment.objects.filter(
                created_at__gte=week_ago,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
        },
        'recent_checks': Check.objects.select_related('user').order_by('-created_at')[:10],
        'recent_payments': Payment.objects.select_related('user').order_by('-created_at')[:10],
        'pending_outbox': Outbox.objects.filter(status='pending').count(),
    }
    
    return render(request, 'admin/dashboard.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_get_text(request):
    """API для получения текста по ключу и языку"""
    try:
        data = json.loads(request.body)
        lang = data.get('lang', 'ru')
        key = data.get('key')
        
        if not key:
            return JsonResponse({'error': 'Key is required'}, status=400)
        
        try:
            text = Text.objects.get(lang=lang, key=key)
            return JsonResponse({'text': text.value})
        except Text.DoesNotExist:
            return JsonResponse({'error': 'Text not found'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_set_text(request):
    """API для установки текста"""
    try:
        data = json.loads(request.body)
        lang = data.get('lang', 'ru')
        key = data.get('key')
        value = data.get('value')
        
        if not all([key, value]):
            return JsonResponse({'error': 'Key and value are required'}, status=400)
        
        text, created = Text.objects.update_or_create(
            lang=lang, key=key,
            defaults={'value': value}
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'text_id': f"{text.lang}:{text.key}"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_get_setting(request):
    """API для получения настройки"""
    try:
        data = json.loads(request.body)
        key = data.get('key')
        
        if not key:
            return JsonResponse({'error': 'Key is required'}, status=400)
        
        try:
            setting = Setting.objects.get(key=key)
            return JsonResponse({'value': setting.value})
        except Setting.DoesNotExist:
            return JsonResponse({'error': 'Setting not found'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_set_setting(request):
    """API для установки настройки"""
    try:
        data = json.loads(request.body)
        key = data.get('key')
        value = data.get('value')
        description = data.get('description', '')
        
        if not all([key, value]):
            return JsonResponse({'error': 'Key and value are required'}, status=400)
        
        setting, created = Setting.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'key': setting.key
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_outbox(request):
    """API для создания сообщения в outbox"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        payload = data.get('payload')
        
        if not all([user_id, payload]):
            return JsonResponse({'error': 'User ID and payload are required'}, status=400)
        
        try:
            user = User.objects.get(tg_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        outbox = Outbox.objects.create(
            user=user,
            payload=payload
        )
        
        return JsonResponse({
            'success': True,
            'outbox_id': outbox.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'checkyourcrypto-admin'
    })
