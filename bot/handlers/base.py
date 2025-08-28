"""
Базовые классы для обработчиков бота
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from common.error_handling import ErrorHandler

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Базовый класс для всех обработчиков"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработать обновление"""
        pass

    def log_error(self, error: Exception, context: str = "", user_id: Optional[int] = None):
        """Логировать ошибку с контекстом"""
        ErrorHandler.log_error(error, f"{self.__class__.__name__}: {context}", user_id)


class TriggerDetector:
    """Детектор триггеров сообщений"""

    @staticmethod
    async def detect_trigger(update: Update) -> Dict[str, Any]:
        """Определение триггера сообщения"""
        message = update.message
        trigger = {"type": "unknown", "value": message.text, "user_id": message.from_user.id}

        # Команда /start
        if message.text == "/start":
            trigger["type"] = "command"
            trigger["value"] = "/start"

        # Кнопки главного меню
        elif message.text in ["🔍 Проверка", "💰 Пополнить", "👤 Личный кабинет", "📁 FAQ"]:
            trigger["type"] = "button"
            trigger["value"] = message.text

        # Адрес (длинная строка с буквами/цифрами)
        elif len(message.text) > 20 and any(c.isalpha() for c in message.text) and any(c.isdigit() for c in message.text):
            from common.chain_detector import is_valid_crypto_address

            if is_valid_crypto_address(message.text):
                trigger["type"] = "address_input"
                trigger["value"] = message.text

        # Другие кнопки
        else:
            trigger["type"] = "text_equals"
            trigger["value"] = message.text

        return trigger


class KeyboardBuilder:
    """Построитель клавиатур"""

    @staticmethod
    def create_keyboard_from_buttons(buttons: List[str]) -> Optional[ReplyKeyboardMarkup]:
        """Создать клавиатуру из списка кнопок - 2 кнопки в ряд"""
        if not buttons:
            return None

        keyboard = []
        row = []

        for i, button_text in enumerate(buttons):
            row.append(KeyboardButton(text=button_text))

            # Каждые 2 кнопки создаем новый ряд
            if len(row) == 2 or i == len(buttons) - 1:
                keyboard.append(row)
                row = []

        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

    @staticmethod
    def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
        """Создать клавиатуру главного меню"""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("🔍 Проверка"), KeyboardButton("💰 Пополнить")],
                [KeyboardButton("👤 Личный кабинет"), KeyboardButton("📁 FAQ")],
            ],
            resize_keyboard=True,
        )

    @staticmethod
    def create_check_options_keyboard() -> ReplyKeyboardMarkup:
        """Создать клавиатуру опций проверки"""
        return ReplyKeyboardMarkup(
            [[KeyboardButton("✅ Бесплатная"), KeyboardButton("🛡️ Платная")], [KeyboardButton("💰 Пополнить")]],
            resize_keyboard=True,
        )

    @staticmethod
    def create_payment_keyboard() -> ReplyKeyboardMarkup:
        """Создать клавиатуру для платежей"""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("🛡️ Заказать глубокий анализ"), KeyboardButton("💰 Пополнить")],
                [KeyboardButton("🏠 Главное меню")],
            ],
            resize_keyboard=True,
        )

    @staticmethod
    def create_dynamic_keyboard(button_text: str) -> ReplyKeyboardMarkup:
        """Создать динамическую клавиатуру из текста кнопок"""
        try:
            # Разбираем текст кнопок (формат: "Кнопка1|Кнопка2|Кнопка3")
            buttons = [btn.strip() for btn in button_text.split("|") if btn.strip()]
            
            # Группируем кнопки по 2 в ряд
            keyboard_rows = []
            for i in range(0, len(buttons), 2):
                row = [KeyboardButton(buttons[i])]
                if i + 1 < len(buttons):
                    row.append(KeyboardButton(buttons[i + 1]))
                keyboard_rows.append(row)
            
            # Добавляем кнопку "Главное меню" в последний ряд
            if keyboard_rows:
                keyboard_rows[-1].append(KeyboardButton("🏠 Главное меню"))
            else:
                keyboard_rows.append([KeyboardButton("🏠 Главное меню")])
            
            return ReplyKeyboardMarkup(keyboard_rows, resize_keyboard=True)
            
        except Exception as e:
            logger.error(f"Ошибка создания динамической клавиатуры: {e}")
            # Fallback на стандартную клавиатуру
            return ReplyKeyboardMarkup(
                [
                    [KeyboardButton("🛡️ Заказать глубокий анализ"), KeyboardButton("💰 Пополнить")],
                    [KeyboardButton("🏠 Главное меню")],
                ],
                resize_keyboard=True,
            )


class MessageFormatter:
    """Форматирование сообщений"""

    @staticmethod
    def convert_markdown_to_html_simple(text: str) -> str:
        """Простая конвертация Markdown в HTML для Telegram"""
        import re

        # Заменяем **текст** на <b>текст</b>
        def replace_bold(match):
            content = match.group(1)
            return f"<b>{content}</b>"

        # Ищем **текст** и заменяем на <b>текст</b>
        html_text = re.sub(r"\*\*(.*?)\*\*", replace_bold, text)

        return html_text

    @staticmethod
    def format_fallback_message() -> str:
        """Форматировать fallback сообщение"""
        return (
            "🚀 Добро пожаловать в Check Your Crypto Bot!\n\n"
            "🔍 Проверяйте криптовалютные адреса\n"
            "💰 Пополняйте баланс\n"
            "👤 Управляйте аккаунтом\n\n"
            "Выберите действие:"
        )

    @staticmethod
    def format_error_message() -> str:
        """Форматировать сообщение об ошибке"""
        return "❌ Произошла ошибка. Попробуйте позже."


class UserContext:
    """Контекст пользователя"""

    def __init__(self, user_id: int, username: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.language = "ru"  # По умолчанию
        self.balance = 0.0
        self.is_blocked = False
        self.current_address: Optional[str] = None

    @classmethod
    async def from_update(cls, update: Update) -> "UserContext":
        """Создать контекст пользователя из обновления"""
        user = update.effective_user
        return cls(user_id=user.id, username=user.username)

    def set_address(self, address: str):
        """Установить текущий адрес"""
        self.current_address = address

    def get_address(self) -> Optional[str]:
        """Получить текущий адрес"""
        return self.current_address


class HandlerResult:
    """Результат обработки"""

    def __init__(self, success: bool, message: str = "", data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}

    @classmethod
    def success(cls, message: str = "", data: Optional[Dict[str, Any]] = None) -> "HandlerResult":
        """Создать успешный результат"""
        return cls(True, message, data)

    @classmethod
    def error(cls, message: str = "", data: Optional[Dict[str, Any]] = None) -> "HandlerResult":
        """Создать результат с ошибкой"""
        return cls(False, message, data)

    def is_success(self) -> bool:
        """Проверить успешность"""
        return self.success

    def get_message(self) -> str:
        """Получить сообщение"""
        return self.message

    def get_data(self) -> Dict[str, Any]:
        """Получить данные"""
        return self.data
