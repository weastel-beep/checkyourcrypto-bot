"""
Сервис переводов для Check Your Crypto
Использует deep-translator - лучшую библиотеку для переводов
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from django.utils import timezone
from django.core.cache import cache

# Импортируем deep-translator
try:
    from deep_translator import GoogleTranslator, LibreTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    logging.warning("deep-translator не установлен. Переводы будут недоступны.")

from .models import Text
from .admin_models import BotText, AdminUser


class TranslationService:
    """Сервис для работы с переводами"""
    
    # Поддерживаемые языки
    SUPPORTED_LANGUAGES = {
        'ru': {'name': 'Русский', 'flag': '🇷🇺'},
        'en': {'name': 'English', 'flag': '🇺🇸'},
        'es': {'name': 'Español', 'flag': '🇪🇸'},
        'fr': {'name': 'Français', 'flag': '🇫🇷'},
        'de': {'name': 'Deutsch', 'flag': '🇩🇪'},
        'it': {'name': 'Italiano', 'flag': '🇮🇹'},
        'pt': {'name': 'Português', 'flag': '🇵🇹'},
        'zh': {'name': '中文', 'flag': '🇨🇳'},
        'ja': {'name': '日本語', 'flag': '🇯🇵'},
        'ko': {'name': '한국어', 'flag': '🇰🇷'},
        'ar': {'name': 'العربية', 'flag': '🇸🇦'},
        'hi': {'name': 'हिन्दी', 'flag': '🇮🇳'},
        'tr': {'name': 'Türkçe', 'flag': '🇹🇷'},
        'pl': {'name': 'Polski', 'flag': '🇵🇱'},
        'nl': {'name': 'Nederlands', 'flag': '🇳🇱'},
    }
    
    # Типы текстов
    TEXT_TYPES = {
        'welcome': 'Приветствие',
        'main_menu': 'Главное меню',
        'check_instructions': 'Инструкции проверки',
        'check_result': 'Результат проверки',
        'payment_info': 'Информация о платежах',
        'profile_info': 'Информация профиля',
        'faq': 'FAQ',
        'error_message': 'Сообщения об ошибках',
        'functions': 'Описание функций',
        'check_choice': 'Выбор типа проверки',
        'insufficient_balance': 'Недостаточно средств',
        'referral_info': 'Реферальная программа',
        'payment_methods': 'Способы оплаты',
        'success_payment': 'Успешная оплата',
        'error_payment': 'Ошибка оплаты',
    }
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 час
        self.translator = None
        self._init_translator()
    
    def _init_translator(self):
        """Инициализация переводчика"""
        if not TRANSLATION_AVAILABLE:
            return
        
        try:
            # Используем Google Translate как основной
            self.translator = GoogleTranslator(source='auto', target='en')
        except Exception as e:
            logging.error(f"Ошибка инициализации переводчика: {e}")
            # Fallback на LibreTranslate
            try:
                self.translator = LibreTranslator(source='auto', target='en')
            except Exception as e2:
                logging.error(f"Ошибка инициализации LibreTranslate: {e2}")
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'ru') -> Optional[str]:
        """Перевод текста"""
        if not TRANSLATION_AVAILABLE or not self.translator:
            return None
        
        if target_lang == source_lang:
            return text
        
        try:
            # Создаем новый переводчик для целевого языка
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            logging.error(f"Ошибка перевода {source_lang} -> {target_lang}: {e}")
            return None
    
    def translate_all_texts(self, source_lang: str = 'ru', target_lang: str = 'en') -> Dict[str, str]:
        """Перевод всех текстов с одного языка на другой"""
        if not TRANSLATION_AVAILABLE:
            return {}
        
        try:
            # Получаем все тексты исходного языка
            texts = Text.objects.filter(lang=source_lang)
            bot_texts = BotText.objects.filter(language=source_lang, is_active=True)
            
            translated_texts = {}
            
            # Переводим обычные тексты
            for text in texts:
                translated = self.translate_text(text.value, target_lang, source_lang)
                if translated:
                    translated_texts[text.key] = translated
            
            # Переводим тексты бота
            for text in bot_texts:
                translated = self.translate_text(text.content, target_lang, source_lang)
                if translated:
                    translated_texts[text.text_type] = translated
            
            return translated_texts
            
        except Exception as e:
            logging.error(f"Ошибка массового перевода: {e}")
            return {}
    
    def add_new_language(self, lang_code: str, base_lang: str = 'ru') -> bool:
        """Добавление нового языка с автоматическим переводом"""
        if lang_code not in self.SUPPORTED_LANGUAGES:
            return False
        
        try:
            # Переводим все тексты
            translated_texts = self.translate_all_texts(base_lang, lang_code)
            
            # Сохраняем переведенные тексты
            for key, value in translated_texts.items():
                # Сохраняем в Text
                Text.objects.update_or_create(
                    lang=lang_code,
                    key=key,
                    defaults={'value': value}
                )
                
                # Сохраняем в BotText если это тип бота
                if key in self.TEXT_TYPES:
                    BotText.objects.update_or_create(
                        text_type=key,
                        language=lang_code,
                        version=1,
                        defaults={
                            'content': value,
                            'is_active': True,
                            'created_by': AdminUser.objects.first()  # Временно
                        }
                    )
            
            logging.info(f"Язык {lang_code} успешно добавлен с переводами")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка добавления языка {lang_code}: {e}")
            return False
    
    def get_texts_for_language(self, lang: str) -> Dict[str, str]:
        """Получение всех текстов для языка"""
        cache_key = f"texts_{lang}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            texts = {}
            
            # Получаем обычные тексты
            for text in Text.objects.filter(lang=lang):
                texts[text.key] = text.value
            
            # Получаем тексты бота
            for text in BotText.objects.filter(language=lang, is_active=True):
                texts[text.text_type] = text.content
            
            cache.set(cache_key, texts, self.cache_timeout)
            return texts
            
        except Exception as e:
            logging.error(f"Ошибка получения текстов для языка {lang}: {e}")
            return {}
    
    def save_texts_for_language(self, lang: str, texts: Dict[str, str]) -> bool:
        """Сохранение текстов для языка"""
        try:
            for key, value in texts.items():
                # Сохраняем в Text
                Text.objects.update_or_create(
                    lang=lang,
                    key=key,
                    defaults={'value': value}
                )
                
                # Сохраняем в BotText если это тип бота
                if key in self.TEXT_TYPES:
                    BotText.objects.update_or_create(
                        text_type=key,
                        language=lang,
                        version=1,
                        defaults={
                            'content': value,
                            'is_active': True,
                            'created_by': AdminUser.objects.first()  # Временно
                        }
                    )
            
            # Очищаем кеш
            cache.delete(f"texts_{lang}")
            
            return True
            
        except Exception as e:
            logging.error(f"Ошибка сохранения текстов для языка {lang}: {e}")
            return False
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Получение списка доступных языков"""
        languages = []
        
        for code, info in self.SUPPORTED_LANGUAGES.items():
            # Проверяем, есть ли тексты для этого языка
            has_texts = Text.objects.filter(lang=code).exists() or BotText.objects.filter(language=code).exists()
            
            languages.append({
                'code': code,
                'name': info['name'],
                'flag': info['flag'],
                'available': has_texts
            })
        
        return languages
    
    def get_text_preview(self, text: str, target_lang: str) -> Optional[str]:
        """Предварительный перевод текста"""
        return self.translate_text(text, target_lang)
    
    def bulk_translate(self, texts: Dict[str, str], target_lang: str, source_lang: str = 'ru') -> Dict[str, str]:
        """Массовый перевод текстов"""
        if not TRANSLATION_AVAILABLE:
            return {}
        
        translated = {}
        
        for key, text in texts.items():
            translated_text = self.translate_text(text, target_lang, source_lang)
            if translated_text:
                translated[key] = translated_text
        
        return translated


# Создаем глобальный экземпляр
translation_service = TranslationService()
