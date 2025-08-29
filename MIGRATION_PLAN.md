# 🚀 План миграции: Объединение Bot API и Admin API

## 📋 Обзор миграции

**Цель**: Объединить дублированные API эндпоинты в единую систему
**Срок**: 4-6 недель
**Команда**: 2-3 разработчика
**Риск**: Средний (управляемый)

## 🎯 Этапы миграции

### Этап 1: Подготовка и анализ (Неделя 1)

#### 1.1 Создание бэкапа
```bash
# Создание полного бэкапа
./backup_before_changes.sh "pre-migration-backup"

# Создание git ветки
git checkout -b feature/unified-api
git push origin feature/unified-api
```

#### 1.2 Анализ зависимостей
- [ ] Составить список всех эндпоинтов в bot/api.py
- [ ] Составить список всех эндпоинтов в admin_panel_new/app/main.py
- [ ] Выявить различия в логике обработки
- [ ] Определить общие модели данных
- [ ] **КРИТИЧНО**: Проанализировать интеграцию бота с конструктором сценариев

#### 1.3 Создание staging окружения
```bash
# Настройка staging базы данных
heroku config:set DATABASE_URL=postgresql://... --app checkyourcrypto-staging

# Деплой текущей версии на staging
git push heroku feature/unified-api:main --app checkyourcrypto-staging
```

### Этап 2: Создание единых компонентов (Неделя 2)

#### 2.1 Единые модели данных
```python
# common/models/unified.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from common.database import Base

class UnifiedBotText(Base):
    """Единая модель для текстов бота"""
    __tablename__ = "bot_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="ru")
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UnifiedScenario(Base):
    """Единая модель для сценариев"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    stages = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UnifiedSetting(Base):
    """Единая модель для настроек"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 2.2 Единые сервисы
```python
# common/services/unified.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from common.models.unified import UnifiedBotText, UnifiedScenario, UnifiedSetting
from common.schemas.unified import TextCreate, TextUpdate, ScenarioCreate, ScenarioUpdate

class UnifiedTextService:
    """Единый сервис для работы с текстами"""
    
    @staticmethod
    async def get_texts(session: Session, category: Optional[str] = None, language: str = "ru") -> List[UnifiedBotText]:
        query = session.query(UnifiedBotText).filter(UnifiedBotText.language == language)
        if category:
            query = query.filter(UnifiedBotText.category == category)
        return query.all()
    
    @staticmethod
    async def create_text(session: Session, text_data: TextCreate) -> UnifiedBotText:
        text = UnifiedBotText(**text_data.dict())
        session.add(text)
        session.commit()
        session.refresh(text)
        return text
    
    @staticmethod
    async def update_text(session: Session, text_id: int, text_data: TextUpdate) -> Optional[UnifiedBotText]:
        text = session.query(UnifiedBotText).filter(UnifiedBotText.id == text_id).first()
        if text:
            for field, value in text_data.dict(exclude_unset=True).items():
                setattr(text, field, value)
            session.commit()
            session.refresh(text)
        return text

class UnifiedScenarioService:
    """Единый сервис для работы со сценариями"""
    
    @staticmethod
    async def get_scenarios(session: Session) -> List[UnifiedScenario]:
        return session.query(UnifiedScenario).all()
    
    @staticmethod
    async def create_scenario(session: Session, scenario_data: ScenarioCreate) -> UnifiedScenario:
        scenario = UnifiedScenario(**scenario_data.dict())
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        return scenario
    
    @staticmethod
    async def update_scenario(session: Session, scenario_id: int, scenario_data: ScenarioUpdate) -> Optional[UnifiedScenario]:
        scenario = session.query(UnifiedScenario).filter(UnifiedScenario.id == scenario_id).first()
        if scenario:
            for field, value in scenario_data.dict(exclude_unset=True).items():
                setattr(scenario, field, value)
            session.commit()
            session.refresh(scenario)
        return scenario
