"""
Сервис для автоматической замены плейсхолдеров в текстах
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PlaceholderService:
    """Сервис для автоматической замены плейсхолдеров в текстах"""

    # Список всех доступных плейсхолдеров
    AVAILABLE_PLACEHOLDERS = {
        # Пользовательские данные
        "{balance}": "Баланс пользователя в USDT",
        "{checks_count}": "Количество проверок пользователя",
        "{saved_amount}": "Сохраненная сумма пользователя",
        "{language}": "Язык пользователя",
        # Настройки системы
        "{paid_check_price}": "Стоимость платной проверки",
        # Данные проверки
        "{address}": "Адрес для проверки",
        "{chain}": "Блокчейн адреса",
        "{risk_level}": "Уровень риска",
        "{risk_score}": "Оценка риска",
        "{risk_details}": "Детали риска",
        "{recommendations}": "Рекомендации",
        "{check_time}": "Время проверки",
        "{time}": "Время ожидания",
        # Address Label API данные
        "{label}": "Метка адреса (например: Binance, Bittrex)",
        "{address_type}": "Тип адреса (exchange, wallet, mixer, etc.)",
        "{website}": "Веб-сайт связанный с адресом",
        "{address_status}": "Статус адреса (заблокирован, санкционирован, etc.)",
        # Платежи
        "{amount}": "Сумма платежа",
        "{required}": "Требуемая сумма",
        # Ошибки
        "{error_message}": "Сообщение об ошибке",
        "{description}": "Описание",
    }

    @staticmethod
    async def replace_placeholders(
        session: AsyncSession, text: str, user_id: int, additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        ГЛОБАЛЬНО: Автоматически находит и заменяет ВСЕ плейсхолдеры в тексте

        Args:
            session: Сессия БД
            text: Текст с плейсхолдерами
            user_id: ID пользователя
            additional_data: Дополнительные данные для замены

        Returns:
            Текст с замененными плейсхолдерами
        """
        try:
            from common.services import UserService, SettingService

            # 1. Находим ВСЕ плейсхолдеры в тексте
            placeholders = PlaceholderService.extract_placeholders_from_text(text)
            logger.info(f"🔍 Найдены плейсхолдеры: {placeholders}")

            if not placeholders:
                logger.info("✅ Плейсхолдеров не найдено")
                return text

            # 2. Получаем данные пользователя
            user_obj = await UserService.get_user_by_tg_id(session, user_id)
            if not user_obj:
                logger.warning(f"⚠️ Пользователь {user_id} не найден")
                return text

            # 3. Получаем настройки системы
            paid_check_price = await SettingService.get_paid_check_price(session)

            # 4. Создаем словарь замен ДИНАМИЧЕСКИ
            replacements = {}

            for placeholder in placeholders:
                value = await PlaceholderService._get_placeholder_value(
                    session, placeholder, user_obj, paid_check_price, additional_data
                )
                if value is not None:
                    replacements[placeholder] = value
                    logger.info(f"🔧 Подготовлена замена {placeholder} -> {value}")

            # 5. Заменяем плейсхолдеры
            for placeholder, value in replacements.items():
                text = text.replace(placeholder, str(value))
                logger.info(f"✅ Заменен {placeholder} -> {value}")

            logger.info(f"✅ Заменены {len(replacements)} плейсхолдеров для пользователя {user_id}")
            return text

        except Exception as e:
            logger.error(f"❌ Ошибка замены плейсхолдеров: {e}")
            return text

    @staticmethod
    async def _get_placeholder_value(
        session: AsyncSession,
        placeholder: str,
        user_obj,
        paid_check_price: float,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Получить значение для конкретного плейсхолдера"""
        try:
            # Пользовательские данные
            if placeholder == "{balance}":
                return str(user_obj.balance)
            elif placeholder == "{checks_count}":
                return str(user_obj.checks_count or 0)
            elif placeholder == "{saved_amount}":
                return str(user_obj.saved_amount or 0)
            elif placeholder == "{language}":
                return user_obj.language or "ru"

            # Настройки системы
            elif placeholder == "{paid_check_price}":
                return str(paid_check_price)

            # Данные проверки
            elif placeholder == "{address}" and additional_data and "address" in additional_data:
                return str(additional_data["address"])
            elif placeholder == "{chain}" and additional_data and "chain" in additional_data:
                return str(additional_data["chain"])
            elif placeholder == "{risk_level}" and additional_data and "risk_level" in additional_data:
                return str(additional_data["risk_level"])
            elif placeholder == "{risk_score}" and additional_data and "risk_score" in additional_data:
                return str(additional_data["risk_score"])
            elif placeholder == "{risk_details}" and additional_data and "risk_details" in additional_data:
                return str(additional_data["risk_details"])

            # Address Label API данные
            elif placeholder == "{label}" and additional_data and "label" in additional_data:
                return str(additional_data["label"])
            elif placeholder == "{address_type}" and additional_data and "address_type" in additional_data:
                return str(additional_data["address_type"])
            elif placeholder == "{website}" and additional_data and "website" in additional_data:
                return str(additional_data["website"])
            elif placeholder == "{address_status}" and additional_data and "address_status" in additional_data:
                return str(additional_data["address_status"])

            # Дополнительные данные
            elif additional_data and placeholder in additional_data:
                return str(additional_data[placeholder])

            # Неизвестные плейсхолдеры - логируем но не падаем
            else:
                logger.warning(f"⚠️ Неизвестный плейсхолдер: {placeholder}")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка получения значения для {placeholder}: {e}")
            return None

    @staticmethod
    def get_available_placeholders() -> Dict[str, str]:
        """Получить список всех доступных плейсхолдеров"""
        return PlaceholderService.AVAILABLE_PLACEHOLDERS.copy()

    @staticmethod
    def extract_placeholders_from_text(text: str) -> list:
        """Извлечь все плейсхолдеры из текста"""
        import re

        placeholders = re.findall(r"\{[^}]+\}", text)
        return list(set(placeholders))  # Убираем дубликаты
