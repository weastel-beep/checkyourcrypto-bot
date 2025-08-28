"""
Сервисы для работы с данными Check Your Crypto
"""
import logging
import secrets
import string
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from .models import User, Check, Text, Setting, CheckType, BotText
from .config import settings
from .error_handling import (
    get_retry_decorator,
    http_circuit_breaker,
    db_circuit_breaker,
    ErrorHandler,
    create_timeout_decorator,
    RetryConfig,
)

logger = logging.getLogger(__name__)


def get_api_base_url() -> str:
    """Получить базовый URL API"""
    # Используем URL из конфигурации без изменений
    base_url = settings.admin_api_url.rstrip("/")
    logger.info(f"🔍 get_api_base_url: settings.admin_api_url = {settings.admin_api_url}")
    logger.info(f"🔍 get_api_base_url: возвращаем base_url = {base_url}")
    return base_url


class UserService:
    """Сервис для работы с пользователями через production API"""

    API_BASE_URL = get_api_base_url() + "/api"

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_or_create_user(session: AsyncSession, tg_id: int, language: str = "ru", username: str = None) -> User:
        """Получить пользователя или создать нового через API"""
        try:
            # Сначала пытаемся получить существующего пользователя
            user = await UserService.get_user_by_tg_id(session, tg_id)

            if user:
                # Обновляем username если изменился
                if username and user.username != username:
                    # TODO: Добавить API endpoint для обновления username
                    user.username = username
                return user

            # Создаем нового пользователя через API
            async with aiohttp.ClientSession() as http_session:
                user_data = {
                    "tg_id": tg_id,
                    "username": username,
                    "language": language,
                    "balance": 0.0,
                    "referral_code": UserService._generate_referral_code(),
                    "is_blocked": False,
                }

                async with http_session.post(f"{UserService.API_BASE_URL}/users", json=user_data) as response:
                    if response.status == 201 or response.status == 200:
                        result = await response.json()
                        # Создаем объект User из API ответа
                        user = User(
                            tg_id=result["tg_id"],
                            username=result["username"],
                            language=result["language"],
                            balance=Decimal(str(result["balance"])),
                            referral_code=result["referral_code"],
                            is_blocked=result["is_blocked"],
                            created_at=datetime.fromisoformat(result["created_at"].replace("Z", "+00:00")),
                            updated_at=datetime.fromisoformat(result["updated_at"].replace("Z", "+00:00")),
                        )
                        logger.info(f"✅ Пользователь создан через API: {user.tg_id}")
                        return user
                    else:
                        error_msg = f"API error: {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), "создание пользователя", tg_id)
                        raise Exception(error_msg)

        except Exception as e:
            ErrorHandler.log_error(e, "создание/получение пользователя через API", tg_id)
            raise

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> Optional[User]:
        """Получить пользователя по tg_id через API"""
        try:
            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(f"{UserService.API_BASE_URL}/users/{tg_id}") as response:
                    if response.status == 200:
                        result = await response.json()
                        # Создаем объект User из API ответа
                        user = User(
                            tg_id=result["tg_id"],
                            username=result["username"],
                            language=result["language"],
                            balance=Decimal(str(result["balance"])),
                            referral_code=result["referral_code"],
                            is_blocked=result["is_blocked"],
                            created_at=datetime.fromisoformat(result["created_at"].replace("Z", "+00:00")),
                            updated_at=datetime.fromisoformat(result["updated_at"].replace("Z", "+00:00")),
                        )
                        logger.info(f"✅ Пользователь получен через API: {user.tg_id}, баланс: {user.balance}")
                        return user
                    elif response.status == 404:
                        logger.info(f"Пользователь не найден в API: {tg_id}")
                        return None
                    else:
                        error_msg = f"API error: {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), "получение пользователя", tg_id)
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение пользователя по tg_id {tg_id} через API")
            return None

    @staticmethod
    @get_retry_decorator("db")
    async def update_user_language(session: AsyncSession, tg_id: int, language: str) -> bool:
        """Обновить язык пользователя"""
        stmt = update(User).where(User.tg_id == tg_id).values(language=language)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    @get_retry_decorator("db")
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
    @get_retry_decorator("db")
    async def update_last_free_check(session: AsyncSession, user: User):
        """Обновить время последней бесплатной проверки"""
        user.last_free_check = datetime.utcnow()
        await session.commit()

    @staticmethod
    @get_retry_decorator("db")
    async def add_balance(session: AsyncSession, user: User, amount: Decimal) -> None:
        """Пополнить баланс пользователя"""
        user.balance += amount
        await session.commit()

    @staticmethod
    @get_retry_decorator("db")
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
        return getattr(user, "is_blocked", False)

    @staticmethod
    def _generate_referral_code(length: int = 8) -> str:
        """Генерировать реферальный код"""
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))