```

#### 2.3 Единые схемы Pydantic
```python
# common/schemas/unified.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TextBase(BaseModel):
    category: str
    language: str = "ru"
    content: str
    version: int = 1
    is_active: bool = True

class TextCreate(TextBase):
    pass

class TextUpdate(BaseModel):
    content: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None

class TextResponse(TextBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = False
    stages: Optional[List[Dict[str, Any]]] = None

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    stages: Optional[List[Dict[str, Any]]] = None

class ScenarioResponse(ScenarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
```

#### 2.4 Единый API роутер
```python
# common/api/unified.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from common.database import get_db
from common.services.unified import UnifiedTextService, UnifiedScenarioService
from common.schemas.unified import (
    TextCreate, TextUpdate, TextResponse,
    ScenarioCreate, ScenarioUpdate, ScenarioResponse
)

router = APIRouter(prefix="/api/unified", tags=["unified"])

# Text endpoints
@router.get("/texts", response_model=List[TextResponse])
async def get_texts(
    category: Optional[str] = None,
    language: str = "ru",
    db: Session = Depends(get_db)
):
    """Получение всех текстов"""
    texts = await UnifiedTextService.get_texts(db, category, language)
    return texts

@router.post("/texts", response_model=TextResponse)
async def create_text(
    text: TextCreate,
    db: Session = Depends(get_db)
):
    """Создание нового текста"""
    return await UnifiedTextService.create_text(db, text)

@router.put("/texts/{text_id}", response_model=TextResponse)
async def update_text(
    text_id: int,
    text_update: TextUpdate,
    db: Session = Depends(get_db)
):
    """Обновление текста"""
    text = await UnifiedTextService.update_text(db, text_id, text_update)
    if not text:
        raise HTTPException(status_code=404, detail="Текст не найден")
    return text

# Scenario endpoints
@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios(db: Session = Depends(get_db)):
    """Получение всех сценариев"""
    return await UnifiedScenarioService.get_scenarios(db)

@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Создание нового сценария"""
    return await UnifiedScenarioService.create_scenario(db, scenario)

@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario_update: ScenarioUpdate,
    db: Session = Depends(get_db)
):
    """Обновление сценария"""
    scenario = await UnifiedScenarioService.update_scenario(db, scenario_id, scenario_update)
    if not scenario:
        raise HTTPException(status_code=404, detail="Сценарий не найден")
    return scenario

# КРИТИЧНО: Сохраняем эндпоинты для конструктора сценариев
@router.get("/bot-flow/scenarios")
async def get_bot_flow_scenarios(db: Session = Depends(get_db)):
    """Получение сценариев для Flow Designer (обратная совместимость)"""
    scenarios = await UnifiedScenarioService.get_scenarios(db)
    return scenarios

@router.get("/bot-flow/texts")
async def get_bot_flow_texts(db: Session = Depends(get_db)):
    """Получение текстов для Flow Designer (обратная совместимость)"""
    texts = await UnifiedTextService.get_texts(db)
    return texts
```

### Этап 3: Миграция Bot API (Неделя 3)

#### 3.1 Обновление bot/main.py
```python
# bot/main.py - обновленная версия
from fastapi import FastAPI, Request
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from common.api.unified import router as unified_router
from common.database import init_db, close_db
from common.config import settings

# ... существующий код ...

# Подключаем единый API роутер
app.include_router(unified_router)

# ... остальной код без изменений ...
```

#### 3.2 Удаление дублированного кода
```bash
# Удаление старого API файла
rm bot/api.py

# Обновление импортов в bot/handlers/
# Замена импортов на единые сервисы
```

#### 3.3 Сохранение критических компонентов
**ВАЖНО**: Следующие файлы НЕ ТРОГАТЬ:
- `bot/handlers/scenarios.py` - обработчик сценариев
- `bot/handlers/main_handler.py` - главный обработчик
- `common/services_package/` - все сервисы пакета
- `bot/handlers/checks.py` - обработчик проверок
- `bot/handlers/base.py` - базовые классы

#### 3.4 Обновление импортов в обработчиках
```python
# bot/handlers/main_handler.py - обновление импортов
from common.services.unified import UnifiedTextService
# ... остальные импорты без изменений ...

class MainHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        # НЕ ИЗМЕНЯТЬ: эти компоненты критически важны
        self.scenario_handler = ScenarioHandler()
        self.check_handler = CheckHandler()
```

### Этап 4: Миграция Admin API (Неделя 4)

#### 4.1 Обновление admin_panel_new/app/main.py
```python
# admin_panel_new/app/main.py - обновленная версия
from fastapi import FastAPI
from common.api.unified import router as unified_router

app = FastAPI(title="CheckYourCrypto Admin API - Unified Version")

# Подключаем единый API роутер
app.include_router(unified_router)

# Оставляем только специфичные для админки эндпоинты
@app.get("/api/admin/dashboard")
async def admin_dashboard():
    # Специфичная логика админки
    pass

# КРИТИЧНО: Сохраняем эндпоинты для конструктора
@app.get("/api/bot-flow/scenarios")
async def get_bot_flow_scenarios():
    """Получение сценариев для Flow Designer"""
    # Делегируем единому сервису
    pass

@app.get("/api/bot-flow/texts")
async def get_bot_flow_texts():
    """Получение текстов для Flow Designer"""
    # Делегируем единому сервису
    pass
```

#### 4.2 Удаление дублированных эндпоинтов
```bash
# Удаление дублированных эндпоинтов из main.py
# Оставление только специфичных для админки функций
```

#### 4.3 Обновление frontend
```javascript
// admin_panel_new/frontend/src/services/api.js
// Обновление URL эндпоинтов на единые

const API_BASE = '/api/unified';

export const textAPI = {
    getTexts: (category, language) => 
        fetch(`${API_BASE}/texts?category=${category}&language=${language}`),
    createText: (textData) => 
        fetch(`${API_BASE}/texts`, { method: 'POST', body: JSON.stringify(textData) }),
    updateText: (id, textData) => 
        fetch(`${API_BASE}/texts/${id}`, { method: 'PUT', body: JSON.stringify(textData) })
};

export const scenarioAPI = {
    getScenarios: () => 
        fetch(`${API_BASE}/scenarios`),
    createScenario: (scenarioData) => 
        fetch(`${API_BASE}/scenarios`, { method: 'POST', body: JSON.stringify(scenarioData) }),
    updateScenario: (id, scenarioData) => 
        fetch(`${API_BASE}/scenarios/${id}`, { method: 'PUT', body: JSON.stringify(scenarioData) })
};

// КРИТИЧНО: Сохраняем обратную совместимость для конструктора
export const botFlowAPI = {
    getScenarios: () => 
        fetch(`${API_BASE}/bot-flow/scenarios`),
    getTexts: () => 
        fetch(`${API_BASE}/bot-flow/texts`)
};
```

### Этап 5: Тестирование (Неделя 5)

#### 5.1 Unit тесты
```python
# tests/unit/test_unified_services.py
import pytest
from common.services.unified import UnifiedTextService, UnifiedScenarioService

class TestUnifiedTextService:
    async def test_get_texts(self):
        # Тестирование получения текстов
        pass
    
    async def test_create_text(self):
        # Тестирование создания текста
        pass
    
    async def test_update_text(self):
        # Тестирование обновления текста
        pass

class TestUnifiedScenarioService:
    async def test_get_scenarios(self):
        # Тестирование получения сценариев
        pass
    
    async def test_create_scenario(self):
        # Тестирование создания сценария
        pass
```

#### 5.2 Integration тесты
```python
# tests/integration/test_unified_api.py
import pytest
from fastapi.testclient import TestClient
from bot.main import app

client = TestClient(app)

class TestUnifiedAPI:
    def test_get_texts(self):
        response = client.get("/api/unified/texts")
        assert response.status_code == 200
    
    def test_create_text(self):
        text_data = {"category": "test", "content": "test content"}
        response = client.post("/api/unified/texts", json=text_data)
        assert response.status_code == 200
    
    def test_get_scenarios(self):
        response = client.get("/api/unified/scenarios")
        assert response.status_code == 200
    
    # КРИТИЧНО: Тестирование обратной совместимости
    def test_bot_flow_scenarios_backward_compatibility(self):
        response = client.get("/api/unified/bot-flow/scenarios")
        assert response.status_code == 200
    
    def test_bot_flow_texts_backward_compatibility(self):
        response = client.get("/api/unified/bot-flow/texts")
        assert response.status_code == 200
```

#### 5.3 End-to-end тесты
```python
# tests/e2e/test_bot_admin_integration.py
import pytest
import requests

class TestBotAdminIntegration:
    def test_text_sync_between_bot_and_admin(self):
        # Тест синхронизации текстов между ботом и админкой
        pass
    
    def test_scenario_sync_between_bot_and_admin(self):
        # Тест синхронизации сценариев между ботом и админкой
        pass
    
    # КРИТИЧНО: Тестирование работы конструктора
    def test_scenario_constructor_integration(self):
        # Тест интеграции с конструктором сценариев
        pass
    
    def test_placeholder_service_integration(self):
        # Тест работы системы плейсхолдеров
        pass
```

### Этап 6: Деплой и мониторинг (Неделя 6)

#### 6.1 Деплой на staging
```bash
# Деплой на staging окружение
git push heroku feature/unified-api:main --app checkyourcrypto-staging

# Тестирование на staging
curl https://checkyourcrypto-staging.herokuapp.com/api/unified/texts
curl https://checkyourcrypto-staging.herokuapp.com/api/unified/scenarios
curl https://checkyourcrypto-staging.herokuapp.com/api/unified/bot-flow/scenarios
```

#### 6.2 Мониторинг и метрики
```python
# common/monitoring/unified_metrics.py
from prometheus_client import Counter, Histogram
import time

# Метрики для единого API
unified_api_requests = Counter('unified_api_requests_total', 'Total unified API requests', ['endpoint', 'method'])
unified_api_duration = Histogram('unified_api_duration_seconds', 'Unified API request duration')

def track_unified_api_request(endpoint: str, method: str, duration: float):
    unified_api_requests.labels(endpoint=endpoint, method=method).inc()
    unified_api_duration.observe(duration)
```

#### 6.3 Деплой на продакшн
```bash
# Создание релиза
git tag v2.0.0-unified-api
git push origin v2.0.0-unified-api

# Деплой на продакшн
git push heroku feature/unified-api:main --app checkyourcrypto-bot

# Мониторинг после деплоя
heroku logs --tail --app checkyourcrypto-bot
```

## 🔧 Инструменты и утилиты

### Скрипт миграции данных
```python
# scripts/migrate_to_unified.py
import asyncio
from sqlalchemy.orm import sessionmaker
from common.database import engine
from common.models.unified import UnifiedBotText, UnifiedScenario
from common.models import BotText, Scenario

async def migrate_data():
    """Миграция данных из старых моделей в новые"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with SessionLocal() as session:
        # Миграция текстов
        old_texts = session.query(BotText).all()
        for old_text in old_texts:
            new_text = UnifiedBotText(
                category=old_text.category,
                language=old_text.language,
                content=old_text.content,
                version=old_text.version,
                created_at=old_text.created_at,
                updated_at=old_text.updated_at
            )
            session.add(new_text)
        
        # Миграция сценариев
        old_scenarios = session.query(Scenario).all()
        for old_scenario in old_scenarios:
            new_scenario = UnifiedScenario(
                name=old_scenario.name,
                description=old_scenario.description,
                is_active=old_scenario.is_active,
                stages=old_scenario.stages,
                created_at=old_scenario.created_at,
                updated_at=old_scenario.updated_at
            )
            session.add(new_scenario)
        
        session.commit()

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

### Скрипт отката
```python
# scripts/rollback_unified.py
import asyncio
from sqlalchemy.orm import sessionmaker
from common.database import engine
from common.models.unified import UnifiedBotText, UnifiedScenario

async def rollback_migration():
    """Откат миграции к предыдущей версии"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with SessionLocal() as session:
        # Удаление новых данных
        session.query(UnifiedBotText).delete()
        session.query(UnifiedScenario).delete()
        session.commit()
        
        # Восстановление из бэкапа
        # ... логика восстановления из бэкапа

if __name__ == "__main__":
    asyncio.run(rollback_migration())
```

### Скрипт проверки совместимости
```python
# scripts/check_compatibility.py
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)

async def check_bot_constructor_compatibility():
    """Проверка совместимости с конструктором сценариев"""
    try:
        async with aiohttp.ClientSession() as session:
            # Проверяем эндпоинты конструктора
            endpoints = [
                "/api/unified/bot-flow/scenarios",
                "/api/unified/bot-flow/texts",
                "/api/unified/texts",
                "/api/unified/scenarios"
            ]
            
            for endpoint in endpoints:
                async with session.get(f"https://checkyourcrypto-staging.herokuapp.com{endpoint}") as response:
                    if response.status == 200:
                        logger.info(f"✅ {endpoint} - OK")
                    else:
                        logger.error(f"❌ {endpoint} - FAILED ({response.status})")
                        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки совместимости: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot_constructor_compatibility())
```

## 📊 Метрики успеха

### Количественные показатели
- [ ] Сокращение кода на 40-50%
- [ ] Сокращение файлов на 30-40%
- [ ] Снижение потребления памяти на 25-30%
- [ ] Ускорение времени ответа API на 20-30%

### Качественные показатели
- [ ] Упрощение поддержки кода
- [ ] Улучшение надежности системы
- [ ] Ускорение разработки новых функций
- [ ] Упрощение тестирования
- [ ] **КРИТИЧНО**: Сохранение работы конструктора сценариев

## 🚨 План действий в случае проблем

### Критические проблемы
1. **Потеря данных**: Восстановление из бэкапа
2. **Недоступность API**: Откат к предыдущей версии
3. **Конфликты в коде**: Разрешение через code review
4. **Нарушение работы конструктора**: Немедленный откат

### Процедура отката
```bash
# Быстрый откат
git checkout main
git push heroku main:main --app checkyourcrypto-bot --force

# Восстановление данных
python scripts/rollback_unified.py

# Проверка совместимости
python scripts/check_compatibility.py
```

## 📝 Чек-лист завершения

### Подготовка
- [ ] Создан бэкап системы
- [ ] Настроено staging окружение
- [ ] Создана ветка для разработки

### Разработка
- [ ] Созданы единые модели данных
- [ ] Созданы единые сервисы
- [ ] Создан единый API роутер
- [ ] Обновлен Bot API
- [ ] Обновлен Admin API
- [ ] **КРИТИЧНО**: Сохранена обратная совместимость с конструктором

### Тестирование
- [ ] Пройдены unit тесты
- [ ] Пройдены integration тесты
- [ ] Пройдены end-to-end тесты
- [ ] Проведено тестирование на staging
- [ ] **КРИТИЧНО**: Проверена работа конструктора сценариев

### Деплой
- [ ] Деплой на staging
- [ ] Мониторинг производительности
- [ ] Деплой на продакшн
- [ ] Финальное тестирование
- [ ] **КРИТИЧНО**: Проверка работы бота с конструктором

### Документация
- [ ] Обновлена документация API
- [ ] Обновлены README файлы
- [ ] Созданы инструкции по миграции
- [ ] Обновлены схемы архитектуры
- [ ] **КРИТИЧНО**: Документированы изменения для конструктора
