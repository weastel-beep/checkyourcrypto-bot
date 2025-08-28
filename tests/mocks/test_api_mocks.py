"""
Mock тесты для API без внешних зависимостей
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


class TestUserServiceMocks:
    """Mock тесты для сервиса пользователей"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_create_user_mock(self):
        """Mock тест создания пользователя"""
        tg_id = 999999999
        language = "ru"
        username = "mock_test_user"
        
        # Полностью мокаем API ответ
        mock_api_response = {
            "id": 1,
            "tg_id": tg_id,
            "username": username,
            "language": language,
            "balance": "0.00",
            "referral_code": "MOCK123",
            "is_blocked": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('common.services.UserService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await UserService.get_or_create_user(mock_session, tg_id, language, username)
                
                assert result is not None
                assert result.tg_id == tg_id
                assert result.username == username
                assert result.language == language
                assert result.balance == Decimal("0.00")
                assert result.is_blocked is False
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_user_mock(self):
        """Mock тест получения пользователя"""
        tg_id = 123456789
        
        mock_api_response = {
            "id": 1,
            "tg_id": tg_id,
            "username": "test_user",
            "language": "ru",
            "balance": "5.00",
            "referral_code": "MOCK123",
            "is_blocked": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('common.services.UserService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await UserService.get_user_by_tg_id(mock_session, tg_id)
                
                assert result is not None
                assert result.tg_id == tg_id
                assert result.balance == Decimal("5.00")
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_user_not_found_mock(self):
        """Mock тест пользователя не найден"""
        tg_id = 999999999
        
        with patch('common.services.UserService._make_api_request') as mock_api_request:
            mock_api_request.side_effect = Exception("User not found")
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await UserService.get_user_by_tg_id(mock_session, tg_id)
                
                assert result is None


class TestCheckServiceMocks:
    """Mock тесты для сервиса проверок"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_create_check_mock(self):
        """Mock тест создания проверки"""
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
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_user_checks_mock(self):
        """Mock тест получения проверок пользователя"""
        user_id = 123456789
        limit = 10
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Мокаем список проверок
            mock_checks = [
                MagicMock(id=1, address="addr1", chain="btc", created_at=datetime.now()),
                MagicMock(id=2, address="addr2", chain="eth", created_at=datetime.now())
            ]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_checks
            mock_session.execute.return_value = mock_result
            
            result = await CheckService.get_user_checks(mock_session, user_id, limit)
            
            assert len(result) == 2
            assert result[0].address == "addr1"
            assert result[1].address == "addr2"


class TestTextServiceMocks:
    """Mock тесты для сервиса текстов"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_text_mock(self):
        """Mock тест получения текста"""
        key = "welcome"
        language = "ru"
        user_id = 123456789
        
        mock_api_response = {
            "texts": [
                {
                    "category": key,
                    "language": language,
                    "is_active": True,
                    "content": "🚀 Добро пожаловать в Check Your Crypto Bot!"
                }
            ]
        }
        
        with patch('common.services.TextService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await TextService.get_text(mock_session, key, language, user_id)
                
                assert result == "🚀 Добро пожаловать в Check Your Crypto Bot!"
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_text_not_found_mock(self):
        """Mock тест текста не найден"""
        key = "unknown_key"
        language = "ru"
        user_id = 123456789
        
        mock_api_response = {"texts": []}
        
        with patch('common.services.TextService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await TextService.get_text(mock_session, key, language, user_id)
                
                assert result == key
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_set_text_mock(self):
        """Mock тест установки текста"""
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


class TestSettingServiceMocks:
    """Mock тесты для сервиса настроек"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_setting_mock(self):
        """Mock тест получения настройки"""
        key = "paid_check_price"
        
        mock_api_response = {"value": "1.50"}
        
        with patch('common.services.SettingService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await SettingService.get_setting(mock_session, key)
                
                assert result == "1.50"
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_setting_not_found_mock(self):
        """Mock тест настройки не найдена"""
        key = "unknown_setting"
        
        with patch('common.services.SettingService._make_api_request') as mock_api_request:
            mock_api_request.side_effect = Exception("Setting not found")
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await SettingService.get_setting(mock_session, key)
                
                assert result is None
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_set_setting_mock(self):
        """Mock тест установки настройки"""
        key = "paid_check_price"
        value = "2.00"
        
        with patch('common.services.SettingService._make_api_request') as mock_api_request:
            mock_api_request.return_value = {"success": True}
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                await SettingService.set_setting(mock_session, key, value)
                
                mock_api_request.assert_called_once()


class TestMetaSleuthAPIMocks:
    """Mock тесты для сервиса MetaSleuth"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_check_address_mock(self):
        """Mock тест проверки адреса через MetaSleuth"""
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        
        mock_api_response = {
            "success": True,
            "data": {
                "address": address,
                "risk_score": 0.1,
                "is_suspicious": False,
                "tags": ["legitimate"],
                "transactions_count": 1000,
                "total_volume": "1000000.00"
            }
        }
        
        with patch('common.metasleuth.MetaSleuthAPI._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            metasleuth = MetaSleuthAPI()
            result = await metasleuth.wallet_screening(address, chain)
            
            assert result["success"] is True
            assert result["data"]["address"] == address
            assert result["data"]["risk_score"] == 0.1
            assert result["data"]["is_suspicious"] is False
            assert "legitimate" in result["data"]["tags"]
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_check_suspicious_address_mock(self):
        """Mock тест проверки подозрительного адреса"""
        address = "suspicious_address"
        chain = "btc"
        
        mock_api_response = {
            "success": True,
            "data": {
                "address": address,
                "risk_score": 0.9,
                "is_suspicious": True,
                "tags": ["suspicious", "scam"],
                "transactions_count": 5,
                "total_volume": "100.00"
            }
        }
        
        with patch('common.metasleuth.MetaSleuthAPI._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            metasleuth = MetaSleuthAPI()
            result = await metasleuth.wallet_screening(address, chain)
            
            assert result["success"] is True
            assert result["data"]["risk_score"] == 0.9
            assert result["data"]["is_suspicious"] is True
            assert "suspicious" in result["data"]["tags"]
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_check_address_api_error_mock(self):
        """Mock тест ошибки API при проверке адреса"""
        address = "error_address"
        chain = "btc"
        
        with patch('common.metasleuth.MetaSleuthAPI._make_api_request') as mock_api_request:
            mock_api_request.side_effect = Exception("API Error")
            
            metasleuth = MetaSleuthAPI()
            result = await metasleuth.wallet_screening(address, chain)
            
            assert result["success"] is False
            assert "error" in result


class TestGPTServiceMocks:
    """Mock тесты для сервиса GPT"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_generate_response_mock(self):
        """Mock тест генерации ответа через GPT"""
        prompt = "Explain what is cryptocurrency"
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Cryptocurrency is a digital or virtual currency that uses cryptography for security. It operates on a decentralized network called blockchain."
                    }
                }
            ]
        }
        
        with patch('common.gpt_service.GPTService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_response
            
            result = await GPTService.generate_response(prompt)
            
            assert "Cryptocurrency" in result
            assert "digital" in result
            assert "blockchain" in result
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_generate_response_error_mock(self):
        """Mock тест ошибки при генерации ответа"""
        prompt = "error_prompt"
        
        with patch('common.gpt_service.GPTService._make_api_request') as mock_api_request:
            mock_api_request.side_effect = Exception("OpenAI API Error")
            
            result = await GPTService.generate_response(prompt)
            
            assert "error" in result.lower()


class TestBinancePayServiceMocks:
    """Mock тесты для сервиса Binance Pay"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_create_order_mock(self):
        """Mock тест создания платежного заказа"""
        amount = 10.0
        currency = "USDT"
        description = "Test payment"
        
        mock_api_response = {
            "status": "SUCCESS",
            "data": {
                "prepayId": "test_prepay_id_123",
                "qrcodeLink": "https://test.qr.code/link",
                "checkoutUrl": "https://test.checkout.url/link",
                "amount": "10.00",
                "currency": "USDT"
            }
        }
        
        with patch('common.binance_pay_service.BinancePayService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            result = await BinancePayService.create_order(amount, currency, description)
            
            assert result["status"] == "SUCCESS"
            assert result["data"]["prepayId"] == "test_prepay_id_123"
            assert result["data"]["qrcodeLink"] == "https://test.qr.code/link"
            assert result["data"]["checkoutUrl"] == "https://test.checkout.url/link"
            assert result["data"]["amount"] == "10.00"
            assert result["data"]["currency"] == "USDT"
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_create_order_error_mock(self):
        """Mock тест ошибки при создании заказа"""
        amount = 10.0
        currency = "USDT"
        description = "Error payment"
        
        with patch('common.binance_pay_service.BinancePayService._make_api_request') as mock_api_request:
            mock_api_request.side_effect = Exception("Binance Pay API Error")
            
            result = await BinancePayService.create_order(amount, currency, description)
            
            assert result["status"] == "ERROR"
            assert "error" in result


class TestScenarioServiceMocks:
    """Mock тесты для сервиса сценариев"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_active_scenario_mock(self):
        """Mock тест получения активного сценария"""
        mock_api_response = {
            "scenarios": [
                {
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
                        },
                        {
                            "id": "check_stage",
                            "type": "address_input",
                            "text": "enter_address",
                            "buttons": ["back_button"]
                        }
                    ]
                }
            ]
        }
        
        with patch('common.services_package.scenario_service.ScenarioService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await ScenarioService.get_active_scenario(mock_session)
                
                assert result is not None
                assert result["id"] == "main_scenario"
                assert result["current_stage"]["id"] == "start_stage"
                assert len(result["stages"]) == 2
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_get_all_scenarios_mock(self):
        """Mock тест получения всех сценариев"""
        mock_api_response = [
            {
                "id": "scenario_1",
                "current_stage": {"id": "stage_1"},
                "stages": [{"id": "stage_1"}]
            },
            {
                "id": "scenario_2",
                "current_stage": {"id": "stage_2"},
                "stages": [{"id": "stage_2"}]
            }
        ]
        
        with patch('common.services_package.scenario_service.ScenarioService._make_api_request') as mock_api_request:
            mock_api_request.return_value = mock_api_response
            
            with patch('common.database.async_session_maker') as mock_session_maker:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await ScenarioService.get_all_scenarios(mock_session)
                
                assert len(result) == 2
                assert result[0]["id"] == "scenario_1"
                assert result[1]["id"] == "scenario_2"


class TestFullBotFlowMocks:
    """Mock тесты для полного flow бота"""
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_complete_check_flow_mock(self):
        """Mock тест полного flow проверки адреса"""
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
        
        mock_context = MagicMock()
        
        # Мокаем все сервисы
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
                                            "is_suspicious": False,
                                            "tags": ["legitimate"]
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
                                    mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.mock
    @pytest.mark.asyncio
    async def test_scenario_flow_mock(self):
        """Mock тест flow сценария бота"""
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