class CheckService:
    """Сервис для работы с проверками"""

    @staticmethod
    @get_retry_decorator("db")
    async def create_check(
        session: AsyncSession, user_id: int, address: str, chain: str, check_type: CheckType, result: Optional[Dict] = None
    ) -> Check:
        """Создать новую проверку"""
        check = Check(user_id=user_id, address=address, chain=chain, type=check_type, result=result)
        session.add(check)
        await session.commit()
        await session.refresh(check)
        return check

    @staticmethod
    @get_retry_decorator("db")
    async def get_user_checks(session: AsyncSession, user_id: int, limit: int = 10) -> List[Check]:
        """Получить проверки пользователя"""
        stmt = select(Check).where(Check.user_id == user_id).order_by(Check.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    @get_retry_decorator("db")
    async def get_check_by_id(session: AsyncSession, check_id: int) -> Optional[Check]:
        """Получить проверку по ID"""
        stmt = select(Check).where(Check.id == check_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    @get_retry_decorator("db")
    async def get_checks_today(session: AsyncSession, user_id: int) -> int:
        """Получить количество проверок пользователя за сегодня"""
        today = datetime.utcnow().date()
        stmt = select(Check).where(Check.user_id == user_id, Check.created_at >= today)
        result = await session.execute(stmt)
        return len(result.scalars().all())


class TextService:
    """Сервис для работы с текстами через API"""

    @staticmethod
    def get_api_base_url() -> str:
        """Получить базовый URL API из конфига"""
        return get_api_base_url()

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_text(session: AsyncSession, key: str, language: str = "ru", user_id: int = None, additional_data: dict = None) -> str:
        """Получить текст по ключу и языку через API"""
        try:
            import aiohttp

            logger.info(f"🔍 TextService: Запрашиваем текст '{key}' для языка '{language}'")

            async with aiohttp.ClientSession() as http_session:
                # Получаем все тексты через API
                api_url = f"{TextService.get_api_base_url()}/api/texts"
                print(f"🔍 TextService: Запрашиваем API: {api_url}")
                async with http_session.get(api_url) as response:
                    print(f"🔍 TextService: API ответ статус: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        texts = data.get("texts", [])
                        print(f"🔍 TextService: Получено {len(texts)} текстов через API")
                        print(f"🔍 TextService: Первые 3 текста: {texts[:3]}")
                        logger.info(f"🔍 TextService: Получено {len(texts)} текстов через API")

                        # Ищем нужный текст
                        for text in texts:
                            if text.get("category") == key and text.get("language") == language and text.get("is_active"):
                                logger.info(f"✅ Текст '{key}' получен через API для языка {language}")
                                content = text.get("content", "")
                                logger.info(f"🔍 TextService: Контент текста '{key}': {content[:100]}...")
                                return await TextService._replace_price_placeholders(session, content, user_id, additional_data)

                        # Если не найден по category, ищем по key (для обратной совместимости)
                        for text in texts:
                            if text.get("key") == key and text.get("language") == language and text.get("is_active"):
                                logger.info(f"✅ Текст '{key}' получен через API по key для языка {language}")
                                content = text.get("content", "")
                                logger.info(f"🔍 TextService: Контент текста '{key}': {content[:100]}...")
                                return await TextService._replace_price_placeholders(session, content, user_id, additional_data)

                        # Если не найден в bot_texts, ищем в старой таблице
                        for text in texts:
                            if text.get("key") == key and text.get("lang") == language:
                                logger.warning(
                                    f"⚠️ Текст '{key}' получен из старой таблицы через API - мигрируйте в Bot Flow Designer"
                                )
                                content = text.get("value", "")
                                logger.info(f"🔍 TextService: Контент из старой таблицы '{key}': {content[:100]}...")
                                return await TextService._replace_price_placeholders(session, content, user_id, additional_data)

                        print(f"❌ TextService: Текст '{key}' не найден через API")
                        print(f"🔍 TextService: Доступные категории: {[t.get('category') for t in texts if t.get('category')]}")
                        print(f"🔍 TextService: Доступные ключи: {[t.get('key') for t in texts if t.get('key')]}")
                        logger.error(f"❌ Текст '{key}' не найден через API - настройте через Bot Flow Designer")
                        logger.info(
                            f"🔍 TextService: Доступные категории: {[t.get('category') for t in texts if t.get('category')]}"
                        )
                        return key
                    else:
                        error_msg = f"API вернул статус {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), f"получение текста '{key}'", user_id)
                        return key

        except Exception as e:
            ErrorHandler.log_error(e, f"получение текста '{key}' через API", user_id)
            return key

    @staticmethod
    async def _replace_price_placeholders(session: AsyncSession, text: str, user_id: int = None, additional_data: dict = None) -> str:
        """Автоматически заменить все плейсхолдеры в тексте"""
        try:
            from .services_package.placeholder_service import PlaceholderService

            # Если есть user_id, заменяем все плейсхолдеры
            if user_id:
                logger.info(f"🔍 TextService: Заменяем плейсхолдеры для пользователя {user_id}")
                result = await PlaceholderService.replace_placeholders(session, text, user_id, additional_data)
                logger.info(f"✅ TextService: Плейсхолдеры заменены, результат: {result[:100]}...")
                return result

            # Иначе только базовые плейсхолдеры без пользователя
            paid_check_price = await SettingService.get_paid_check_price(session)
            print(f"🔍 TextService: Получена цена: {paid_check_price}")
            text = text.replace("{paid_check_price}", str(paid_check_price))
            print(f"🔍 TextService: Текст после замены: {text[:200]}...")

            return text
        except Exception as e:
            ErrorHandler.log_error(e, "замена плейсхолдеров", user_id)
            # В случае ошибки возвращаем текст как есть
            return text

    @staticmethod
    @get_retry_decorator("db")
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
        """Синхронизировать текст из BotText в Text - УДАЛЕНО согласно константной архитектуре"""
        logger.warning(f"⚠️ Синхронизация отключена для ключа {key} ({language}) - используйте новую админку")
        return

    @staticmethod
    def get_default_texts() -> Dict[str, str]:
        """Получить тексты по умолчанию - УДАЛЕНО согласно константной архитектуре"""
        logger.warning("⚠️ get_default_texts() отключен - используйте Bot Flow Designer")
        return {}

    @staticmethod
    @get_retry_decorator("db")
    async def get_menu(session: AsyncSession, menu_key: str, language: str = "ru") -> Optional[Dict]:
        """Получить конфигурацию меню из базы данных"""
        try:
            # Пытаемся получить меню из BotText
            stmt = select(BotText).where(
                BotText.category == f"menu_{menu_key}", BotText.language == language, BotText.is_active == True
            )
            result = await session.execute(stmt)
            menu_text = result.scalar_one_or_none()

            if menu_text:
                # Парсим JSON конфигурацию меню
                import json

                try:
                    menu_config = json.loads(menu_text.content)
                    logger.info(f"✅ Меню '{menu_key}' получено из BotText для языка {language}")
                    return menu_config
                except json.JSONDecodeError:
                    logger.error(f"❌ Ошибка парсинга JSON для меню '{menu_key}': {menu_text.content}")
                    return None

            logger.warning(f"⚠️ Меню '{menu_key}' не найдено в BotText для языка {language}")
            return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение меню '{menu_key}'")
            return None


class SettingService:
    """Сервис для работы с настройками через API"""

    API_BASE_URL = get_api_base_url()

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_paid_check_price(session: AsyncSession) -> float:
        """Получить стоимость платной проверки через API"""
        try:
            print(f"🔍 SettingService: Запрашиваем цену платной проверки")
            # Получаем цену через API
            paid_check_price = await SettingService.get_setting(session, "paid_check_price")
            print(f"🔍 SettingService: Получена цена из API: {paid_check_price}")
            if paid_check_price:
                result = float(paid_check_price)
                print(f"🔍 SettingService: Возвращаем цену: {result}")
                return result

            # Если нет в API, возвращаем значение по умолчанию
            print(f"🔍 SettingService: Цена не найдена, возвращаем 1.0")
            return 1.0
        except Exception as e:
            ErrorHandler.log_error(e, "получение стоимости платной проверки через API")
            return 1.0

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_setting(session: AsyncSession, key: str) -> Optional[str]:
        """Получить значение настройки через API"""
        try:
            import aiohttp

            url = f"{SettingService.API_BASE_URL}/api/settings/{key}"
            print(f"🔍 SettingService: Запрашиваем настройку: {url}")

            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("value")
                    elif response.status == 404:
                        logger.warning(f"⚠️ Настройка '{key}' не найдена через API")
                        return None
                    else:
                        error_msg = f"API вернул статус {response.status} для настройки '{key}'"
                        ErrorHandler.log_error(Exception(error_msg), f"получение настройки '{key}'")
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение настройки '{key}' через API")
            return None

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def set_setting(session: AsyncSession, key: str, value: str):
        """Установить значение настройки через API"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as http_session:
                async with http_session.put(
                    f"{SettingService.API_BASE_URL}/api/settings/{key}", json={"value": value}
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Настройка '{key}' обновлена через API")
                    else:
                        error_msg = f"Ошибка обновления настройки '{key}' через API: {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), f"обновление настройки '{key}'")

        except Exception as e:
            ErrorHandler.log_error(e, f"установка настройки '{key}' через API")

    @staticmethod
    @get_retry_decorator("db")
    async def block_user(session: AsyncSession, user: User, reason: str = None) -> bool:
        """Заблокировать пользователя"""
        try:
            user.is_blocked = True
            await session.commit()
            logger.info(f"Пользователь {user.tg_id} заблокирован. Причина: {reason}")
            return True
        except Exception as e:
            ErrorHandler.log_error(e, f"блокировка пользователя {user.tg_id}")
            await session.rollback()
            return False

    @staticmethod
    @get_retry_decorator("db")
    async def unblock_user(session: AsyncSession, user: User) -> bool:
        """Разблокировать пользователя"""
        try:
            user.is_blocked = False
            await session.commit()
            logger.info(f"Пользователь {user.tg_id} разблокирован")
            return True
        except Exception as e:
            ErrorHandler.log_error(e, f"разблокировка пользователя {user.tg_id}")
            await session.rollback()
            return False

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
            "btc": "₿",
            "eth": "Ξ",
            "tron": "TRX",
            "solana": "◎",
            "optimism": "OP",
            "cronos": "CRO",
            "bsc": "BNB",
            "gnosis": "XDAI",
            "polygon": "MATIC",
            "manta": "MANTA",
            "bittorrent": "BTT",
            "fantom": "FTM",
            "boba": "BOBA",
            "zksync": "ZK",
            "clv": "CLV",
            "polygonzkevm": "zkEVM",
            "wemix": "WEMIX",
            "moonbeam": "GLMR",
            "moonriver": "MOVR",
            "mantle": "MNT",
            "base": "BASE",
            "arbitrum": "ARB",
            "celo": "CELO",
            "avalanche": "AVAX",
            "linea": "LINEA",
            "blast": "BLAST",
            "aurora": "AURORA",
        }
        normalized = ChainService.normalize_chain(chain)
        return emojis.get(normalized, "🔗")

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


class ScenarioService:
    """Сервис для работы со сценариями Bot Flow Designer"""

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_default_scenario() -> Optional[Dict]:
        """Получить сценарий по умолчанию для проверки адреса"""
        try:
            import aiohttp

            # Получаем сценарий из API
            api_url = "https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com/api/scenarios/active/default"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        scenario = await response.json()
                        logger.info(f"✅ Получен сценарий: {scenario.get('name', 'Unknown')}")
                        return scenario
                    else:
                        error_msg = f"Ошибка получения сценария: {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), "получение сценария")
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, "получение сценария")
            return None

    @staticmethod
    @get_retry_decorator("http")
    @create_timeout_decorator(RetryConfig.HTTP_TIMEOUT)
    async def get_scenario_by_id(scenario_id: int) -> Optional[Dict]:
        """Получить сценарий по ID"""
        try:
            import aiohttp

            api_url = f"https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com/api/scenarios/{scenario_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        scenario = await response.json()
                        logger.info(f"✅ Получен сценарий {scenario_id}: {scenario.get('name', 'Unknown')}")
                        return scenario
                    else:
                        error_msg = f"Ошибка получения сценария {scenario_id}: {response.status}"
                        ErrorHandler.log_error(Exception(error_msg), f"получение сценария {scenario_id}")
                        return None

        except Exception as e:
            ErrorHandler.log_error(e, f"получение сценария {scenario_id}")
            return None

    @staticmethod
    async def execute_scenario_stage(scenario: Dict, current_stage_name: str, user_data: Dict) -> Optional[Dict]:
        """Выполнить этап сценария и определить следующий этап"""
        try:
            if not scenario or not scenario.get("stages"):
                logger.warning("Сценарий пустой или не содержит этапов")
                return None

            # Находим текущий этап
            current_stage = None
            for stage in scenario["stages"]:
                if stage["name"] == current_stage_name:
                    current_stage = stage
                    break

            if not current_stage:
                logger.warning(f"Этап '{current_stage_name}' не найден в сценарии")
                return None

            # Проверяем условия этапа
            for condition in current_stage.get("conditions", []):
                if ScenarioService._evaluate_condition(condition, user_data):
                    # Условие выполнено - возвращаем действие
                    return {
                        "action": condition["action"],
                        "target_stage": condition["target_stage"],
                        "message_text": condition.get("message_text"),
                        "parameters": condition.get("parameters", {}),
                    }

            # Если условия не выполнены, возвращаем следующий этап по порядку
            current_index = current_stage["order_index"]
            next_stage = None
            for stage in scenario["stages"]:
                if stage["order_index"] > current_index:
                    next_stage = stage
                    break

            if next_stage:
                return {"action": "next_stage", "target_stage": next_stage["name"], "message_text": None, "parameters": {}}

            return None

        except Exception as e:
            ErrorHandler.log_error(e, "выполнение этапа сценария")
            return None

    @staticmethod
    def _evaluate_condition(condition: Dict, user_data: Dict) -> bool:
        """Оценить условие на основе данных пользователя"""
        try:
            condition_type = condition.get("type", "")

            if condition_type == "balance_insufficient":
                balance = user_data.get("balance", 0)
                return balance < 3.4

            elif condition_type == "balance_sufficient":
                balance = user_data.get("balance", 0)
                return balance >= 3.4

            elif condition_type == "address_valid":
                return user_data.get("address_valid", False)

            elif condition_type == "address_invalid":
                return not user_data.get("address_valid", True)

            elif condition_type == "free_limit_exceeded":
                return user_data.get("free_limit_exceeded", False)

            elif condition_type == "user_blocked":
                return user_data.get("is_blocked", False)

            elif condition_type == "Баланс < 3.4 USDT":
                balance = user_data.get("balance", 0)
                return balance < 3.4

            elif condition_type == "Баланс >= 3.4 USDT":
                balance = user_data.get("balance", 0)
                return balance >= 3.4

            # По умолчанию условие не выполнено
            return False

        except Exception as e:
            ErrorHandler.log_error(e, "оценка условия")
            return False

    @staticmethod
    async def get_stage_text(scenario: Dict, stage_name: str, language: str = "ru") -> Optional[str]:
        """Получить текст для этапа"""
        try:
            if not scenario or not scenario.get("stages"):
                return None

            # Находим этап
            stage = None
            for s in scenario["stages"]:
                if s["name"] == stage_name:
                    stage = s
                    break

            if not stage:
                return None

            text_key = stage.get("text_key")
            if not text_key:
                return None

            # Получаем текст из TextService
            from .database import async_session_maker

            async with async_session_maker() as session:
                text = await TextService.get_text(session, text_key, language)
                return text

        except Exception as e:
            ErrorHandler.log_error(e, "получение текста этапа")
            return None
