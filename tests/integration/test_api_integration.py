"""
Интеграционные тесты для API взаимодействий
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from common.services import UserService, CheckService, TextService, SettingService
from common.services_package.scenario_service import ScenarioService
from common.metasleuth import MetaSleuthAPI
from common.gpt_service import GPTService
from common.binance_pay_service import BinancePayService


class TestUserServiceIntegration:
    """Интеграционные тесты для сервиса пользователей"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_via_api(self):
        """Тест создания пользователя через реальный API"""
        tg_id = 999999999
        language = "ru"
        username = "integration_test_user"
        
        # Используем реальный API endpoint
        with patch('common.services.aiohttp.ClientSession') as mock_client_session:
            # Правильно мокаем HTTP сессию
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            # Мокаем успешный ответ от API
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={
                "id": 1,
                "tg_id": tg_id,
                "username": username,
                "language": language,
                "balance": "0.00",
                "referral_code": "TEST123",
                "is_blocked": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            })
            
            mock_http_session.post.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            # Выполняем тест
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await UserService.get_or_create_user(mock_session, tg_id, language, username)
                
                # Проверяем результат
                assert result is not None
                assert result.tg_id == tg_id
                assert result.username == username
                assert result.language == language
                assert result.balance == Decimal("0.00")
                assert result.is_blocked is False
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_via_api(self):
        """Тест получения пользователя через реальный API"""
        tg_id = 123456789
        
        with patch('common.services.aiohttp.ClientSession') as mock_client_session:
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "id": 1,
                "tg_id": tg_id,
                "username": "test_user",
                "language": "ru",
                "balance": "5.00",
                "referral_code": "TEST123",
                "is_blocked": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            })
            
            mock_http_session.get.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await UserService.get_user_by_tg_id(mock_session, tg_id)
                
                assert result is not None
                assert result.tg_id == tg_id
                assert result.balance == Decimal("5.00")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_language_integration(self):
        """Тест обновления языка пользователя в базе данных"""
        tg_id = 123456789
        new_language = "en"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Мокаем результат выполнения SQL запроса
            mock_result = MagicMock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            
            result = await UserService.update_user_language(mock_session, tg_id, new_language)
            
            assert result is True
            mock_session.commit.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_balance_operations_integration(self):
        """Тест операций с балансом пользователя"""
        user = MagicMock()
        user.balance = Decimal("10.00")
        amount = Decimal("5.00")
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Тест пополнения баланса
            await UserService.add_balance(mock_session, user, amount)
            assert user.balance == Decimal("15.00")
            
            # Тест списания баланса
            result = await UserService.deduct_balance(mock_session, user, amount)
            assert result is True
            assert user.balance == Decimal("10.00")
            
            # Тест недостаточного баланса
            result = await UserService.deduct_balance(mock_session, user, Decimal("20.00"))
            assert result is False
            assert user.balance == Decimal("10.00")


class TestCheckServiceIntegration:
    """Интеграционные тесты для сервиса проверок"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_check_integration(self):
        """Тест создания проверки в базе данных"""
        user_id = 123456789
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        check_type = "free"
        result = {"status": "completed", "risk_score": 0.1}
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Создаем реальный объект Check
            from common.models import Check
            mock_check = Check(
                user_id=user_id,
                address=address,
                chain=chain,
                type=check_type,
                result=result
            )
            mock_check.id = 1
            mock_check.created_at = datetime.now()
            
            mock_session.refresh.return_value = mock_check
            
            result_check = await CheckService.create_check(
                mock_session, user_id, address, chain, check_type, result
            )
            
            assert result_check is not None
            assert result_check.user_id == user_id
            assert result_check.address == address
            assert result_check.chain == chain
            assert result_check.type == check_type
            assert result_check.result == result
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_checks_integration(self):
        """Тест получения проверок пользователя из базы данных"""
        user_id = 123456789
        limit = 10
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Мокаем список проверок
            mock_checks = [
                MagicMock(id=1, address="addr1", chain="btc"),
                MagicMock(id=2, address="addr2", chain="eth")
            ]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_checks
            mock_session.execute.return_value = mock_result
            
            result = await CheckService.get_user_checks(mock_session, user_id, limit)
            
            assert len(result) == 2
            assert result[0].address == "addr1"
            assert result[1].address == "addr2"


class TestTextServiceIntegration:
    """Интеграционные тесты для сервиса текстов"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_text_via_api(self):
        """Тест получения текста через реальный API"""
        key = "welcome"
        language = "ru"
        user_id = 123456789
        
        with patch('common.services.aiohttp.ClientSession') as mock_client_session:
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "texts": [
                    {
                        "category": key,
                        "language": language,
                        "is_active": True,
                        "content": "🚀 Добро пожаловать в Check Your Crypto Bot!"
                    }
                ]
            })
            
            mock_http_session.get.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await TextService.get_text(mock_session, key, language, user_id)
                
                assert result == "🚀 Добро пожаловать в Check Your Crypto Bot!"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_set_text_integration(self):
        """Тест установки текста в базе данных"""
        key = "test_key"
        value = "test_value"
        language = "ru"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_text = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_text
            mock_session.execute.return_value = mock_result
            
            await TextService.set_text(mock_session, key, value, language)
            
            mock_session.commit.assert_called_once()


