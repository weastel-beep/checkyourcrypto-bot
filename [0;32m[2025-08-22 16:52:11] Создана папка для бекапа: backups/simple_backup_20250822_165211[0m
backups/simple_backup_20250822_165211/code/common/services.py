"""
Сервисы для работы с данными Check Your Crypto
"""
import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from .models import User, Check, Text, Setting, CheckType
from .config import settings

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_or_create_user(session: AsyncSession, tg_id: int, language: str = "ru", username: str = None) -> User:
        """Получить или создать пользователя"""
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            # Создаем нового пользователя
            referral_code = UserService._generate_referral_code()
            user = User(
                tg_id=tg_id,
                username=username,
                language=language,
                referral_code=referral_code,
                is_blocked=False  # Новые пользователи не заблокированы
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Создан новый пользователь: {tg_id}")
        else:
            # Обновляем username если он изменился
            if username and user.username != username:
                user.username = username
                await session.commit()
                logger.info(f"Обновлен username пользователя {tg_id}: {username}")
        
        return user
    
    @staticmethod
    async def update_user_language(session: AsyncSession, tg_id: int, language: str) -> bool:
        """Обновить язык пользователя"""
        stmt = update(User).where(User.tg_id == tg_id).values(language=language)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_user_by_referral_code(session: AsyncSession, referral_code: str) -> Optional[User]:
        """Получить пользователя по реферальному коду"""
        stmt = select(User).where(User.referral_code == referral_code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def can_use_free_check(session: AsyncSession, user: User) -> tuple[bool, Optional[int]]:
        """Проверить, может ли пользователь использовать бесплатную проверку"""
        from .check_limits import check_limits
        return check_limits.can_perform_free_check(user)
    
    @staticmethod
    async def update_last_free_check(session: AsyncSession, user: User):
        """Обновить время последней бесплатной проверки"""
        user.last_free_check = datetime.utcnow()
        await session.commit()
    
    @staticmethod
    async def add_balance(session: AsyncSession, user: User, amount: Decimal) -> None:
        """Пополнить баланс пользователя"""
        user.balance += amount
        await session.commit()
    
    @staticmethod
    async def deduct_balance(session: AsyncSession, user: User, amount: Decimal) -> bool:
        """Списать средства с баланса пользователя"""
        if user.balance < amount:
            return False
        
        user.balance -= amount
        await session.commit()
        return True
    
    @staticmethod
    def is_user_blocked(user: User) -> bool:
        """Проверить, заблокирован ли пользователь"""
        return getattr(user, 'is_blocked', False)
    
    @staticmethod
    async def block_user(session: AsyncSession, user: User, reason: str = None) -> bool:
        """Заблокировать пользователя"""
        try:
            user.is_blocked = True
            await session.commit()
            logger.info(f"Пользователь {user.tg_id} заблокирован. Причина: {reason}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при блокировке пользователя {user.tg_id}: {e}")
            await session.rollback()
            return False
    
    @staticmethod
    async def unblock_user(session: AsyncSession, user: User) -> bool:
        """Разблокировать пользователя"""
        try:
            user.is_blocked = False
            await session.commit()
            logger.info(f"Пользователь {user.tg_id} разблокирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка при разблокировке пользователя {user.tg_id}: {e}")
            await session.rollback()
            return False
    
    @staticmethod
    def _generate_referral_code(length: int = 8) -> str:
        """Сгенерировать реферальный код"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class CheckService:
    """Сервис для работы с проверками"""
    
    @staticmethod
    async def create_check(
        session: AsyncSession,
        user_id: int,
        address: str,
        chain: str,
        check_type: CheckType,
        result: Optional[Dict] = None
    ) -> Check:
        """Создать новую проверку"""
        check = Check(
            user_id=user_id,
            address=address,
            chain=chain,
            type=check_type,
            result=result
        )
        session.add(check)
        await session.commit()
        await session.refresh(check)
        return check
    
    @staticmethod
    async def get_user_checks(session: AsyncSession, user_id: int, limit: int = 10) -> List[Check]:
        """Получить проверки пользователя"""
        stmt = (
            select(Check)
            .where(Check.user_id == user_id)
            .order_by(Check.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_check_by_id(session: AsyncSession, check_id: int) -> Optional[Check]:
        """Получить проверку по ID"""
        stmt = select(Check).where(Check.id == check_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_checks_today(session: AsyncSession, user_id: int) -> int:
        """Получить количество проверок пользователя за сегодня"""
        today = datetime.utcnow().date()
        stmt = (
            select(Check)
            .where(
                Check.user_id == user_id,
                Check.created_at >= today
            )
        )
        result = await session.execute(stmt)
        return len(result.scalars().all())


class TextService:
    """Сервис для работы с текстами (мультиязычность)"""
    
    @staticmethod
    async def get_text(session: AsyncSession, key: str, language: str = "ru") -> str:
        """Получить текст по ключу и языку"""
        # Сначала пытаемся получить из основной таблицы
        stmt = select(Text).where(Text.key == key, Text.lang == language)
        result = await session.execute(stmt)
        text_obj = result.scalar_one_or_none()
        
        if text_obj:
            return text_obj.value
        
        # Если текст не найден, пытаемся синхронизировать из BotText
        await TextService.sync_from_bot_texts(session, key, language)
        
        # Повторно пытаемся получить текст
        stmt = select(Text).where(Text.key == key, Text.lang == language)
        result = await session.execute(stmt)
        text_obj = result.scalar_one_or_none()
        
        if text_obj:
            return text_obj.value
        
        # Если текст не найден, возвращаем ключ
        return key
    
    @staticmethod
    async def set_text(session: AsyncSession, key: str, value: str, language: str = "ru"):
        """Установить текст по ключу и языку"""
        stmt = select(Text).where(Text.key == key, Text.lang == language)
        result = await session.execute(stmt)
        text_obj = result.scalar_one_or_none()
        
        if text_obj:
            text_obj.value = value
        else:
            text_obj = Text(key=key, value=value, lang=language)
            session.add(text_obj)
        
        await session.commit()
    
    @staticmethod
    async def sync_from_bot_texts(session: AsyncSession, key: str, language: str):
        """Синхронизировать текст из BotText в Text"""
        try:
            # Импортируем Django ORM для работы с BotText
            import os
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
            django.setup()
            
            from admin_app.core.admin_models import BotText
            
            # Получаем активный текст из BotText
            bot_text = BotText.get_active_text(key, language)
            
            if bot_text:
                # Создаем или обновляем текст в основной таблице
                stmt = select(Text).where(Text.key == key, Text.lang == language)
                result = await session.execute(stmt)
                text_obj = result.scalar_one_or_none()
                
                if text_obj:
                    text_obj.value = bot_text.content
                else:
                    text_obj = Text(key=key, value=bot_text.content, lang=language)
                    session.add(text_obj)
                
                await session.commit()
                print(f"✅ Синхронизирован текст: {key} ({language})")
            
        except Exception as e:
            print(f"❌ Ошибка синхронизации текста {key} ({language}): {e}")
    
    @staticmethod
    def get_default_texts() -> Dict[str, str]:
        """Получить тексты по умолчанию"""
        return {
            "welcome": "Добро пожаловать в Check Your Crypto! 🔍\n\nПроверяйте криптовалютные адреса на безопасность и риски.",
            "main_menu": "Главное меню",
            "check_address": "🔍 Проверка",
            "add_balance": "💰 Пополнить",
            "profile": "👤 Личный кабинет",
            "faq": "📁 FAQ",
            "enter_address": "Введите адрес для проверки:",
            "select_chain": "Выберите блокчейн:",
            "checking_address": "🔎 Проверяю адрес ({chain})...",
            "check_result": "🔎 Адрес ({chain}): `{address}`\n\n🔹 Метка: {label}\n🔹 Риск: {risk}/5 {emoji} — {risk_description}\n\n❗ Детали блокировки:\n{block_details}\n\n🔗 Доп. информация:\n- Веб-сайт: {website}\n- Тип: {type}\n- Теги: {tags}",
            "paid_example": "────────────────────────\n🛡️ Защитите свои средства\n\n`Глубокий AI-анализ адреса с детальным отчетом рисков, процентным соотношением и рекомендациями для максимальной безопасности.`",
            "check_detailed": "Проверить детально",
            "insufficient_balance": "Недостаточно средств на балансе. Пополните баланс для детальной проверки.",
            "free_check_available": "✅ Бесплатная проверка доступна",
            "free_check_wait": "⏳ Следующая бесплатная проверка через {minutes} минут",
            "free_check_choice": "⏳ Следующая бесплатная проверка через {minutes} минут\n\nВыберите вариант:\n1️⃣ Подождать {minutes} минут для бесплатной проверки\n2️⃣ Пополнить баланс и сделать платную проверку сейчас",
            "balance_info": "💰 Баланс: {balance} USDT",
            "payment_methods": "Способы оплаты:",
            "payment_success": "✅ Платеж успешно обработан!",
            "payment_failed": "❌ Ошибка при обработке платежа",
            "profile_info": "👤 Личный кабинет\n\nID: {tg_id}\nБаланс: {balance} проверок\n📊 Проверок за сегодня: {checks_today}\nЯзык: {language}\n\n🔗 Реферальная программа: в разработке, скоро будет доступна",
            "referral_info": "Пригласите друзей и получите бонусы!\nВаш код: {referral_code}",
            "faq_content": "❓ Часто задаваемые вопросы\n\nQ: Как работает проверка?\nA: Мы анализируем адрес через MetaSleuth API на предмет рисков и подозрительной активности.\n\nQ: Сколько стоит глубокий AI-анализ?\nA: 1 проверка = 1 USDT.\n\nQ: Какие блокчейны поддерживаются?\nA: BTC, ETH, TRON, Solana и другие популярные сети.\n\nQ: Какие есть лимиты бесплатных проверок?\nA: Бесплатная проверка доступна раз в минуту. Пополнение баланса открывает доступ к глубокому AI-анализу.",
            "error_occurred": "❌ Произошла ошибка. Попробуйте позже.",
            "invalid_address": "❌ Неверный формат адреса.",
            "unsupported_chain": "❌ Неподдерживаемый блокчейн.",
            "user_blocked": "🚫 **Ваш аккаунт заблокирован**\n\n❌ Вы не можете использовать бота.\n\n📧 Для разблокировки обратитесь к администрации:\n• Email: support@checkyourcrypto.com\n• Telegram: @checkyourcrypto_support\n\n⚠️ **Причина блокировки:** Нарушение правил использования сервиса.",
        }


class SettingService:
    """Сервис для работы с настройками"""
    
    @staticmethod
    async def get_setting(session: AsyncSession, key: str) -> Optional[str]:
        """Получить значение настройки"""
        stmt = select(Setting).where(Setting.key == key)
        result = await session.execute(stmt)
        setting = result.scalar_one_or_none()
        return setting.value if setting else None
    
    @staticmethod
    async def set_setting(session: AsyncSession, key: str, value: str):
        """Установить значение настройки"""
        stmt = select(Setting).where(Setting.key == key)
        result = await session.execute(stmt)
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            session.add(setting)
        
        await session.commit()
    
    @staticmethod
    def get_default_settings() -> Dict[str, str]:
        """Получить настройки по умолчанию"""
        return {
            "show_paid_example": "true",
            "free_check_limit_minutes": str(settings.free_limit_minutes),
            "paid_check_price": "1.00",
            "referral_bonus": "0.50",
            "max_free_checks_per_day": "10",
        }


class ChainService:
    """Сервис для работы с блокчейнами"""
    
    @staticmethod
    def normalize_chain(chain: str) -> str:
        """Нормализовать название блокчейна"""
        return chain.lower().strip()
    
    @staticmethod
    def is_supported_chain(chain: str) -> bool:
        """Проверить, поддерживается ли блокчейн"""
        normalized = ChainService.normalize_chain(chain)
        return normalized in settings.supported_chains
    
    @staticmethod
    def get_chain_emoji(chain: str) -> str:
        """Получить эмодзи для блокчейна"""
        emojis = {
            'btc': '₿',
            'eth': 'Ξ',
            'tron': 'TRX',
            'solana': '◎',
            'optimism': 'OP',
            'cronos': 'CRO',
            'bsc': 'BNB',
            'gnosis': 'XDAI',
            'polygon': 'MATIC',
            'manta': 'MANTA',
            'bittorrent': 'BTT',
            'fantom': 'FTM',
            'boba': 'BOBA',
            'zksync': 'ZK',
            'clv': 'CLV',
            'polygonzkevm': 'zkEVM',
            'wemix': 'WEMIX',
            'moonbeam': 'GLMR',
            'moonriver': 'MOVR',
            'mantle': 'MNT',
            'base': 'BASE',
            'arbitrum': 'ARB',
            'celo': 'CELO',
            'avalanche': 'AVAX',
            'linea': 'LINEA',
            'blast': 'BLAST',
            'aurora': 'AURORA',
        }
        normalized = ChainService.normalize_chain(chain)
        return emojis.get(normalized, '🔗')
    
    @staticmethod
    def get_risk_emoji(risk: int) -> str:
        """Получить эмодзи для уровня риска"""
        if risk <= 1:
            return "🟢"
        elif risk <= 2:
            return "🟡"
        elif risk <= 3:
            return "🟠"
        elif risk <= 4:
            return "🔴"
        else:
            return "⚫"
    
    @staticmethod
    def get_risk_description(risk: int) -> str:
        """Получить описание уровня риска"""
        if risk == 1:
            return "🟢 Безопасно. Адрес чистый, рисков не выявлено."
        elif risk == 2:
            return "🟢 Низкий риск. Небольшие подозрительные связи, но критичных проблем нет."
        elif risk == 3:
            return "🟡 Средний риск. Есть заметные взаимодействия с сомнительными адресами, стоит быть осторожным."
        elif risk == 4:
            return "🟠 Высокий риск. Связан с мошенничеством, отмыванием или санкциями. Рекомендуется избегать."
        elif risk == 5:
            return "🔴 Критический риск. Прямое участие в криминальной или санкционной деятельности. Контакт категорически нежелателен."
        else:
            return "❓ Неизвестный уровень риска"
