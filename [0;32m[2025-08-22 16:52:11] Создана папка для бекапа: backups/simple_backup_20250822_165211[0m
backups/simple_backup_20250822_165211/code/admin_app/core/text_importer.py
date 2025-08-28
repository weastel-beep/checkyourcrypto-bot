"""
Скрипт для импорта существующих текстов из бота в админку
"""
import asyncio
from typing import Dict, List, Tuple

# Проверяем доступность Django
try:
    import os
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        # Django не настроен
        raise ImportError("Django settings not configured")
    
    from django.db import transaction
    from django.utils import timezone
    from .models import BotText, AdminUser
    DJANGO_AVAILABLE = True
except ImportError:
    # Django недоступен - создаем заглушки для IDE
    DJANGO_AVAILABLE = False
    transaction = None
    timezone = None
    BotText = None
    AdminUser = None


class TextImporter:
    """Импортер текстов из бота в админку"""
    
    # Существующие тексты из бота
    BOT_TEXTS = {
        'welcome': {
            'ru': """👋 **CheckYourCrypto AI** — умный бот для защиты ваших криптоактивов.

🤖 AI мгновенно выявляет риски, санкции и подозрительные адреса.
🛡️ Безопасные сделки начинаются здесь.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Почему это важно?**

Вы можете не подозревать, что получили средства с санкционного или сомнительного адреса.

На централизованных биржах такие активы часто замораживаются или блокируются.

**Проверка = ваша уверенность и защита в мире блокчейна.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **Что может бот?**

1️⃣ **Базовая проверка (Free)** — мгновенный уровень риска: низкий / средний / высокий.

2️⃣ **Глубокий AI-анализ (1 USDT)** — расширенный отчёт: источники риска, санкции, подозрительные паттерны и рекомендации.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 **Просто вставьте криптовалютный адрес, и мы сразу покажем доступные варианты проверки.**

**Используйте кнопки ниже для навигации:**""",
            'en': """👋 **CheckYourCrypto AI** — smart bot for protecting your crypto assets.

🤖 AI instantly detects risks, sanctions, and suspicious addresses.
🛡️ Safe transactions start here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Why is this important?**

You might not suspect that you received funds from a sanctioned or suspicious address.

On centralized exchanges, such assets are often frozen or blocked.

**Verification = your confidence and protection in the blockchain world.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **What can the bot do?**

1️⃣ **Basic Check (Free)** — instant risk level: low / medium / high.

2️⃣ **Deep AI Analysis (1 USDT)** — detailed report: risk sources, sanctions, suspicious patterns and recommendations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 **Just paste a cryptocurrency address, and we'll immediately show available verification options.**

**Use the buttons below for navigation:**"""
        },
        'main_menu': {
            'ru': """🔍 **Проверка криптоадреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Баланс:** {balance} USDT

✅ **Базовая проверка** — базовая оценка риска, 1 раз в минуту
🛡️ **Глубокий AI-анализ** — 1 USDT
・ Детальный отчёт о рисках
・ Санкции, подозрительные паттерны
・ Рекомендации от AI

📌 **Как это работает:**
1️⃣ Отправьте криптоадрес (BTC, ETH, USDT и др.)
2️⃣ Мы определим блокчейн автоматически
3️⃣ Выберите тип проверки:
   ✅ Базовая (базовая оценка риска - бесплатно)
   🛡️ AI-анализ (глубокая аналитика 1 USD)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 **Отправьте адрес для проверки**""",
            'en': """🔍 **Crypto Address Check**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Balance:** {balance} USDT

✅ **Basic Check** — basic risk assessment, once per minute
🛡️ **Deep AI Analysis** — 1 USDT
・ Detailed risk report
・ Sanctions and suspicious patterns
・ AI recommendations

📌 **How it works:**
1️⃣ Send a crypto address (BTC, ETH, USDT, etc.)
2️⃣ We'll automatically determine the blockchain
3️⃣ Choose verification type:
   ✅ Basic (basic risk assessment - free)
   🛡️ AI Analysis (deep analytics 1 USD)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 **Send address for verification**"""
        },
        'check': {
            'ru': """🔍 **Проверка адреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** {address}
⛓️ **Блокчейн:** {chain}
💳 **Баланс:** {balance} USDT

Выберите тип проверки:""",
            'en': """🔍 **Address Check**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Address:** {address}
⛓️ **Blockchain:** {chain}
💳 **Balance:** {balance} USDT

Select check type:"""
        },
        'check_choice': {
            'ru': """🔍 **Выберите тип проверки адреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** {address}
⛓️ **Блокчейн:** {chain}
💰 **Баланс:** {balance} USDT

Выберите тип проверки:""",
            'en': """🔍 **Select Address Check Type**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Address:** {address}
⛓️ **Blockchain:** {chain}
💰 **Balance:** {balance} USDT

Select check type:"""
        },
        'check_result': {
            'ru': """🔍 **Результат проверки адреса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Адрес:** {address}
⛓️ **Блокчейн:** {chain}
🔍 **Тип проверки:** {check_type}

📊 **Результат анализа:**
{result}""",
            'en': """🔍 **Address Check Result**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Address:** {address}
⛓️ **Blockchain:** {chain}
🔍 **Check Type:** {check_type}

📊 **Analysis Result:**
{result}"""
        },
        'payment': {
            'ru': """💰 **Пополнение баланса**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Текущий баланс:** {balance} USDT

Выберите способ пополнения:""",
            'en': """💰 **Add Balance**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Current Balance:** {balance} USDT

Select payment method:"""
        },
        'error': {
            'ru': """❌ **Произошла ошибка**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{error}

Попробуйте еще раз или обратитесь в поддержку.""",
            'en': """❌ **An error occurred**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{error}

Try again or contact support."""
        },
        'help': {
            'ru': """📁 **Часто задаваемые вопросы**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **Как работает проверка?**
Мы анализируем адрес через MetaSleuth API, проверяя его на связи с мошенническими схемами, санкциями и другими рисками.

❓ **Сколько стоит детальная проверка?**
Детальная проверка стоит 1 USDT и предоставляет расширенный анализ с процентными показателями.

❓ **Какие блокчейны поддерживаются?**
BTC, ETH, TRON, Solana, BSC, Polygon, Arbitrum и многие другие.

❓ **Безопасны ли мои данные?**
Мы не храним личные данные, только адреса для проверки.""",
            'en': """📁 **Frequently Asked Questions**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **How does the check work?**
We analyze the address through MetaSleuth API, checking it for connections with fraudulent schemes, sanctions and other risks.

❓ **How much does detailed check cost?**
Detailed check costs $1 and provides extended analysis with percentage indicators.

❓ **Which blockchains are supported?**
BTC, ETH, TRON, Solana, BSC, Polygon, Arbitrum and many others.

❓ **Are my data safe?**
We do not store personal data, only addresses for verification."""
        },
        'settings': {
            'ru': """⚙️ **Настройки**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 **Язык:** {language}
💰 **Баланс:** {balance} USDT
🔍 **Проверок сегодня:** {checks_today}

Выберите настройку для изменения:""",
            'en': """⚙️ **Settings**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 **Language:** {language}
💰 **Balance:** {balance} USDT
🔍 **Checks today:** {checks_today}

Select setting to change:"""
        },
        'insufficient_balance': {
            'ru': """❌ **Недостаточно средств**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Текущий баланс:** {balance} USDT
💰 **Требуется:** {required} USDT

Пополните баланс для детальной проверки.""",
            'en': """❌ **Insufficient Balance**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **Current Balance:** {balance} USDT
💰 **Required:** {required} USDT

Add funds for detailed check."""
        },
        'user_blocked': {
            'ru': """🚫 **Доступ заблокирован**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ваш аккаунт был заблокирован администратором.

Причина: {reason}

Для разблокировки обратитесь в поддержку.""",
            'en': """🚫 **Access Blocked**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your account has been blocked by administrator.

Reason: {reason}

Contact support to unblock your account."""
        }
    }

    @classmethod
    def import_all_texts(cls):
        """Импортировать все тексты из бота в админку"""
        if not DJANGO_AVAILABLE:
            print("❌ Django недоступен. Импорт текстов невозможен.")
            return False
            
        try:
            with transaction.atomic():
                imported_count = 0
                
                for category, languages in cls.BOT_TEXTS.items():
                    for language, content in languages.items():
                        # Проверяем, существует ли уже такой текст
                        existing_text = BotText.objects.filter(
                            category=category,
                            language=language,
                            is_active=True
                        ).first()
                        
                        if existing_text:
                            # Обновляем существующий текст
                            existing_text.content = content
                            existing_text.updated_at = timezone.now()
                            existing_text.save()
                            print(f"✅ Обновлен текст: {category} ({language})")
                        else:
                            # Создаем новый текст
                            BotText.objects.create(
                                category=category,
                                language=language,
                                content=content,
                                is_active=True,
                                version=1
                            )
                            print(f"✅ Создан новый текст: {category} ({language})")
                        
                        imported_count += 1
                
                print(f"🎉 Импортировано {imported_count} текстов")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка импорта текстов: {e}")
            return False

    @classmethod
    def get_texts_by_category(cls, category: str) -> Dict[str, str]:
        """Получить тексты для категории на всех языках"""
        if not DJANGO_AVAILABLE:
            # Возвращаем дефолтные тексты если Django недоступен
            return cls.BOT_TEXTS.get(category, {})
            
        texts = {}
        for language in ['ru', 'en']:
            text_obj = BotText.objects.filter(
                category=category,
                language=language,
                is_active=True
            ).first()
            
            if text_obj:
                texts[language] = text_obj.content
            else:
                # Возвращаем дефолтный текст если нет в БД
                texts[language] = cls.BOT_TEXTS.get(category, {}).get(language, '')
        
        return texts

    @classmethod
    def get_languages(cls) -> List[str]:
        """Получить список поддерживаемых языков"""
        return ['ru', 'en']
