"""
Единые сервисы для объединенного API
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from common.models.unified import UnifiedBotText, UnifiedScenario, UnifiedSetting
from common.schemas.unified import TextCreate, TextUpdate, ScenarioCreate, ScenarioUpdate, SettingCreate, SettingUpdate

logger = logging.getLogger(__name__)


class UnifiedTextService:
    """Единый сервис для работы с текстами"""
    
    @staticmethod
    def get_texts(session: Session, category: Optional[str] = None, language: str = "ru") -> List[UnifiedBotText]:
        """Получить все тексты с фильтрацией"""
        query = session.query(UnifiedBotText).filter(UnifiedBotText.language == language)
        if category:
            query = query.filter(UnifiedBotText.category == category)
        return query.all()
    
    @staticmethod
    def get_text_by_id(session: Session, text_id: int) -> Optional[UnifiedBotText]:
        """Получить текст по ID"""
        return session.query(UnifiedBotText).filter(UnifiedBotText.id == text_id).first()
    
    @staticmethod
    def create_text(session: Session, text_data: TextCreate) -> UnifiedBotText:
        """Создать новый текст"""
        text = UnifiedBotText(**text_data.dict())
        session.add(text)
        session.commit()
        session.refresh(text)
        logger.info(f"Создан новый текст: {text.id}")
        return text
    
    @staticmethod
    def update_text(session: Session, text_id: int, text_data: TextUpdate) -> Optional[UnifiedBotText]:
        """Обновить текст"""
        text = session.query(UnifiedBotText).filter(UnifiedBotText.id == text_id).first()
        if text:
            for field, value in text_data.dict(exclude_unset=True).items():
                setattr(text, field, value)
            session.commit()
            session.refresh(text)
            logger.info(f"Обновлен текст: {text_id}")
        return text
    
    @staticmethod
    def delete_text(session: Session, text_id: int) -> bool:
        """Удалить текст"""
        text = session.query(UnifiedBotText).filter(UnifiedBotText.id == text_id).first()
        if text:
            session.delete(text)
            session.commit()
            logger.info(f"Удален текст: {text_id}")
            return True
        return False


class UnifiedScenarioService:
    """Единый сервис для работы со сценариями"""
    
    @staticmethod
    def get_scenarios(session: Session) -> List[UnifiedScenario]:
        """Получить все сценарии"""
        return session.query(UnifiedScenario).all()
    
    @staticmethod
    def get_scenario_by_id(session: Session, scenario_id: int) -> Optional[UnifiedScenario]:
        """Получить сценарий по ID"""
        return session.query(UnifiedScenario).filter(UnifiedScenario.id == scenario_id).first()
    
    @staticmethod
    def get_active_scenarios(session: Session) -> List[UnifiedScenario]:
        """Получить активные сценарии"""
        return session.query(UnifiedScenario).filter(UnifiedScenario.is_active == True).all()
    
    @staticmethod
    def create_scenario(session: Session, scenario_data: ScenarioCreate) -> UnifiedScenario:
        """Создать новый сценарий"""
        scenario = UnifiedScenario(**scenario_data.dict())
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        logger.info(f"Создан новый сценарий: {scenario.id}")
        return scenario
    
    @staticmethod
    def update_scenario(session: Session, scenario_id: int, scenario_data: ScenarioUpdate) -> Optional[UnifiedScenario]:
        """Обновить сценарий"""
        scenario = session.query(UnifiedScenario).filter(UnifiedScenario.id == scenario_id).first()
        if scenario:
            for field, value in scenario_data.dict(exclude_unset=True).items():
                setattr(scenario, field, value)
            session.commit()
            session.refresh(scenario)
            logger.info(f"Обновлен сценарий: {scenario_id}")
        return scenario
    
    @staticmethod
    def delete_scenario(session: Session, scenario_id: int) -> bool:
        """Удалить сценарий"""
        scenario = session.query(UnifiedScenario).filter(UnifiedScenario.id == scenario_id).first()
        if scenario:
            session.delete(scenario)
            session.commit()
            logger.info(f"Удален сценарий: {scenario_id}")
            return True
        return False


class UnifiedSettingService:
    """Единый сервис для работы с настройками"""
    
    @staticmethod
    def get_settings(session: Session) -> List[UnifiedSetting]:
        """Получить все настройки"""
        return session.query(UnifiedSetting).all()
    
    @staticmethod
    def get_setting_by_key(session: Session, key: str) -> Optional[UnifiedSetting]:
        """Получить настройку по ключу"""
        return session.query(UnifiedSetting).filter(UnifiedSetting.key == key).first()
    
    @staticmethod
    def create_setting(session: Session, setting_data: SettingCreate) -> UnifiedSetting:
        """Создать новую настройку"""
        setting = UnifiedSetting(**setting_data.dict())
        session.add(setting)
        session.commit()
        session.refresh(setting)
        logger.info(f"Создана новая настройка: {setting.key}")
        return setting
    
    @staticmethod
    def update_setting(session: Session, setting_id: int, setting_data: SettingUpdate) -> Optional[UnifiedSetting]:
        """Обновить настройку"""
        setting = session.query(UnifiedSetting).filter(UnifiedSetting.id == setting_id).first()
        if setting:
            for field, value in setting_data.dict(exclude_unset=True).items():
                setattr(setting, field, value)
            session.commit()
            session.refresh(setting)
            logger.info(f"Обновлена настройка: {setting.key}")
        return setting
    
    @staticmethod
    def delete_setting(session: Session, setting_id: int) -> bool:
        """Удалить настройку"""
        setting = session.query(UnifiedSetting).filter(UnifiedSetting.id == setting_id).first()
        if setting:
            session.delete(setting)
            session.commit()
            logger.info(f"Удалена настройка: {setting.key}")
            return True
        return False
