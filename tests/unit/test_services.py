"""
Unit тесты для сервисов
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from common.services import UserService, CheckService, TextService, SettingService
from common.services_package.scenario_service import ScenarioService
from common.chain_detector import detect_chain, is_valid_crypto_address


class TestUserService:
    """Тесты для сервиса пользователей"""
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_new_user(self, sample_user_data):
        """Тест создания нового пользователя"""
        tg_id = 123456789
        language = "ru"
        username = "test_user"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.UserService.get_user_by_tg_id', return_value=None):
                with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                    mock_session = AsyncMock()
                    mock_session_maker.return_value.__aenter__.return_value = mock_session
                    
                    # Правильно мокаем HTTP сессию
                    mock_http_session = AsyncMock()
                    mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                    mock_http_session.__aexit__ = AsyncMock(return_value=None)
                    
                    mock_response = AsyncMock()
                    mock_response.status = 201
                    mock_response.json = AsyncMock(return_value=sample_user_data)
                    
                    mock_http_session.post.return_value = mock_response
                    mock_client_session.return_value = mock_http_session
                    
                    result = await UserService.get_or_create_user(mock_session, tg_id, language, username)
                    
                    assert result.tg_id == sample_user_data["tg_id"]
                    assert result.username == sample_user_data["username"]
                    assert result.language == sample_user_data["language"]
                    assert result.balance == Decimal(str(sample_user_data["balance"]))
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_user(self, sample_user_data):
        """Тест получения существующего пользователя"""
        tg_id = 123456789
        language = "ru"
        username = "test_user"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.UserService.get_user_by_tg_id') as mock_get_user:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                existing_user = MagicMock()
                existing_user.tg_id = tg_id
                existing_user.username = username
                existing_user.language = language
                existing_user.balance = Decimal("5.0")
                existing_user.referral_code = "TEST123"
                existing_user.is_blocked = False
                existing_user.created_at = datetime.now()
                existing_user.updated_at = datetime.now()
                
                mock_get_user.return_value = existing_user
                
                result = await UserService.get_or_create_user(mock_session, tg_id, language, username)
                
                assert result == existing_user
    
    @pytest.mark.asyncio
    async def test_get_user_by_tg_id_success(self, sample_user_data):
        """Тест успешного получения пользователя по tg_id"""
        tg_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=sample_user_data)
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await UserService.get_user_by_tg_id(mock_session, tg_id)
                
                assert result.tg_id == sample_user_data["tg_id"]
                assert result.username == sample_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_tg_id_not_found(self):
        """Тест получения пользователя когда не найден"""
        tg_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 404
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await UserService.get_user_by_tg_id(mock_session, tg_id)
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_update_user_language(self):
        """Тест обновления языка пользователя"""
        tg_id = 123456789
        language = "en"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            
            result = await UserService.update_user_language(mock_session, tg_id, language)
            
            assert result is True
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_referral_code(self):
        """Тест получения пользователя по реферальному коду"""
        referral_code = "TEST123"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_user = MagicMock()
            mock_user.referral_code = referral_code
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result
            
            result = await UserService.get_user_by_referral_code(mock_session, referral_code)
            
            assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_can_use_free_check(self):
        """Тест проверки возможности использования бесплатной проверки"""
        user = MagicMock()
        user.tg_id = 123456789
        
        with patch('common.services.check_limits') as mock_check_limits:
            mock_check_limits.can_perform_free_check.return_value = (True, 5)
            
            result = await UserService.can_use_free_check(None, user)
            
            assert result == (True, 5)
    
    @pytest.mark.asyncio
    async def test_update_last_free_check(self):
        """Тест обновления времени последней бесплатной проверки"""
        user = MagicMock()
        user.tg_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            await UserService.update_last_free_check(mock_session, user)
            
            assert user.last_free_check is not None
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_balance(self):
        """Тест пополнения баланса"""
        user = MagicMock()
        user.balance = Decimal("5.0")
        amount = Decimal("10.0")
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            await UserService.add_balance(mock_session, user, amount)
            
            assert user.balance == Decimal("15.0")
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deduct_balance_success(self):
        """Тест списания баланса - успешно"""
        user = MagicMock()
        user.balance = Decimal("10.0")
        amount = Decimal("5.0")
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            result = await UserService.deduct_balance(mock_session, user, amount)
            
            assert result is True
            assert user.balance == Decimal("5.0")
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deduct_balance_insufficient(self):
        """Тест списания баланса - недостаточно средств"""
        user = MagicMock()
        user.balance = Decimal("3.0")
        amount = Decimal("5.0")
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            result = await UserService.deduct_balance(mock_session, user, amount)
            
            assert result is False
            assert user.balance == Decimal("3.0")
    
    def test_is_user_blocked_true(self):
        """Тест проверки блокировки пользователя - заблокирован"""
        user = MagicMock()
        user.is_blocked = True
        
        result = UserService.is_user_blocked(user)
        
        assert result is True
    
    def test_is_user_blocked_false(self):
        """Тест проверки блокировки пользователя - не заблокирован"""
        user = MagicMock()
        user.is_blocked = False
        
        result = UserService.is_user_blocked(user)
        
        assert result is False
    
    def test_generate_referral_code(self):
        """Тест генерации реферального кода"""
        code = UserService._generate_referral_code()
        
        assert len(code) == 8
        assert code.isalnum()
        assert code.isupper()


class TestCheckService:
    """Тесты для сервиса проверок"""
    
    @pytest.mark.asyncio
    async def test_create_check(self):
        """Тест создания проверки"""
        user_id = 123456789
        address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        chain = "btc"
        check_type = "free"
        result = {"status": "completed"}
        
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
            
            mock_session.refresh.return_value = mock_check
            
            result_check = await CheckService.create_check(mock_session, user_id, address, chain, check_type, result)
            
            assert result_check.user_id == user_id
            assert result_check.address == address
            assert result_check.chain == chain
            assert result_check.type == check_type
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_checks(self):
        """Тест получения проверок пользователя"""
        user_id = 123456789
        limit = 10
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_checks = [MagicMock(), MagicMock()]
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_checks
            mock_session.execute.return_value = mock_result
            
            result = await CheckService.get_user_checks(mock_session, user_id, limit)
            
            assert result == mock_checks
    
    @pytest.mark.asyncio
    async def test_get_check_by_id(self):
        """Тест получения проверки по ID"""
        check_id = 1
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_check = MagicMock()
            mock_check.id = check_id
            mock_session.get.return_value = mock_check
            
            result = await CheckService.get_check_by_id(mock_session, check_id)
            
            assert result == mock_check
    
    @pytest.mark.asyncio
    async def test_get_checks_today(self):
        """Тест получения проверок за сегодня"""
        user_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_checks = [MagicMock(), MagicMock(), MagicMock()]
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_checks
            mock_session.execute.return_value = mock_result
            
            result = await CheckService.get_checks_today(mock_session, user_id)
            
            assert result == 3


class TestTextService:
    """Тесты для сервиса текстов"""
    
    @pytest.mark.asyncio
    async def test_get_text_success(self, sample_texts):
        """Тест успешного получения текста"""
        key = "welcome"
        language = "ru"
        user_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
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
                            "content": sample_texts[key]
                        }
                    ]
                })
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await TextService.get_text(mock_session, key, language, user_id)
                
                assert result == sample_texts[key]
    
    @pytest.mark.asyncio
    async def test_get_text_not_found(self):
        """Тест получения текста когда не найден"""
        key = "unknown_key"
        language = "ru"
        user_id = 123456789
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"texts": []})
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await TextService.get_text(mock_session, key, language, user_id)
                
                assert result == key
    
    @pytest.mark.asyncio
    async def test_set_text(self):
        """Тест установки текста"""
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
    
    @pytest.mark.asyncio
    async def test_get_menu_success(self):
        """Тест успешного получения меню"""
        menu_key = "main_menu"
        language = "ru"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_menu_text = MagicMock()
            mock_menu_text.content = '{"buttons": ["Button 1", "Button 2"]}'
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_menu_text
            mock_session.execute.return_value = mock_result
            
            result = await TextService.get_menu(mock_session, menu_key, language)
            
            assert result == {"buttons": ["Button 1", "Button 2"]}


class TestSettingService:
    """Тесты для сервиса настроек"""
    
    @pytest.mark.asyncio
    async def test_get_paid_check_price(self, sample_settings):
        """Тест получения цены платной проверки"""
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.SettingService.get_setting') as mock_get_setting:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                mock_get_setting.return_value = sample_settings["paid_check_price"]
                
                result = await SettingService.get_paid_check_price(mock_session)
                
                assert result == float(sample_settings["paid_check_price"])
    
    @pytest.mark.asyncio
    async def test_get_paid_check_price_default(self):
        """Тест получения цены платной проверки по умолчанию"""
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.SettingService.get_setting', return_value=None):
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                result = await SettingService.get_paid_check_price(mock_session)
                
                assert result == 1.0
    
    @pytest.mark.asyncio
    async def test_get_setting_success(self, sample_settings):
        """Тест успешного получения настройки"""
        key = "paid_check_price"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"value": sample_settings[key]})
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await SettingService.get_setting(mock_session, key)
                
                assert result == sample_settings[key]
    
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self):
        """Тест получения настройки когда не найдена"""
        key = "unknown_setting"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 404
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await SettingService.get_setting(mock_session, key)
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_set_setting(self, sample_settings):
        """Тест установки настройки"""
        key = "paid_check_price"
        value = "2.00"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                
                mock_http_session.put.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                await SettingService.set_setting(mock_session, key, value)
                
                mock_http_session.put.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_block_user(self):
        """Тест блокировки пользователя"""
        user = MagicMock()
        user.tg_id = 123456789
        reason = "Test reason"
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            result = await SettingService.block_user(mock_session, user, reason)
            
            assert result is True
            assert user.is_blocked is True
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unblock_user(self):
        """Тест разблокировки пользователя"""
        user = MagicMock()
        user.tg_id = 123456789
        user.is_blocked = True
        
        with patch('common.database.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            result = await SettingService.unblock_user(mock_session, user)
            
            assert result is True
            assert user.is_blocked is False
            mock_session.commit.assert_called_once()
    
    def test_get_default_settings(self, sample_settings):
        """Тест получения настроек по умолчанию"""
        result = SettingService.get_default_settings()
        
        assert result["paid_check_price"] == sample_settings["paid_check_price"]
        assert result["referral_bonus"] == sample_settings["referral_bonus"]
        assert result["max_free_checks_per_day"] == sample_settings["max_free_checks_per_day"]


class TestScenarioService:
    """Тесты для сервиса сценариев"""
    
    @pytest.mark.asyncio
    async def test_get_active_scenario_success(self, sample_scenario):
        """Тест успешного получения активного сценария"""
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services_package.scenario_service.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"scenarios": [sample_scenario]})
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await ScenarioService.get_active_scenario(mock_session)
                
                assert result == sample_scenario
    
    @pytest.mark.asyncio
    async def test_get_active_scenario_not_found(self):
        """Тест получения активного сценария когда не найден"""
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services_package.scenario_service.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"scenarios": []})
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await ScenarioService.get_active_scenario(mock_session)
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_scenarios_success(self, sample_scenario):
        """Тест успешного получения всех сценариев"""
        with patch('common.database.async_session_maker') as mock_session_maker:
            with patch('common.services_package.scenario_service.aiohttp.ClientSession') as mock_client_session:
                mock_session = AsyncMock()
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                
                # Правильно мокаем HTTP сессию
                mock_http_session = AsyncMock()
                mock_http_session.__aenter__ = AsyncMock(return_value=mock_http_session)
                mock_http_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=[sample_scenario])
                
                mock_http_session.get.return_value = mock_response
                mock_client_session.return_value = mock_http_session
                
                result = await ScenarioService.get_all_scenarios(mock_session)
                
                assert result == [sample_scenario]
    
    @pytest.mark.asyncio
    async def test_get_stage_success(self, sample_scenario):
        """Тест успешного получения этапа"""
        stage_name = "start_stage"
        
        result = await ScenarioService.get_stage(sample_scenario, stage_name)
        
        assert result is not None
        assert result["id"] == stage_name
    
    @pytest.mark.asyncio
    async def test_get_stage_not_found(self, sample_scenario):
        """Тест получения этапа когда не найден"""
        stage_name = "unknown_stage"
        
        result = await ScenarioService.get_stage(sample_scenario, stage_name)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_next_stage_success(self, sample_scenario):
        """Тест успешного получения следующего этапа"""
        current_stage = "start_stage"
        
        result = await ScenarioService.get_next_stage(sample_scenario, current_stage)
        
        assert result == "check_stage"
    
    @pytest.mark.asyncio
    async def test_get_next_stage_not_found(self, sample_scenario):
        """Тест получения следующего этапа когда не найден"""
        current_stage = "unknown_stage"
        
        result = await ScenarioService.get_next_stage(sample_scenario, current_stage)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_stage_type_success(self, sample_scenario):
        """Тест успешного получения типа этапа"""
        stage_name = "start_stage"
        
        result = await ScenarioService.get_stage_type(sample_scenario, stage_name)
        
        assert result == "command"
    
    @pytest.mark.asyncio
    async def test_get_stage_buttons_success(self, sample_scenario):
        """Тест успешного получения кнопок этапа"""
        stage_name = "start_stage"
        
        result = await ScenarioService.get_stage_buttons(sample_scenario, stage_name)
        
        assert len(result) == 2
        assert result[0]["text"] == "check_button"
        assert result[1]["text"] == "balance_button"
    
    @pytest.mark.asyncio
    async def test_replace_placeholders_in_text(self):
        """Тест замены плейсхолдеров в тексте"""
        text = "Hello {user_id}, your balance is {balance}"
        user_id = 123456789
        
        with patch('common.services_package.scenario_service.PlaceholderService') as mock_placeholder_service:
            mock_placeholder_service.replace_placeholders.return_value = "Hello 123456789, your balance is 5.0"
            
            result = await ScenarioService.replace_placeholders_in_text(None, text, user_id)
            
            assert result == "Hello 123456789, your balance is 5.0"
            mock_placeholder_service.replace_placeholders.assert_called_once_with(None, text, user_id)
