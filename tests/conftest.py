"""
Конфигурация и фикстуры для тестов
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes


@pytest.fixture
def event_loop():
    """Создать event loop для асинхронных тестов"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user():
    """Создать мок пользователя"""
    user = MagicMock(spec=User)
    user.id = 123456789
    user.username = "test_user"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_bot = False
    return user


@pytest.fixture
def mock_chat():
    """Создать мок чата"""
    chat = MagicMock(spec=Chat)
    chat.id = 123456789
    chat.type = "private"
    chat.title = None
    chat.username = None
    return chat


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Создать мок сообщения"""
    message = MagicMock(spec=Message)
    message.message_id = 1
    message.from_user = mock_user
    message.chat = mock_chat
    message.date = None
    message.text = "test message"
    return message


@pytest.fixture
def mock_update(mock_message):
    """Создать мок обновления"""
    update = MagicMock(spec=Update)
    update.update_id = 1
    update.message = mock_message
    update.effective_user = mock_message.from_user
    return update


@pytest.fixture
def mock_context():
    """Создать мок контекста"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.bot_data = {}
    context.application = MagicMock()
    return context


@pytest.fixture
def sample_addresses():
    """Примеры криптовалютных адресов для тестов"""
    return {
        "bitcoin": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "ethereum": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "tron": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "solana": "11111111111111111111111111111112",
        "invalid": "invalid_address_123"
    }


@pytest.fixture
def sample_scenario():
    """Пример сценария для тестов"""
    return {
        "id": 1,
        "name": "Test Scenario",
        "is_active": True,
        "stages": [
            {
                "id": "start_stage",
                "name": "Start Stage",
                "trigger": "command",
                "trigger_value": "/start",
                "text_key": "welcome",
                "buttons": ["check_button", "balance_button"],
                "next_stage": "check_stage"
            },
            {
                "id": "check_stage",
                "name": "Check Stage",
                "trigger": "address_input",
                "text_key": "check_options",
                "buttons": ["free_check", "paid_check"],
                "conditions": [
                    {
                        "type": "balance_sufficient",
                        "action": "show_paid_options",
                        "next_stage": "paid_options"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя для тестов"""
    return {
        "tg_id": 123456789,
        "username": "test_user",
        "language": "ru",
        "balance": 5.0,
        "referral_code": "TEST123",
        "is_blocked": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_session():
    """Создать мок сессии базы данных"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_http_response():
    """Создать мок HTTP ответа"""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"status": "ok"})
    return response


@pytest.fixture
def mock_http_session(mock_http_response):
    """Создать мок HTTP сессии"""
    session = AsyncMock()
    session.get = AsyncMock(return_value=mock_http_response)
    session.post = AsyncMock(return_value=mock_http_response)
    session.put = AsyncMock(return_value=mock_http_response)
    session.delete = AsyncMock(return_value=mock_http_response)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def mock_bot():
    """Создать мок бота"""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.get_me = AsyncMock(return_value=MagicMock(username="test_bot"))
    return bot


@pytest.fixture
def sample_texts():
    """Примеры текстов для тестов"""
    return {
        "welcome": "🚀 Добро пожаловать в Check Your Crypto Bot!",
        "check_options": "🔍 Выберите тип проверки:",
        "invalid_address": "❌ Неверный формат адреса",
        "check_choice": "💰 Баланс: {balance}, Цена: {paid_check_price}",
        "free_check_result": "✅ Бесплатная проверка завершена",
        "paid_check_result": "🛡️ Платная проверка завершена"
    }


@pytest.fixture
def sample_settings():
    """Примеры настроек для тестов"""
    return {
        "paid_check_price": "1.00",
        "free_limit_minutes": "60",
        "referral_bonus": "0.50",
        "max_free_checks_per_day": "10"
    }


@pytest.fixture
def mock_logger():
    """Создать мок логгера"""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def sample_triggers():
    """Примеры триггеров для тестов"""
    return {
        "command": {
            "type": "command",
            "value": "/start",
            "user_id": 123456789
        },
        "address_input": {
            "type": "address_input",
            "value": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "user_id": 123456789
        },
        "button": {
            "type": "button",
            "value": "🔍 Проверка",
            "user_id": 123456789
        },
        "text_equals": {
            "type": "text_equals",
            "value": "💰 Пополнить",
            "user_id": 123456789
        }
    }


@pytest.fixture
def sample_check_result():
    """Пример результата проверки для тестов"""
    return {
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "chain": "btc",
        "check_type": "free",
        "status": "completed",
        "risk_level": 2,
        "risk_description": "🟢 Низкий риск",
        "balance": 5.0,
        "price": 1.0
    }
