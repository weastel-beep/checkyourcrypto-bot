"""
API endpoints для работы с конструктором сценариев
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import json

from common.database import async_session_maker
from common.models import BotText, Scenario, Setting
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Создаем router для API
api_router = APIRouter(prefix="/api", tags=["API"])

# Pydantic модели
class BotTextCreate(BaseModel):
    category: str
    language: str = "ru"
    content: str
    version: int = 1

class BotTextUpdate(BaseModel):
    content: str

class ScenarioCreate(BaseModel):
    name: str
    description: str = ""
    is_active: bool = False
    stages: List[Dict[str, Any]] = []

class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    stages: Optional[List[Dict[str, Any]]] = None

class SettingCreate(BaseModel):
    key: str
    value: str

class SettingUpdate(BaseModel):
    value: str

# API endpoints для текстов
@api_router.get("/texts")
async def get_texts():
    """Получение всех текстов"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(BotText))
            texts = result.scalars().all()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": text.id,
                        "category": text.category,
                        "language": text.language,
                        "content": text.content,
                        "version": text.version,
                        "created_at": text.created_at.isoformat() if text.created_at else None,
                        "updated_at": text.updated_at.isoformat() if text.updated_at else None
                    }
                    for text in texts
                ]
            }
    except Exception as e:
        logger.error(f"Ошибка при получении текстов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/texts")
async def create_text(text: BotTextCreate):
    """Создание нового текста"""
    try:
        async with async_session_maker() as session:
            new_text = BotText(
                category=text.category,
                language=text.language,
                content=text.content,
                version=text.version
            )
            session.add(new_text)
            await session.commit()
            await session.refresh(new_text)
            
            return {
                "status": "success",
                "data": {
                    "id": new_text.id,
                    "category": new_text.category,
                    "language": new_text.language,
                    "content": new_text.content,
                    "version": new_text.version
                }
            }
    except Exception as e:
        logger.error(f"Ошибка при создании текста: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/texts/{text_id}")
async def update_text(text_id: int, text_update: BotTextUpdate):
    """Обновление текста"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(BotText).where(BotText.id == text_id))
            text = result.scalar_one_or_none()
            
            if not text:
                raise HTTPException(status_code=404, detail="Текст не найден")
            
            text.content = text_update.content
            text.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                "status": "success",
                "data": {
                    "id": text.id,
                    "category": text.category,
                    "language": text.language,
                    "content": text.content,
                    "version": text.version
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints для сценариев
@api_router.get("/scenarios")
async def get_scenarios():
    """Получение всех сценариев"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Scenario))
            scenarios = result.scalars().all()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": scenario.id,
                        "name": scenario.name,
                        "description": scenario.description,
                        "is_active": scenario.is_active,
                        "stages": scenario.stages if isinstance(scenario.stages, list) else (json.loads(scenario.stages) if scenario.stages else []),
                        "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
                        "updated_at": scenario.updated_at.isoformat() if scenario.updated_at else None
                    }
                    for scenario in scenarios
                ]
            }
    except Exception as e:
        logger.error(f"Ошибка при получении сценариев: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/scenarios")
async def create_scenario(scenario: ScenarioCreate):
    """Создание нового сценария"""
    try:
        async with async_session_maker() as session:
            new_scenario = Scenario(
                name=scenario.name,
                description=scenario.description,
                is_active=scenario.is_active,
                stages=json.dumps(scenario.stages) if scenario.stages else "[]"
            )
            session.add(new_scenario)
            await session.commit()
            await session.refresh(new_scenario)
            
            return {
                "status": "success",
                "data": {
                    "id": new_scenario.id,
                    "name": new_scenario.name,
                    "description": new_scenario.description,
                    "is_active": new_scenario.is_active,
                    "stages": new_scenario.stages if isinstance(new_scenario.stages, list) else (json.loads(new_scenario.stages) if new_scenario.stages else [])
                }
            }
    except Exception as e:
        logger.error(f"Ошибка при создании сценария: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/scenarios/{scenario_id}")
async def update_scenario(scenario_id: int, scenario_update: ScenarioUpdate):
    """Обновление сценария"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Scenario).where(Scenario.id == scenario_id))
            scenario = result.scalar_one_or_none()
            
            if not scenario:
                raise HTTPException(status_code=404, detail="Сценарий не найден")
            
            if scenario_update.name is not None:
                scenario.name = scenario_update.name
            if scenario_update.description is not None:
                scenario.description = scenario_update.description
            if scenario_update.is_active is not None:
                scenario.is_active = scenario_update.is_active
            if scenario_update.stages is not None:
                scenario.stages = json.dumps(scenario_update.stages)
            
            scenario.updated_at = datetime.utcnow()
            await session.commit()
            
            return {
                "status": "success",
                "data": {
                    "id": scenario.id,
                    "name": scenario.name,
                    "description": scenario.description,
                    "is_active": scenario.is_active,
                    "stages": scenario.stages if isinstance(scenario.stages, list) else (json.loads(scenario.stages) if scenario.stages else [])
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении сценария: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints для настроек
@api_router.get("/settings")
async def get_settings():
    """Получение всех настроек"""
    try:
        logger.info("🔍 Получаем настройки из БД...")
        async with async_session_maker() as session:
            result = await session.execute(select(Setting))
            settings = result.scalars().all()
            logger.info(f"✅ Найдено настроек: {len(settings)}")
            
            return {
                "status": "success",
                "data": [
                    {
                        "key": setting.key,
                        "value": setting.value,
                        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
                    }
                    for setting in settings
                ]
            }
    except Exception as e:
        logger.error(f"❌ Ошибка при получении настроек: {e}")
        logger.error(f"❌ Тип ошибки: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/settings")
async def create_setting(setting: SettingCreate):
    """Создание новой настройки"""
    try:
        async with async_session_maker() as session:
            new_setting = Setting(
                key=setting.key,
                value=setting.value
            )
            session.add(new_setting)
            await session.commit()
            await session.refresh(new_setting)
            
            return {
                "status": "success",
                "data": {
                    "key": new_setting.key,
                    "value": new_setting.value
                }
            }
    except Exception as e:
        logger.error(f"Ошибка при создании настройки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/settings/{setting_id}")
async def update_setting(setting_id: int, setting_update: SettingUpdate):
    """Обновление настройки"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Setting).where(Setting.id == setting_id))
            setting = result.scalar_one_or_none()
            
            if not setting:
                raise HTTPException(status_code=404, detail="Настройка не найдена")
            
            setting.value = setting_update.value
            setting.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                "status": "success",
                "data": {
                    "key": setting.key,
                    "value": setting.value
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении настройки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check для API
@api_router.get("/health")
async def api_health():
    """Health check для API"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Check Your Crypto Bot API"
    }
