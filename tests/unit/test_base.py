"""
Unit тесты для базовых классов обработчиков
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

from bot.handlers.base import (
    TriggerDetector, KeyboardBuilder, 
    MessageFormatter, UserContext, HandlerResult
)


class TestTriggerDetector:
    """Тесты для детектора триггеров"""
    
    @pytest.mark.asyncio
    async def test_detect_trigger_command(self, mock_update):
        """Тест определения команды"""
        mock_update.message.text = "/start"
        
        trigger = await TriggerDetector.detect_trigger(mock_update)
        
        assert trigger["type"] == "command"
        assert trigger["value"] == "/start"
        assert trigger["user_id"] == 123456789
    
    @pytest.mark.asyncio
    async def test_detect_trigger_button(self, mock_update):
        """Тест определения кнопки"""
        mock_update.message.text = "🔍 Проверка"
        
        trigger = await TriggerDetector.detect_trigger(mock_update)
        
        assert trigger["type"] == "button"
        assert trigger["value"] == "🔍 Проверка"
        assert trigger["user_id"] == 123456789
    
    @pytest.mark.asyncio
    async def test_detect_trigger_address_input(self, mock_update):
        """Тест определения ввода адреса"""
        mock_update.message.text = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=True):
            trigger = await TriggerDetector.detect_trigger(mock_update)
            
            assert trigger["type"] == "address_input"
            assert trigger["value"] == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
            assert trigger["user_id"] == 123456789
    
    @pytest.mark.asyncio
    async def test_detect_trigger_text_equals(self, mock_update):
        """Тест определения обычного текста"""
        mock_update.message.text = "какой-то текст"
        
        trigger = await TriggerDetector.detect_trigger(mock_update)
        
        assert trigger["type"] == "text_equals"
        assert trigger["value"] == "какой-то текст"
        assert trigger["user_id"] == 123456789
    
    @pytest.mark.asyncio
    async def test_detect_trigger_invalid_address(self, mock_update):
        """Тест определения невалидного адреса"""
        mock_update.message.text = "invalid_address"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=False):
            trigger = await TriggerDetector.detect_trigger(mock_update)
            
            assert trigger["type"] == "text_equals"
            assert trigger["value"] == "invalid_address"


class TestKeyboardBuilder:
    """Тесты для построителя клавиатур"""
    
    def test_create_keyboard_from_buttons_empty(self):
        """Тест создания клавиатуры из пустого списка кнопок"""
        keyboard = KeyboardBuilder.create_keyboard_from_buttons([])
        assert keyboard is None
    
    def test_create_keyboard_from_buttons_single(self):
        """Тест создания клавиатуры с одной кнопкой"""
        buttons = ["Кнопка 1"]
        keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 1
        assert len(keyboard.keyboard[0]) == 1
        assert keyboard.keyboard[0][0].text == "Кнопка 1"
    
    def test_create_keyboard_from_buttons_two(self):
        """Тест создания клавиатуры с двумя кнопками"""
        buttons = ["Кнопка 1", "Кнопка 2"]
        keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 1
        assert len(keyboard.keyboard[0]) == 2
        assert keyboard.keyboard[0][0].text == "Кнопка 1"
        assert keyboard.keyboard[0][1].text == "Кнопка 2"
    
    def test_create_keyboard_from_buttons_three(self):
        """Тест создания клавиатуры с тремя кнопками (2 в первом ряду, 1 во втором)"""
        buttons = ["Кнопка 1", "Кнопка 2", "Кнопка 3"]
        keyboard = KeyboardBuilder.create_keyboard_from_buttons(buttons)
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2  # Первый ряд
        assert len(keyboard.keyboard[1]) == 1  # Второй ряд
        assert keyboard.keyboard[0][0].text == "Кнопка 1"
        assert keyboard.keyboard[0][1].text == "Кнопка 2"
        assert keyboard.keyboard[1][0].text == "Кнопка 3"
    
    def test_create_main_menu_keyboard(self):
        """Тест создания клавиатуры главного меню"""
        keyboard = KeyboardBuilder.create_main_menu_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2
        assert len(keyboard.keyboard[1]) == 2
        
        # Проверяем кнопки
        assert keyboard.keyboard[0][0].text == "🔍 Проверка"
        assert keyboard.keyboard[0][1].text == "💰 Пополнить"
        assert keyboard.keyboard[1][0].text == "👤 Личный кабинет"
        assert keyboard.keyboard[1][1].text == "📁 FAQ"
    
    def test_create_check_options_keyboard(self):
        """Тест создания клавиатуры опций проверки"""
        keyboard = KeyboardBuilder.create_check_options_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2
        assert len(keyboard.keyboard[1]) == 1
        
        # Проверяем кнопки
        assert keyboard.keyboard[0][0].text == "✅ Бесплатная"
        assert keyboard.keyboard[0][1].text == "🛡️ Платная"
        assert keyboard.keyboard[1][0].text == "💰 Пополнить"
    
    def test_create_payment_keyboard(self):
        """Тест создания клавиатуры для платежей"""
        keyboard = KeyboardBuilder.create_payment_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2
        assert len(keyboard.keyboard[1]) == 1
        
        # Проверяем кнопки
        assert keyboard.keyboard[0][0].text == "🛡️ Заказать глубокий анализ"
        assert keyboard.keyboard[0][1].text == "💰 Пополнить"
        assert keyboard.keyboard[1][0].text == "🏠 Главное меню"


class TestMessageFormatter:
    """Тесты для форматировщика сообщений"""
    
    def test_convert_markdown_to_html_simple_bold(self):
        """Тест конвертации Markdown в HTML для жирного текста"""
        markdown_text = "Это **жирный** текст"
        html_text = MessageFormatter.convert_markdown_to_html_simple(markdown_text)
        
        assert html_text == "Это <b>жирный</b> текст"
    
    def test_convert_markdown_to_html_simple_multiple_bold(self):
        """Тест конвертации Markdown в HTML для нескольких жирных фрагментов"""
        markdown_text = "**Первый** обычный **второй** текст"
        html_text = MessageFormatter.convert_markdown_to_html_simple(markdown_text)
        
        assert html_text == "<b>Первый</b> обычный <b>второй</b> текст"
    
    def test_convert_markdown_to_html_simple_no_bold(self):
        """Тест конвертации Markdown в HTML без жирного текста"""
        markdown_text = "Обычный текст без форматирования"
        html_text = MessageFormatter.convert_markdown_to_html_simple(markdown_text)
        
        assert html_text == markdown_text
    
    def test_convert_markdown_to_html_simple_empty(self):
        """Тест конвертации пустого текста"""
        markdown_text = ""
        html_text = MessageFormatter.convert_markdown_to_html_simple(markdown_text)
        
        assert html_text == ""
    
    def test_format_fallback_message(self):
        """Тест форматирования fallback сообщения"""
        message = MessageFormatter.format_fallback_message()
        
        assert "🚀 Добро пожаловать в Check Your Crypto Bot!" in message
        assert "🔍 Проверяйте криптовалютные адреса" in message
        assert "💰 Пополняйте баланс" in message
        assert "👤 Управляйте аккаунтом" in message
        assert "Выберите действие:" in message
    
    def test_format_error_message(self):
        """Тест форматирования сообщения об ошибке"""
        message = MessageFormatter.format_error_message()
        
        assert message == "❌ Произошла ошибка. Попробуйте позже."


class TestUserContext:
    """Тесты для контекста пользователя"""
    
    def test_user_context_initialization(self):
        """Тест инициализации контекста пользователя"""
        context = UserContext(user_id=123, username="test_user")
        
        assert context.user_id == 123
        assert context.username == "test_user"
        assert context.language == "ru"
        assert context.balance == 0.0
        assert context.is_blocked is False
        assert context.current_address is None
    
    @pytest.mark.asyncio
    async def test_from_update(self, mock_update):
        """Тест создания контекста из обновления"""
        context = await UserContext.from_update(mock_update)
        
        assert context.user_id == 123456789
        assert context.username == "test_user"
    
    def test_set_address(self):
        """Тест установки адреса"""
        context = UserContext(user_id=123)
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        context.set_address(address)
        
        assert context.current_address == address
    
    def test_get_address(self):
        """Тест получения адреса"""
        context = UserContext(user_id=123)
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        context.set_address(address)
        result = context.get_address()
        
        assert result == address
    
    def test_get_address_none(self):
        """Тест получения адреса когда он не установлен"""
        context = UserContext(user_id=123)
        result = context.get_address()
        
        assert result is None


class TestHandlerResult:
    """Тесты для результата обработки"""
    
    def test_handler_result_initialization(self):
        """Тест инициализации результата обработки"""
        result = HandlerResult(success=True, message="test", data={"key": "value"})
        
        assert result.success is True
        assert result.message == "test"
        assert result.data == {"key": "value"}
    
    def test_handler_result_default_data(self):
        """Тест инициализации с пустыми данными по умолчанию"""
        result = HandlerResult(success=False, message="error")
        
        assert result.success is False
        assert result.message == "error"
        assert result.data == {}
    
    def test_success_classmethod(self):
        """Тест создания успешного результата"""
        result = HandlerResult.success("success message", {"data": "value"})
        
        assert result.success is True
        assert result.message == "success message"
        assert result.data == {"data": "value"}
    
    def test_error_classmethod(self):
        """Тест создания результата с ошибкой"""
        result = HandlerResult.error("error message", {"error": "details"})
        
        assert result.success is False
        assert result.message == "error message"
        assert result.data == {"error": "details"}
    
    def test_is_success(self):
        """Тест проверки успешности"""
        success_result = HandlerResult.success("test")
        error_result = HandlerResult.error("test")
        
        assert success_result.is_success() is True
        assert error_result.is_success() is False
    
    def test_get_message(self):
        """Тест получения сообщения"""
        result = HandlerResult(success=True, message="test message")
        
        assert result.get_message() == "test message"
    
    def test_get_data(self):
        """Тест получения данных"""
        data = {"key": "value", "number": 42}
        result = HandlerResult(success=True, message="test", data=data)
        
        assert result.get_data() == data
