"""
Unit тесты для обработчиков
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update

from bot.handlers.scenarios import ScenarioHandler
from bot.handlers.checks import CheckHandler, CheckValidator, CheckResultFormatter
from bot.handlers.main_handler import MainHandler


class TestScenarioHandler:
    """Тесты для обработчика сценариев"""
    
    def test_scenario_handler_initialization(self):
        """Тест инициализации обработчика сценариев"""
        handler = ScenarioHandler()
        assert handler.logger is not None
        assert handler.logger.name == "ScenarioHandler"
    
    @pytest.mark.asyncio
    async def test_handle_success(self, mock_update, mock_context, sample_scenario):
        """Тест успешной обработки сценария"""
        handler = ScenarioHandler()
        
        # Подготавливаем сценарий с правильной структурой
        scenario = sample_scenario.copy()
        scenario["current_stage"] = sample_scenario["stages"][0]
        scenario["current_stage_id"] = "start_stage"
        
        with patch.object(handler, 'find_scenario_by_trigger', return_value=scenario):
            with patch.object(handler, 'execute_stage') as mock_execute:
                result = await handler.handle(mock_update, mock_context)
                
                assert result is True
                mock_execute.assert_called_once_with(mock_update, mock_context, scenario)
    
    @pytest.mark.asyncio
    async def test_handle_no_scenario(self, mock_update, mock_context):
        """Тест обработки без найденного сценария"""
        handler = ScenarioHandler()
        
        with patch.object(handler, 'find_scenario_by_trigger', return_value=None):
            result = await handler.handle(mock_update, mock_context)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_handle_exception(self, mock_update, mock_context):
        """Тест обработки исключения"""
        handler = ScenarioHandler()
        
        with patch.object(handler, 'find_scenario_by_trigger', side_effect=Exception("Test error")):
            result = await handler.handle(mock_update, mock_context)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_find_scenario_by_trigger_success(self, sample_scenario):
        """Тест успешного поиска сценария по триггеру"""
        handler = ScenarioHandler()
        trigger = {"type": "command", "value": "/start", "user_id": 123}
        
        with patch('bot.handlers.scenarios.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.scenarios.ScenarioService.get_all_scenarios', return_value=[sample_scenario]):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await handler.find_scenario_by_trigger(trigger)
                
                assert result is not None
                assert result["current_stage"]["id"] == "start_stage"
    
    @pytest.mark.asyncio
    async def test_find_scenario_by_trigger_not_found(self):
        """Тест поиска сценария когда не найден"""
        handler = ScenarioHandler()
        trigger = {"type": "unknown", "value": "unknown", "user_id": 123}
        
        with patch('bot.handlers.scenarios.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.scenarios.ScenarioService.get_all_scenarios', return_value=[]):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await handler.find_scenario_by_trigger(trigger)
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_execute_stage_success(self, mock_update, mock_context, sample_scenario):
        """Тест успешного выполнения этапа"""
        handler = ScenarioHandler()
        
        # Подготавливаем сценарий с правильной структурой
        scenario = sample_scenario.copy()
        scenario["current_stage"] = sample_scenario["stages"][0]
        scenario["current_stage_id"] = "start_stage"
        
        with patch('bot.handlers.scenarios.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.scenarios.UserService.get_or_create_user') as mock_get_user:
                with patch('bot.handlers.scenarios.TextService.get_text', return_value="Test text"):
                    with patch.object(handler, 'get_buttons_from_database', return_value=["Button 1"]):
                        with patch.object(handler, 'process_stage_conditions'):
                            mock_session = AsyncMock()
                            mock_session_maker.return_value.__aenter__.return_value = mock_session
                            
                            mock_user = MagicMock()
                            mock_user.language = "ru"
                            mock_get_user.return_value = mock_user
                            
                            await handler.execute_stage(mock_update, mock_context, scenario)
                            
                            # Проверяем, что сообщение было отправлено
                            mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_buttons_from_database_success(self, sample_scenario):
        """Тест успешного получения кнопок из базы данных"""
        handler = ScenarioHandler()
        stage = sample_scenario["stages"][0]
        
        with patch('bot.handlers.scenarios.TextService.get_text', return_value="Button Text"):
            result = await handler.get_buttons_from_database(None, stage, "ru", 123)
            
            assert result == ["Button Text", "Button Text"]
    
    @pytest.mark.asyncio
    async def test_get_buttons_from_database_empty(self, sample_scenario):
        """Тест получения кнопок когда их нет"""
        handler = ScenarioHandler()
        stage = {"buttons": []}
        
        result = await handler.get_buttons_from_database(None, stage, "ru", 123)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_check_address_validity_valid(self):
        """Тест проверки валидности адреса - валидный"""
        handler = ScenarioHandler()
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=True):
            result = await handler.check_address_validity(address)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_address_validity_invalid(self):
        """Тест проверки валидности адреса - невалидный"""
        handler = ScenarioHandler()
        address = "invalid_address"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=False):
            result = await handler.check_address_validity(address)
            
            assert result is False


class TestCheckHandler:
    """Тесты для обработчика проверок"""
    
    def test_check_handler_initialization(self):
        """Тест инициализации обработчика проверок"""
        handler = CheckHandler()
        assert handler.logger is not None
        assert handler.logger.name == "CheckHandler"
    
    @pytest.mark.asyncio
    async def test_handle_valid_address(self, mock_update, mock_context, sample_addresses):
        """Тест обработки валидного адреса"""
        handler = CheckHandler()
        mock_update.message.text = sample_addresses["bitcoin"]
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=True):
            with patch('common.chain_detector.detect_chain', return_value="btc"):
                with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
                    with patch('bot.handlers.checks.UserService.get_or_create_user') as mock_get_user:
                        with patch.object(handler, 'check_user_limits') as mock_check_limits:
                            with patch.object(handler, 'execute_check') as mock_execute:
                                mock_session = AsyncMock()
                                mock_session_maker.return_value.__aenter__.return_value = mock_session
                                
                                mock_user = MagicMock()
                                mock_get_user.return_value = mock_user
                                
                                mock_check_limits.return_value = {
                                    "can_check": True,
                                    "check_type": "free"
                                }
                                
                                result = await handler.handle(mock_update, mock_context)
                                
                                assert result is True
                                mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_address(self, mock_update, mock_context):
        """Тест обработки невалидного адреса"""
        handler = CheckHandler()
        mock_update.message.text = "invalid_address"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=False):
            with patch.object(handler, 'handle_invalid_address') as mock_handle_invalid:
                result = await handler.handle(mock_update, mock_context)
                
                assert result is True
                mock_handle_invalid.assert_called_once_with(mock_update, "invalid_address")
    
    @pytest.mark.asyncio
    async def test_handle_invalid_address_success(self, mock_update):
        """Тест успешной обработки невалидного адреса"""
        handler = CheckHandler()
        address = "invalid_address"
        
        with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.checks.TextService.get_text', return_value="Invalid address"):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                await handler.handle_invalid_address(mock_update, address)
                
                mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_user_limits_sufficient_balance(self):
        """Тест проверки лимитов пользователя - достаточный баланс"""
        handler = CheckHandler()
        user = MagicMock()
        user.balance = 5.0
        user.is_blocked = False
        
        with patch('bot.handlers.checks.SettingService.get_paid_check_price', return_value=1.0):
            result = await handler.check_user_limits(None, user)
            
            assert result["can_check"] is True
            assert result["check_type"] == "paid"
            assert result["balance"] == 5.0
    
    @pytest.mark.asyncio
    async def test_check_user_limits_insufficient_balance_free_available(self):
        """Тест проверки лимитов - недостаточный баланс, но доступны бесплатные"""
        handler = CheckHandler()
        user = MagicMock()
        user.balance = 0.0
        user.is_blocked = False
        
        with patch('bot.handlers.checks.SettingService.get_paid_check_price', return_value=1.0):
            with patch('bot.handlers.checks.UserService.can_use_free_check', return_value=(True, 5)):
                result = await handler.check_user_limits(None, user)
                
                assert result["can_check"] is True
                assert result["check_type"] == "free"
                assert result["remaining_free"] == 5
    
    @pytest.mark.asyncio
    async def test_check_user_limits_blocked_user(self):
        """Тест проверки лимитов - заблокированный пользователь"""
        handler = CheckHandler()
        user = MagicMock()
        user.is_blocked = True
        
        result = await handler.check_user_limits(None, user)
        
        assert result["can_check"] is False
        assert result["reason"] == "blocked"
    
    @pytest.mark.asyncio
    async def test_execute_check_success(self, mock_update, mock_context):
        """Тест успешного выполнения проверки"""
        handler = CheckHandler()
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        user = MagicMock()
        check_type = "free"
        
        with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.checks.CheckService.create_check') as mock_create_check:
                with patch.object(handler, 'get_check_result_text', return_value="Check result"):
                    with patch.object(handler, 'send_check_result') as mock_send_result:
                        mock_session = AsyncMock()
                        mock_session_maker.return_value.__aenter__.return_value = mock_session
                        
                        mock_create_check.return_value = MagicMock()
                        
                        await handler.execute_check(mock_update, mock_context, address, chain, user, check_type)
                        
                        mock_create_check.assert_called_once()
                        mock_send_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_check_result_text_success(self):
        """Тест получения текста результата проверки"""
        handler = CheckHandler()
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        check_type = "free"
        user = MagicMock()
        user.language = "ru"
        user.balance = 5.0
        
        with patch('bot.handlers.checks.TextService.get_text', return_value="Check result for {address} on {chain}"):
            with patch('bot.handlers.checks.SettingService.get_paid_check_price', return_value=1.0):
                result = await handler.get_check_result_text(None, address, chain, check_type, user)
                
                assert "Check result for" in result
                assert address in result
                assert chain in result


class TestCheckValidator:
    """Тесты для валидатора проверок"""
    
    @pytest.mark.asyncio
    async def test_validate_address_valid(self, sample_addresses):
        """Тест валидации валидного адреса"""
        address = sample_addresses["bitcoin"]
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=True):
            is_valid, error = await CheckValidator.validate_address(address)
            
            assert is_valid is True
            assert error is None
    
    @pytest.mark.asyncio
    async def test_validate_address_invalid(self):
        """Тест валидации невалидного адреса"""
        address = "invalid"
        
        with patch('common.chain_detector.is_valid_crypto_address', return_value=False):
            is_valid, error = await CheckValidator.validate_address(address)
            
            assert is_valid is False
            assert error == "Неверный формат адреса"
    
    @pytest.mark.asyncio
    async def test_validate_address_too_short(self):
        """Тест валидации слишком короткого адреса"""
        address = "short"
        
        is_valid, error = await CheckValidator.validate_address(address)
        
        assert is_valid is False
        assert error == "Адрес слишком короткий"
    
    @pytest.mark.asyncio
    async def test_validate_user_permissions_valid(self):
        """Тест валидации прав пользователя - валидный"""
        user_id = 123
        
        with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.checks.UserService.get_user_by_tg_id') as mock_get_user:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                mock_user = MagicMock()
                mock_user.is_blocked = False
                mock_get_user.return_value = mock_user
                
                is_valid, error = await CheckValidator.validate_user_permissions(user_id)
                
                assert is_valid is True
                assert error is None
    
    @pytest.mark.asyncio
    async def test_validate_user_permissions_blocked(self):
        """Тест валидации прав пользователя - заблокированный"""
        user_id = 123
        
        with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.checks.UserService.get_user_by_tg_id') as mock_get_user:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                mock_user = MagicMock()
                mock_user.is_blocked = True
                mock_get_user.return_value = mock_user
                
                is_valid, error = await CheckValidator.validate_user_permissions(user_id)
                
                assert is_valid is False
                assert error == "Пользователь заблокирован"
    
    @pytest.mark.asyncio
    async def test_get_check_cost(self):
        """Тест получения стоимости проверки"""
        user_id = 123
        
        with patch('bot.handlers.checks.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.checks.SettingService.get_paid_check_price', return_value=1.5):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                cost = await CheckValidator.get_check_cost(user_id)
                
                assert cost == 1.5


class TestCheckResultFormatter:
    """Тесты для форматировщика результатов проверок"""
    
    def test_format_chain_info_known_chain(self):
        """Тест форматирования информации о известном блокчейне"""
        result = CheckResultFormatter.format_chain_info("btc")
        assert result == "₿ BTC"
    
    def test_format_chain_info_unknown_chain(self):
        """Тест форматирования информации о неизвестном блокчейне"""
        result = CheckResultFormatter.format_chain_info("unknown")
        assert result == "🔗 UNKNOWN"
    
    def test_format_address_short(self):
        """Тест форматирования короткого адреса"""
        address = "short_address"
        result = CheckResultFormatter.format_address(address)
        assert result == address
    
    def test_format_address_long(self):
        """Тест форматирования длинного адреса"""
        address = "very_long_address_that_needs_truncation"
        result = CheckResultFormatter.format_address(address)
        assert len(result) < len(address)
        assert "..." in result
    
    def test_format_balance(self):
        """Тест форматирования баланса"""
        result = CheckResultFormatter.format_balance(5.25)
        assert result == "$5.25"
    
    def test_format_check_type_paid(self):
        """Тест форматирования типа проверки - платная"""
        result = CheckResultFormatter.format_check_type("paid")
        assert result == "🛡️ Платная проверка"
    
    def test_format_check_type_free(self):
        """Тест форматирования типа проверки - бесплатная"""
        result = CheckResultFormatter.format_check_type("free")
        assert result == "✅ Бесплатная проверка"


class TestMainHandler:
    """Тесты для главного обработчика"""
    
    def test_main_handler_initialization(self):
        """Тест инициализации главного обработчика"""
        handler = MainHandler()
        assert handler.scenario_handler is not None
        assert handler.check_handler is not None
        assert isinstance(handler.scenario_handler, ScenarioHandler)
        assert isinstance(handler.check_handler, CheckHandler)
    
    @pytest.mark.asyncio
    async def test_handle_start_command(self, mock_update, mock_context):
        """Тест обработки команды /start"""
        handler = MainHandler()
        
        with patch('bot.handlers.main_handler.async_session_maker') as mock_session_maker:
            with patch('bot.handlers.main_handler.TextService.get_text', return_value="Welcome"):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await handler.handle_start_command(mock_update, mock_context)
                
                assert result is True
                mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_address_input(self, mock_update, mock_context):
        """Тест обработки ввода адреса"""
        handler = MainHandler()
        mock_update.message.text = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        with patch('bot.handlers.main_handler.TriggerDetector.detect_trigger') as mock_detect:
            with patch.object(handler.check_handler, 'handle', return_value=True):
                mock_detect.return_value = {"type": "address_input", "value": mock_update.message.text}
                
                result = await handler.handle(mock_update, mock_context)
                
                assert result is True
                handler.check_handler.handle.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_handle_scenario(self, mock_update, mock_context):
        """Тест обработки сценария"""
        handler = MainHandler()
        mock_update.message.text = "🔍 Проверка"
        
        with patch('bot.handlers.main_handler.TriggerDetector.detect_trigger') as mock_detect:
            with patch.object(handler.check_handler, 'handle', return_value=False):
                with patch.object(handler.scenario_handler, 'handle', return_value=True):
                    mock_detect.return_value = {"type": "button", "value": mock_update.message.text}
                    
                    result = await handler.handle(mock_update, mock_context)
                    
                    assert result is True
                    handler.scenario_handler.handle.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_handle_fallback(self, mock_update, mock_context):
        """Тест обработки fallback"""
        handler = MainHandler()
        mock_update.message.text = "unknown message"
        
        with patch('bot.handlers.main_handler.TriggerDetector.detect_trigger') as mock_detect:
            with patch.object(handler.check_handler, 'handle', return_value=False):
                with patch.object(handler.scenario_handler, 'handle', return_value=False):
                    mock_detect.return_value = {"type": "text_equals", "value": mock_update.message.text}
                    
                    result = await handler.handle(mock_update, mock_context)
                    
                    assert result is True
                    mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_exception(self, mock_update, mock_context):
        """Тест обработки исключения"""
        handler = MainHandler()
        
        with patch('bot.handlers.main_handler.TriggerDetector.detect_trigger', side_effect=Exception("Test error")):
            with patch.object(handler, 'handle_error') as mock_handle_error:
                result = await handler.handle(mock_update, mock_context)
                
                assert result is False
                mock_handle_error.assert_called_once_with(mock_update, mock_context)