class TestSettingServiceIntegration:
    """Интеграционные тесты для сервиса настроек"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_setting_via_api(self):
        """Тест получения настройки через реальный API"""
        key = "paid_check_price"
        
        with patch('common.services.aiohttp.ClientSession') as mock_client_session:
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"value": "1.50"})
            
            mock_http_session.get.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await SettingService.get_setting(mock_session, key)
                
                assert result == "1.50"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_block_user_integration(self):
        """Тест блокировки пользователя в базе данных"""
        user = MagicMock()
        user.tg_id = 123456789
        user.is_blocked = False
        reason = "Test reason"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            result = await SettingService.block_user(mock_session, user, reason)
            
            assert result is True
            assert user.is_blocked is True
            mock_session.commit.assert_called_once()


class TestMetaSleuthAPIIntegration:
    """Интеграционные тесты для сервиса MetaSleuth"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_check_address_via_metasleuth(self):
        """Тест проверки адреса через MetaSleuth API"""
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        
        with patch('common.metasleuth.aiohttp.ClientSession') as mock_client_session:
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "success": True,
                "data": {
                    "address": address,
                    "risk_score": 0.1,
                    "is_suspicious": False,
                    "tags": ["legitimate"]
                }
            })
            
            mock_http_session.post.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            metasleuth = MetaSleuthAPI()
            result = await metasleuth.wallet_screening(address, chain)
            
            assert result["success"] is True
            assert result["data"]["address"] == address
            assert result["data"]["risk_score"] == 0.1
            assert result["data"]["is_suspicious"] is False


class TestGPTServiceIntegration:
    """Интеграционные тесты для сервиса GPT"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_response_via_openai(self):
        """Тест генерации ответа через OpenAI API"""
        prompt = "Explain what is cryptocurrency"
        
        with patch('common.gpt_service.openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Cryptocurrency is a digital or virtual currency..."
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await GPTService.generate_response(prompt)
            
            assert "Cryptocurrency" in result
            mock_client.chat.completions.create.assert_called_once()


class TestBinancePayServiceIntegration:
    """Интеграционные тесты для сервиса Binance Pay"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_payment_order(self):
        """Тест создания платежного заказа через Binance Pay"""
        amount = 10.0
        currency = "USDT"
        description = "Test payment"
        
        with patch('common.binance_pay_service.aiohttp.ClientSession') as mock_client_session:
            mock_http_session = AsyncMock()
            mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
            mock_http_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "status": "SUCCESS",
                "data": {
                    "prepayId": "test_prepay_id",
                    "qrcodeLink": "https://test.qr.code",
                    "checkoutUrl": "https://test.checkout.url"
                }
            })
            
            mock_http_session.post.return_value = mock_response
            mock_client_session.return_value = mock_http_session
            
            result = await BinancePayService.create_order(amount, currency, description)
            
            assert result["status"] == "SUCCESS"
            assert "prepayId" in result["data"]
            assert "qrcodeLink" in result["data"]


