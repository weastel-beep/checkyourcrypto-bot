"""
API для работы с текстами бота
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import BotText
from .text_importer import TextImporter


def add_cors_headers(response):
    """Добавляет CORS заголовки к ответу"""
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
    return response


def sync_single_text_to_bot(text_obj):
    """Синхронизирует один текст с ботом"""
    import asyncio
    import asyncpg
    import os
    
    async def sync_text():
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception('Не найден DATABASE_URL')
        
        conn = await asyncpg.connect(database_url)
        try:
            # Проверяем, есть ли уже такой текст
            existing = await conn.fetchrow(
                "SELECT id FROM texts WHERE key = $1 AND lang = $2",
                text_obj.category, text_obj.language
            )
            
            if existing:
                # Обновляем существующий
                await conn.execute(
                    "UPDATE texts SET value = $1, updated_at = NOW() WHERE key = $2 AND lang = $3",
                    text_obj.content, text_obj.category, text_obj.language
                )
            else:
                # Создаем новый
                await conn.execute(
                    "INSERT INTO texts (key, lang, value, updated_at) VALUES ($1, $2, $3, NOW())",
                    text_obj.category, text_obj.language, text_obj.content
                )
            
            print(f"✅ Синхронизирован: {text_obj.category} ({text_obj.language})")
            
        finally:
            await conn.close()
    
    # Запускаем синхронизацию
    asyncio.run(sync_text())


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_texts_for_language(request):
    """Получить тексты для конкретного языка"""
    try:
        language = request.GET.get('language', 'ru')
        texts = {}
        
        for category, _ in BotText.CATEGORIES:
            text_obj = BotText.objects.filter(
                category=category,
                language=language,
                is_active=True
            ).first()
            
            if text_obj:
                texts[category] = text_obj.content
            else:
                # Возвращаем дефолтный текст
                default_texts = TextImporter.get_texts_by_category(category)
                texts[category] = default_texts.get(language, '')
        
        return JsonResponse({
            'success': True,
            'language': language,
            'texts': texts
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_texts_by_category(request):
    """Получить тексты для конкретной категории на всех языках"""
    try:
        category = request.GET.get('category')
        if not category:
            response = JsonResponse({
                'success': False,
                'error': 'Категория не указана'
            }, status=400)
            return add_cors_headers(response)
        
        # Получаем тексты из базы данных
        texts = {}
        languages = TextImporter.get_languages()
        
        for language in languages:
            text_obj = BotText.objects.filter(
                category=category,
                language=language,
                is_active=True
            ).first()
            
            if text_obj:
                texts[language] = text_obj.content
            else:
                # Возвращаем дефолтный текст из импортера
                default_texts = TextImporter.get_texts_by_category(category)
                texts[language] = default_texts.get(language, '')
        
        response = JsonResponse({
            'success': True,
            'category': category,
            'languages': languages,
            'texts': texts
        })
        return add_cors_headers(response)
        
    except Exception as e:
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)


@csrf_exempt
@csrf_exempt
@require_http_methods(["POST"])
def save_text(request):
    """Сохранить текст для конкретной категории и языка"""
    try:
        data = json.loads(request.body)
        category = data.get('category')
        language = data.get('language')
        content = data.get('content')
        
        if not all([category, language, content]):
            return JsonResponse({
                'success': False,
                'error': 'Не все параметры указаны'
            }, status=400)
        
        # Проверяем, существует ли уже такой текст
        text_obj = BotText.objects.filter(
            category=category,
            language=language,
            is_active=True
        ).first()
        
        if text_obj:
            # Обновляем существующий текст
            text_obj.content = content
            text_obj.save()
        else:
            # Создаем новый текст
            text_obj = BotText.objects.create(
                category=category,
                language=language,
                content=content,
                is_active=True,
                version=1
            )
        
        # Автоматически синхронизируем с ботом
        try:
            sync_single_text_to_bot(text_obj)
        except Exception as sync_error:
            print(f"Ошибка синхронизации текста {category}/{language}: {sync_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Текст {category}/{language} сохранен и синхронизирован с ботом'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_all_texts(request):
    """Сохранить все тексты для категории"""
    try:
        data = json.loads(request.body)
        category = data.get('category')
        texts = data.get('texts', {})
        
        if not category or not texts:
            return JsonResponse({
                'success': False,
                'error': 'Категория и тексты должны быть указаны'
            }, status=400)
        
        saved_count = 0
        
        for language, content in texts.items():
            # Проверяем, существует ли уже такой текст
            text_obj = BotText.objects.filter(
                category=category,
                language=language,
                is_active=True
            ).first()
            
            if text_obj:
                # Обновляем существующий текст
                text_obj.content = content
                text_obj.save()
            else:
                # Создаем новый текст
                text_obj = BotText.objects.create(
                    category=category,
                    language=language,
                    content=content,
                    is_active=True,
                    version=1
                )
            
            saved_count += 1
        
        # Автоматически синхронизируем все сохраненные тексты с ботом
        try:
            for language, content in texts.items():
                text_obj = BotText.objects.filter(
                    category=category,
                    language=language,
                    is_active=True
                ).first()
                if text_obj:
                    sync_single_text_to_bot(text_obj)
        except Exception as sync_error:
            print(f"Ошибка синхронизации текстов категории {category}: {sync_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Сохранено и синхронизировано {saved_count} текстов для категории {category}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def import_texts(request):
    """Импортировать тексты из бота"""
    try:
        success = TextImporter.import_all_texts()
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Тексты успешно импортированы из бота'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Ошибка при импорте текстов'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_languages(request):
    """Получить список поддерживаемых языков"""
    try:
        languages = TextImporter.get_languages()
        
        return JsonResponse({
            'success': True,
            'languages': languages
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_categories(request):
    """Получить список категорий текстов"""
    try:
        categories = [choice[0] for choice in BotText.CATEGORIES]
        
        return JsonResponse({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sync_texts_to_bot(request):
    """Синхронизировать тексты из админки в бот"""
    try:
        import asyncio
        import asyncpg
        import os
        from .models import BotText
        
        # Получаем все активные тексты из админки
        admin_texts = BotText.objects.filter(is_active=True)
        
        if not admin_texts:
            return JsonResponse({
                'success': False,
                'error': 'Нет активных текстов для синхронизации'
            }, status=400)
        
        # Подключаемся к PostgreSQL боты
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return JsonResponse({
                'success': False,
                'error': 'Не найден DATABASE_URL'
            }, status=500)
        
        async def sync_texts():
            conn = await asyncpg.connect(database_url)
            try:
                synced_count = 0
                for text_obj in admin_texts:
                    # Проверяем, есть ли уже такой текст
                    existing = await conn.fetchrow(
                        "SELECT id FROM texts WHERE key = $1 AND lang = $2",
                        text_obj.category, text_obj.language
                    )
                    
                    if existing:
                        # Обновляем существующий
                        await conn.execute(
                            "UPDATE texts SET value = $1, updated_at = NOW() WHERE key = $2 AND lang = $3",
                            text_obj.content, text_obj.category, text_obj.language
                        )
                    else:
                        # Создаем новый
                        await conn.execute(
                            "INSERT INTO texts (key, lang, value, updated_at) VALUES ($1, $2, $3, NOW())",
                            text_obj.category, text_obj.language, text_obj.content
                        )
                    
                    synced_count += 1
                    print(f"✅ Синхронизирован: {text_obj.category} ({text_obj.language})")
                
                return synced_count
                
            finally:
                await conn.close()
        
        # Запускаем синхронизацию
        synced_count = asyncio.run(sync_texts())
        
        return JsonResponse({
            'success': True,
            'message': f'Синхронизировано {synced_count} текстов в бот',
            'synced_count': synced_count
        })
        
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
