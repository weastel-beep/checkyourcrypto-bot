"""
Единый API роутер для объединенного API
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from common.database import get_db
from common.services.unified import UnifiedTextService, UnifiedScenarioService, UnifiedSettingService
from common.schemas.unified import (
    TextCreate, TextUpdate, TextResponse,
    ScenarioCreate, ScenarioUpdate, ScenarioResponse,
    SettingCreate, SettingUpdate, SettingResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/unified", tags=["unified"])

# ============================================================================
# TEXT ENDPOINTS
# ============================================================================

@router.get("/texts", response_model=List[TextResponse])
async def get_texts(
    category: Optional[str] = None,
    language: str = "ru",
    db: Session = Depends(get_db)
):
    """Получение всех текстов с фильтрацией"""
    try:
        texts = UnifiedTextService.get_texts(db, category, language)
        return texts
    except Exception as e:
        logger.error(f"Ошибка при получении текстов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/texts/{text_id}", response_model=TextResponse)
async def get_text_by_id(
    text_id: int,
    db: Session = Depends(get_db)
):
    """Получение текста по ID"""
    try:
        text = UnifiedTextService.get_text_by_id(db, text_id)
        if not text:
            raise HTTPException(status_code=404, detail="Текст не найден")
        return text
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении текста {text_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/texts", response_model=TextResponse)
async def create_text(
    text: TextCreate,
    db: Session = Depends(get_db)
):
    """Создание нового текста"""
    try:
        return UnifiedTextService.create_text(db, text)
    except Exception as e:
        logger.error(f"Ошибка при создании текста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/texts/{text_id}", response_model=TextResponse)
async def update_text(
    text_id: int,
    text_update: TextUpdate,
    db: Session = Depends(get_db)
):
    """Обновление текста"""
    try:
        text = UnifiedTextService.update_text(db, text_id, text_update)
        if not text:
            raise HTTPException(status_code=404, detail="Текст не найден")
        return text
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста {text_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/texts/{text_id}")
async def delete_text(
    text_id: int,
    db: Session = Depends(get_db)
):
    """Удаление текста"""
    try:
        success = UnifiedTextService.delete_text(db, text_id)
        if not success:
            raise HTTPException(status_code=404, detail="Текст не найден")
        return {"message": "Текст успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении текста {text_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SCENARIO ENDPOINTS
# ============================================================================

@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios(db: Session = Depends(get_db)):
    """Получение всех сценариев"""
    try:
        scenarios = UnifiedScenarioService.get_scenarios(db)
        return scenarios
    except Exception as e:
        logger.error(f"Ошибка при получении сценариев: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/active", response_model=List[ScenarioResponse])
async def get_active_scenarios(db: Session = Depends(get_db)):
    """Получение активных сценариев"""
    try:
        scenarios = UnifiedScenarioService.get_active_scenarios(db)
        return scenarios
    except Exception as e:
        logger.error(f"Ошибка при получении активных сценариев: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_by_id(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """Получение сценария по ID"""
    try:
        scenario = UnifiedScenarioService.get_scenario_by_id(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Сценарий не найден")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении сценария {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Создание нового сценария"""
    try:
        return UnifiedScenarioService.create_scenario(db, scenario)
    except Exception as e:
        logger.error(f"Ошибка при создании сценария: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario_update: ScenarioUpdate,
    db: Session = Depends(get_db)
):
    """Обновление сценария"""
    try:
        scenario = UnifiedScenarioService.update_scenario(db, scenario_id, scenario_update)
        if not scenario:
            raise HTTPException(status_code=404, detail="Сценарий не найден")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении сценария {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """Удаление сценария"""
    try:
        success = UnifiedScenarioService.delete_scenario(db, scenario_id)
        if not success:
            raise HTTPException(status_code=404, detail="Сценарий не найден")
        return {"message": "Сценарий успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении сценария {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SETTING ENDPOINTS
# ============================================================================

@router.get("/settings", response_model=List[SettingResponse])
async def get_settings(db: Session = Depends(get_db)):
    """Получение всех настроек"""
    try:
        settings = UnifiedSettingService.get_settings(db)
        return settings
    except Exception as e:
        logger.error(f"Ошибка при получении настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{key}")
async def get_setting_by_key(
    key: str,
    db: Session = Depends(get_db)
):
    """Получение настройки по ключу"""
    try:
        setting = UnifiedSettingService.get_setting_by_key(db, key)
        if not setting:
            raise HTTPException(status_code=404, detail="Настройка не найдена")
        return setting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении настройки {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings", response_model=SettingResponse)
async def create_setting(
    setting: SettingCreate,
    db: Session = Depends(get_db)
):
    """Создание новой настройки"""
    try:
        return UnifiedSettingService.create_setting(db, setting)
    except Exception as e:
        logger.error(f"Ошибка при создании настройки: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{setting_id}", response_model=SettingResponse)
async def update_setting(
    setting_id: int,
    setting_update: SettingUpdate,
    db: Session = Depends(get_db)
):
    """Обновление настройки"""
    try:
        setting = UnifiedSettingService.update_setting(db, setting_id, setting_update)
        if not setting:
            raise HTTPException(status_code=404, detail="Настройка не найдена")
        return setting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении настройки {setting_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/settings/{setting_id}")
async def delete_setting(
    setting_id: int,
    db: Session = Depends(get_db)
):
    """Удаление настройки"""
    try:
        success = UnifiedSettingService.delete_setting(db, setting_id)
        if not success:
            raise HTTPException(status_code=404, detail="Настройка не найдена")
        return {"message": "Настройка успешно удалена"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении настройки {setting_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKWARD COMPATIBILITY ENDPOINTS
# ============================================================================

@router.get("/bot-flow/scenarios")
async def get_bot_flow_scenarios(db: Session = Depends(get_db)):
    """Получение сценариев для Flow Designer (обратная совместимость)"""
    try:
        scenarios = UnifiedScenarioService.get_scenarios(db)
        return scenarios
    except Exception as e:
        logger.error(f"Ошибка при получении сценариев для Flow Designer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot-flow/texts")
async def get_bot_flow_texts(db: Session = Depends(get_db)):
    """Получение текстов для Flow Designer (обратная совместимость)"""
    try:
        texts = UnifiedTextService.get_texts(db)
        return texts
    except Exception as e:
        logger.error(f"Ошибка при получении текстов для Flow Designer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check для единого API"""
    return {
        "status": "ok",
        "service": "Unified API",
        "version": "1.0.0"
    }