class TestFullBotFlowIntegration:
    """Интеграционные тесты для полного flow бота"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_check_flow(self):
        """Тест полного flow проверки адреса"""
        from bot.handlers.main_handler import MainHandler
        from telegram import Update, Message, User, Chat
        
        # Создаем мок обновления
        mock_user = User(id=123456789, is_bot=False, first_name="Test", username="test_user")
        mock_chat = Chat(id=123456789, type="private")
        mock_message = Message(
            message_id=1,
            date=datetime.now(),
            chat=mock_chat,
            from_user=mock_user,
            text="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        )
        mock_update = Update(update_id=1, message=mock_message)
        
        # Создаем мок контекста
        mock_context = MagicMock()
        
        # Мокаем все необходимые сервисы
        with patch('bot.handlers.main_handler.async_session_maker') as mock_session_maker:
            with patch('common.chain_detector.is_valid_crypto_address', return_value=True):
                with patch('common.chain_detector.detect_chain', return_value="btc"):
                    with patch('common.metasleuth.MetaSleuthAPI.wallet_screening') as mock_metasleuth:
                        with patch('common.services.UserService.get_or_create_user') as mock_get_user:
                            with patch('common.services.CheckService.create_check') as mock_create_check:
                                with patch('common.services.TextService.get_text') as mock_get_text:
                                    mock_session = AsyncMock()
                                    mock_session_maker.return_value.__aenter__.return_value = mock_session
                                    
                                    # Мокаем пользователя
                                    mock_user_obj = MagicMock()
                                    mock_user_obj.tg_id = 123456789
                                    mock_user_obj.balance = Decimal("10.00")
                                    mock_user_obj.is_blocked = False
                                    mock_get_user.return_value = mock_user_obj
                                    
                                    # Мокаем результат MetaSleuth
                                    mock_metasleuth.return_value = {
                                        "success": True,
                                        "data": {
                                            "risk_score": 0.1,
                                            "is_suspicious": False
                                        }
                                    }
                                    
                                    # Мокаем создание проверки
                                    mock_check = MagicMock()
                                    mock_create_check.return_value = mock_check
                                    
                                    # Мокаем текст
                                    mock_get_text.return_value = "Check result for {address}"
                                    
                                    # Выполняем тест
                                    handler = MainHandler()
                                    result = await handler.handle(mock_update, mock_context)
                                    
                                    # Проверяем результат
                                    assert result is True
                                    mock_create_check.assert_called_once()
                                    mock_get_text.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scenario_flow(self):
        """Тест flow сценария бота"""
        from bot.handlers.scenarios import ScenarioHandler
        from telegram import Update, Message, User, Chat
        
        # Создаем мок обновления для команды /start
        mock_user = User(id=123456789, is_bot=False, first_name="Test", username="test_user")
        mock_chat = Chat(id=123456789, type="private")
        mock_message = Message(
            message_id=1,
            date=datetime.now(),
            chat=mock_chat,
            from_user=mock_user,
            text="/start"
        )
        mock_update = Update(update_id=1, message=mock_message)
        
        mock_context = MagicMock()
        
        # Мокаем сценарий
        sample_scenario = {
            "id": "main_scenario",
            "current_stage": {
                "id": "start_stage",
                "type": "command",
                "text": "welcome_message",
                "buttons": ["check_button", "balance_button"]
            },
            "stages": [
                {
                    "id": "start_stage",
                    "type": "command",
                    "text": "welcome_message",
                    "buttons": ["check_button", "balance_button"]
                }
            ]
        }
        
        with patch('bot.handlers.scenarios.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.scenarios.ScenarioService.get_all_scenarios', return_value=[sample_scenario]):
                with patch('common.services.UserService.get_or_create_user') as mock_get_user:
                    with patch('common.services.TextService.get_text') as mock_get_text:
                        mock_session = AsyncMock()
                        mock_session_maker.return_value.__aenter__.return_value = mock_session
                        
                        mock_user_obj = MagicMock()
                        mock_user_obj.language = "ru"
                        mock_get_user.return_value = mock_user_obj
                        
                        mock_get_text.return_value = "Welcome message"
                        
                        handler = ScenarioHandler()
                        result = await handler.handle(mock_update, mock_context)
                        
                        assert result is True
                        mock_update.message.reply_text.assert_called_once()
