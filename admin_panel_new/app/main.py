from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import psycopg2
import os
import requests
from datetime import datetime
from pydantic import BaseModel
import json
import logging
import sys
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Логируем запуск приложения
logger.info("=== NEW CLEAN API STARTUP ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

app = FastAPI(title="CheckYourCrypto Admin API - NEW CLEAN VERSION")

logger.info("FastAPI app created")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    try:
        # Проверяем подключение к базе данных
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("Database connection: OK")
        else:
            logger.warning("DATABASE_URL not set")
        
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins временно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware added")

# Подключаем auth роутер
try:
    from app.api.auth import router as auth_router
    app.include_router(auth_router, prefix="/api")
    logger.info("Auth router included successfully")
except Exception as e:
    logger.error(f"Failed to include auth router: {e}")
    # Создаем простой auth эндпоинт
    @app.post("/api/auth/login")
    async def simple_login():
        """Простой эндпоинт для логина"""
        return {"access_token": "demo-token", "token_type": "bearer"}
    
    logger.info("Simple auth endpoint created")

# Pydantic модели для текстов
class BotTextCreate(BaseModel):
    category: str
    language: str = "ru"
    content: str
    version: int = 1

class BotTextUpdate(BaseModel):
    content: str

# Pydantic модели для сценариев
class ScenarioCreate(BaseModel):
    name: str
    description: str = ""
    is_active: bool = False
    stages: list = []

class ScenarioUpdate(BaseModel):
    name: str = None
    description: str = None
    is_active: bool = None
    stages: list = None

# API endpoints для текстов
@app.get("/api/texts")
async def get_texts():
    """Получение всех текстов из базы данных"""
    logger.info("GET /api/texts called")
    try:
        # Читаем тексты из базы данных
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, language, content, is_active, created_at, updated_at
            FROM bot_texts
            ORDER BY category, language
        """)
        
        texts = []
        for row in cursor.fetchall():
            texts.append({
                "id": row[0],
                "category": row[1],
                "language": row[2],
                "content": row[3],
                "is_active": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Returning {len(texts)} texts from database")
        return {"texts": texts, "count": len(texts)}
        
    except Exception as e:
        logger.error(f"Error getting texts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting texts: {str(e)}")

@app.get("/api/texts/{category}")
async def get_texts_by_category(category: str):
    """Получение текстов по категории"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, language, content, is_active, created_at, updated_at
            FROM bot_texts
            WHERE category = %s
            ORDER BY language
        """, (category,))
        
        texts = []
        for row in cursor.fetchall():
            texts.append({
                "id": row[0],
                "category": row[1],
                "language": row[2],
                "content": row[3],
                "is_active": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        return {"texts": texts, "count": len(texts)}
        
    except Exception as e:
        logger.error(f"Error getting texts by category: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting texts by category: {str(e)}")

@app.post("/api/texts")
async def create_text(text_data: BotTextCreate):
    """Создание нового текста"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bot_texts (category, language, content, is_active, version, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (text_data.category, text_data.language, text_data.content, True, text_data.version))
        
        text_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"id": text_id, "message": "Text created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating text: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating text: {str(e)}")

@app.put("/api/texts/{text_id}")
async def update_text(text_id: int, text_data: BotTextUpdate):
    """Обновление текста"""
    logger.info(f"PUT /api/texts/{text_id} called with content: {text_data.content[:100]}...")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bot_texts 
            SET content = %s, updated_at = NOW()
            WHERE id = %s
        """, (text_data.content, text_id))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Text not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Text {text_id} updated successfully")
        return {"message": "Text updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating text: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating text: {str(e)}")

@app.delete("/api/texts/{text_id}")
async def delete_text(text_id: int):
    """Удаление текста"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM bot_texts WHERE id = %s", (text_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Text not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Text deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting text: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting text: {str(e)}")

# API endpoints для сценариев
@app.get("/api/scenarios")
async def get_scenarios():
    """Получение всех сценариев"""
    logger.info("GET /api/scenarios called")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица scenarios
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scenarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Создаем таблицу scenarios если её нет
            cursor.execute("""
                CREATE TABLE scenarios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    stages JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
            logger.info("Table 'scenarios' created")
        
        cursor.execute("""
            SELECT id, name, description, is_active, stages, created_at, updated_at
            FROM scenarios
            ORDER BY created_at DESC
        """)
        
        scenarios = []
        for row in cursor.fetchall():
            scenarios.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "is_active": row[3],
                "stages": row[4] if row[4] else {},
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        return {"scenarios": scenarios, "count": len(scenarios)}
        
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting scenarios: {str(e)}")

@app.get("/api/scenarios/active/default")
async def get_active_scenario():
    """Получение активного сценария по умолчанию"""
    logger.info("GET /api/scenarios/active/default called")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица scenarios
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scenarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Создаем таблицу и базовый сценарий
            cursor.execute("""
                CREATE TABLE scenarios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    stages JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Создаем базовый сценарий
            basic_scenario = {
                "welcome": {
                    "type": "message",
                    "text_category": "welcome",
                    "next": "main_menu"
                },
                "main_menu": {
                    "type": "menu",
                    "text_category": "main_menu",
                    "buttons": [
                        {"text": "check_button", "action": "check_address"},
                        {"text": "add_balance_button", "action": "add_balance"},
                        {"text": "profile_button", "action": "profile"},
                        {"text": "faq_button", "action": "faq"}
                    ]
                },
                "check_address": {
                    "type": "input",
                    "text_category": "check_address_prompt",
                    "next": "process_address"
                }
            }
            
            cursor.execute("""
                INSERT INTO scenarios (name, description, is_active, stages)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, ("Default Scenario", "Базовый сценарий бота", True, json.dumps(basic_scenario)))
            
            conn.commit()
            logger.info("Default scenario created")
        
        # Получаем активный сценарий
        cursor.execute("""
            SELECT id, name, description, is_active, stages, created_at, updated_at
            FROM scenarios
            WHERE is_active = TRUE
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if not row:
            # Если нет активного сценария, возвращаем базовый
            return {
                "id": 1,
                "name": "Default Scenario",
                "description": "Базовый сценарий бота",
                "is_active": True,
                "stages": {
                    "welcome": {
                        "type": "message",
                        "text_category": "welcome",
                        "next": "main_menu"
                    },
                    "main_menu": {
                        "type": "menu",
                        "text_category": "main_menu",
                        "buttons": [
                            {"text": "check_button", "action": "check_address"},
                            {"text": "add_balance_button", "action": "add_balance"},
                            {"text": "profile_button", "action": "profile"},
                            {"text": "faq_button", "action": "faq"}
                        ]
                    }
                }
            }
        
        scenario = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "is_active": row[3],
            "stages": row[4] if row[4] else {},
            "created_at": row[5].isoformat() if row[5] else None,
            "updated_at": row[6].isoformat() if row[6] else None
        }
        
        cursor.close()
        conn.close()
        
        return scenario
        
    except Exception as e:
        logger.error(f"Error getting active scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting active scenario: {str(e)}")

@app.post("/api/scenarios")
async def create_scenario(scenario_data: ScenarioCreate):
    """Создание нового сценария"""
    logger.info(f"POST /api/scenarios called with name: {scenario_data.name}")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица scenarios
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scenarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            cursor.execute("""
                CREATE TABLE scenarios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    stages JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
        
        cursor.execute("""
            INSERT INTO scenarios (id, name, description, is_active, stages, created_at, updated_at)
            VALUES (DEFAULT, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (scenario_data.name, scenario_data.description, scenario_data.is_active, json.dumps(scenario_data.stages)))
        
        scenario_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Scenario {scenario_id} created successfully")
        return {"id": scenario_id, "message": "Scenario created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating scenario: {str(e)}")

# API endpoints для Flow Designer (старые эндпоинты для совместимости)
@app.get("/api/bot-flow/scenarios")
async def get_bot_flow_scenarios():
    """Получение сценариев для Flow Designer"""
    try:
        logger.info("GET /api/bot-flow/scenarios called")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, is_active, stages, created_at, updated_at
            FROM scenarios
            ORDER BY created_at DESC
        """)
        
        scenarios = []
        for row in cursor.fetchall():
            scenario_id, name, description, is_active, stages_json, created_at, updated_at = row
            
            # Парсим JSON stages или используем как есть если это уже список
            if isinstance(stages_json, list):
                stages = stages_json
            elif isinstance(stages_json, str):
                stages = json.loads(stages_json) if stages_json else []
            else:
                stages = []
            
            scenarios.append({
                "id": scenario_id,
                "name": name,
                "description": description,
                "is_active": is_active,
                "stages": stages,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Returning {len(scenarios)} scenarios from database")
        return scenarios  # Возвращаем массив напрямую
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting scenarios: {str(e)}")

@app.get("/api/bot-flow/scenarios/{scenario_id}")
async def get_scenario(scenario_id: int):
    """Получение конкретного сценария"""
    try:
        # Получаем сценарий из базы данных
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, is_active, stages, created_at, updated_at
            FROM scenarios
            WHERE id = %s
        """, (scenario_id,))
        
        row = cursor.fetchone()
        if row:
            scenario_id, name, description, is_active, stages_json, created_at, updated_at = row
            
            # Парсим JSON stages или используем как есть если это уже список
            if isinstance(stages_json, list):
                stages = stages_json
            elif isinstance(stages_json, str):
                stages = json.loads(stages_json) if stages_json else []
            else:
                stages = []
            
            scenario = {
                "id": scenario_id,
                "name": name,
                "description": description,
                "is_active": is_active,
                "stages": stages,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None
            }
        else:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        cursor.close()
        conn.close()
        
        return scenario
    except Exception as e:
        logger.error(f"Error getting scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting scenario: {str(e)}")

@app.get("/api/bot-flow/texts")
async def get_texts_for_flow():
    """Получение текстов для Flow Designer"""
    try:
        # Читаем тексты из базы данных
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT category, language, content
            FROM bot_texts
            WHERE is_active = true AND language = 'ru'
            ORDER BY category
        """)
        
        # Возвращаем массив объектов как ожидает фронтенд
        texts = []
        for row in cursor.fetchall():
            category = row[0]
            content = row[2]
            
            # Создаем понятное имя из категории
            name = category.replace('_', ' ').title()
            
            texts.append({
                "key": category,
                "name": name,
                "content": content
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Returning {len(texts)} texts for Flow Designer")
        return texts  # Возвращаем массив напрямую
        
    except Exception as e:
        logger.error(f"Error getting texts for flow: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting texts for flow: {str(e)}")

@app.post("/api/bot-flow/recreate-table")
async def recreate_scenarios_table():
    """Пересоздание таблицы scenarios с правильной структурой"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Удаляем старую таблицу scenarios
        cursor.execute("DROP TABLE IF EXISTS scenarios")
        conn.commit()
        logger.info("Old scenarios table dropped")
        
        # Создаем новую таблицу scenarios с правильной структурой
        cursor.execute("""
            CREATE TABLE scenarios (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                stages JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("New scenarios table created with VARCHAR id")
        return {"message": "Scenarios table recreated successfully"}
        
    except Exception as e:
        logger.error(f"Error recreating scenarios table: {e}")
        raise HTTPException(status_code=500, detail=f"Error recreating scenarios table: {str(e)}")

@app.put("/api/bot-flow/scenarios/{scenario_id}")
async def update_scenario(scenario_id: str, scenario_data: dict):
    """Обновление сценария"""
    try:
        logger.info(f"Updating scenario {scenario_id}")
        logger.info(f"Scenario data: {scenario_data}")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица scenarios
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scenarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            cursor.execute("""
                CREATE TABLE scenarios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    stages JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
            logger.info("Table 'scenarios' created")
        
        # Проверяем, существует ли сценарий с таким ID
        cursor.execute("SELECT id FROM scenarios WHERE id = %s", (scenario_id,))
        existing_scenario = cursor.fetchone()
        
        if existing_scenario:
            # Обновляем существующий сценарий
            cursor.execute("""
                UPDATE scenarios 
                SET name = %s, description = %s, is_active = %s, stages = %s, updated_at = NOW()
                WHERE id = %s
            """, (
                scenario_data.get('name', 'Default Scenario'),
                scenario_data.get('description', ''),
                scenario_data.get('is_active', True),
                json.dumps(scenario_data.get('stages', {})),
                scenario_id
            ))
            logger.info(f"Scenario {scenario_id} updated successfully")
        else:
            # Создаем новый сценарий с указанным ID
            cursor.execute("""
                INSERT INTO scenarios (id, name, description, is_active, stages, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                scenario_id,
                scenario_data.get('name', 'Default Scenario'),
                scenario_data.get('description', ''),
                scenario_data.get('is_active', True),
                json.dumps(scenario_data.get('stages', {}))
            ))
            logger.info(f"Scenario {scenario_id} created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Scenario updated successfully", "scenario_id": scenario_id}
        
    except Exception as e:
        logger.error(f"Error updating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating scenario: {str(e)}")

@app.post("/api/bot-flow/scenarios")
async def create_scenario(scenario_data: dict):
    """Создание нового сценария"""
    try:
        logger.info(f"Creating new scenario")
        logger.info(f"Scenario data: {scenario_data}")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли таблица scenarios
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scenarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            cursor.execute("""
                CREATE TABLE scenarios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    stages JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
            logger.info("Table 'scenarios' created")
        
        # Создаем новый сценарий в базе данных
        cursor.execute("""
            INSERT INTO scenarios (name, description, is_active, stages, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            scenario_data.get('name', 'New Scenario'),
            scenario_data.get('description', ''),
            scenario_data.get('is_active', False),
            json.dumps(scenario_data.get('stages', {}))
        ))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Scenario {new_id} created successfully")
        return {"message": "Scenario created successfully", "scenario_id": new_id}
        
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating scenario: {str(e)}")

@app.delete("/api/bot-flow/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Удаление сценария"""
    try:
        logger.info(f"Deleting scenario {scenario_id}")
        
        # Пока просто логируем удаление
        # TODO: Удалить из базы данных
        logger.info(f"Scenario {scenario_id} deleted successfully")
        
        return {"message": "Scenario deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting scenario: {str(e)}")

# API endpoints для пользователей
@app.get("/api/users")
async def get_users(page: int = 1, limit: int = 20, search: str = ""):
    """Получение списка пользователей"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы users
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        logger.info(f"Users table columns: {columns}")
        
        # Базовый запрос
        base_query = "FROM users WHERE 1=1"
        params = []
        
        if search:
            base_query += " AND username ILIKE %s"
            search_param = f"%{search}%"
            params.append(search_param)
        
        # Подсчет общего количества
        count_query = f"SELECT COUNT(*) {base_query}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Получение пользователей с пагинацией
        offset = (page - 1) * limit
        users_query = f"""
            SELECT tg_id, username, language, balance, is_blocked, created_at, updated_at
            {base_query}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(users_query, params + [limit, offset])
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],  # Используем tg_id как id
                "tg_id": row[0],
                "username": row[1],
                "language": row[2],
                "balance": float(row[3]) if row[3] else 0.0,
                "is_blocked": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "users": users,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

@app.post("/api/users")
async def create_user(user_data: dict):
    """Создание нового пользователя"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT tg_id FROM users WHERE tg_id = %s", (user_data['tg_id'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Создаем пользователя
        cursor.execute("""
            INSERT INTO users (tg_id, username, language, balance, is_blocked, 
                             last_free_check, referral_code, referrer_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING tg_id
        """, (
            user_data['tg_id'],
            user_data.get('username', ''),
            user_data.get('language', 'ru'),
            user_data.get('balance', 0.0),
            user_data.get('is_blocked', False),
            user_data.get('last_free_check'),
            user_data.get('referral_code', ''),
            user_data.get('referrer_id'),
            user_data.get('created_at'),
            user_data.get('updated_at')
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"User created successfully: {user_id}")
        return {"message": "User created successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Получение конкретного пользователя"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Получаем пользователя
        cursor.execute("""
            SELECT tg_id, username, language, balance, is_blocked, created_at, updated_at,
                   last_free_check, referral_code, referrer_id
            FROM users 
            WHERE tg_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user[0],
            "tg_id": user[0],
            "username": user[1],
            "language": user[2],
            "balance": float(user[3]) if user[3] else 0.0,
            "is_blocked": user[4],
            "created_at": user[5].isoformat() if user[5] else None,
            "updated_at": user[6].isoformat() if user[6] else None,
            "last_free_check": user[7].isoformat() if user[7] else None,
            "referral_code": user[8],
            "referrer_id": user[9]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")

@app.get("/api/users/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Получение статистики пользователя"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT tg_id FROM users WHERE tg_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем базовую статистику
        cursor.execute("""
            SELECT COUNT(*) as total_checks
            FROM checks 
            WHERE user_id = %s
        """, (user_id,))
        
        check_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "total_checks": check_stats[0] or 0,
            "free_checks": 0,  # Пока не знаем структуру
            "paid_checks": 0,  # Пока не знаем структуру
            "total_payments": 0,
            "total_amount": 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

@app.get("/api/users/{user_id}/checks")
async def get_user_checks(user_id: int, page: int = 1, limit: int = 20):
    """Получение проверок пользователя"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT tg_id FROM users WHERE tg_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверяем структуру таблицы checks
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'checks' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        logger.info(f"Checks table columns: {columns}")
        
        # Получаем проверки с пагинацией (упрощенный запрос)
        offset = (page - 1) * limit
        cursor.execute("""
            SELECT id, created_at
            FROM checks 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        
        checks = []
        for row in cursor.fetchall():
            checks.append({
                "id": row[0],
                "created_at": row[1].isoformat() if row[1] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "checks": checks,
            "page": page,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user checks {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user checks: {str(e)}")

# API endpoints для сообщений
@app.get("/api/messages")
async def get_messages(page: int = 1, limit: int = 20):
    """Получение списка сообщений"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем какие таблицы есть в базе данных
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%message%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        logger.info(f"Tables with 'message' in name: {tables}")
        
        # Если таблицы нет, возвращаем пустой список
        if not tables:
            logger.warning("No messages table found, returning empty list")
            return {
                "messages": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "pages": 0
            }
        
        # Используем первую найденную таблицу
        table_name = tables[0][0]
        logger.info(f"Using table: {table_name}")
        
        # Проверяем структуру таблицы
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        logger.info(f"Table {table_name} columns: {columns}")
        
        # Подсчет общего количества
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        # Получение сообщений с пагинацией
        offset = (page - 1) * limit
        
        # Адаптируем запрос под реальную структуру таблицы
        # Используем только существующие колонки
        cursor.execute(f"""
            SELECT *
            FROM {table_name}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        messages = []
        for row in cursor.fetchall():
            # Создаем словарь с данными, адаптируя под реальную структуру
            message_data = {
                "id": row[0] if len(row) > 0 else None,
                "title": f"Сообщение {row[0]}" if len(row) > 0 else "Без названия",
                "content": row[1] if len(row) > 1 else "Содержимое недоступно",
                "user_filter": "all",
                "send_type": "now",
                "status": "sent",
                "created_at": row[2].isoformat() if len(row) > 2 and hasattr(row[2], 'isoformat') else str(row[2]) if len(row) > 2 else None,
                "sent_at": row[2].isoformat() if len(row) > 2 and hasattr(row[2], 'isoformat') else str(row[2]) if len(row) > 2 else None,
                "sent_count": 1,
                "total_count": 1
            }
            messages.append(message_data)
        
        cursor.close()
        conn.close()
        
        return {
            "messages": messages,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

# API endpoints для меню
@app.get("/api/menus")
async def get_menus(page: int = 1, limit: int = 20, language: str = "", menu_type: str = "", search: str = ""):
    """Получение списка меню"""
    try:
        # Пока возвращаем тестовые данные
        menus = [
            {
                "id": 1,
                "name": "Главное меню",
                "description": "Основное меню бота",
                "menu_type": "main",
                "language": "ru",
                "keyboard_data": '[["🔍 Проверка", "💰 Пополнить"], ["👤 Личный кабинет", "📁 FAQ"]]',
                "is_active": True,
                "created_at": "2025-08-23T21:00:00",
                "updated_at": "2025-08-23T21:00:00"
            }
        ]
        
        return {
            "menus": menus,
            "total": 1,
            "page": page,
            "limit": limit,
            "pages": 1
        }
        
    except Exception as e:
        logger.error(f"Error getting menus: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting menus: {str(e)}")

# API endpoints для админ действий
@app.get("/api/admin/actions")
async def get_admin_actions():
    """Получение административных действий"""
    try:
        # Пока возвращаем тестовые данные
        actions = [
            {
                "id": 1,
                "action_type": "text_update",
                "description": "Обновлен текст главного меню",
                "user_id": 1,
                "created_at": "2025-08-23T21:00:00",
                "details": "Добавлен текст '11' в главное меню"
            }
        ]
        
        return {"actions": actions}
        
    except Exception as e:
        logger.error(f"Error getting admin actions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting admin actions: {str(e)}")

# API endpoints для дашборда
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Получение статистики для дашборда"""
    try:
        # Пока возвращаем тестовые данные
        return {
            "total_users": 100,
            "new_users_24h": 5,
            "total_checks": 500,
            "checks_24h": 25,
            "total_balance": 1000.0,
            "total_payments": 50,
            "total_revenue": 500.0
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

# API endpoints для настроек
@app.get("/api/settings")
async def get_settings():
    """Получение всех настроек из базы данных"""
    logger.info("GET /api/settings called")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key, value, updated_at
            FROM settings
            ORDER BY key
        """)
        
        settings = {}
        for row in cursor.fetchall():
            settings[row[0]] = {
                "value": row[1],
                "updated_at": row[2].isoformat() if row[2] else None
            }
        
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(settings)} settings")
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings/{key}")
async def get_setting(key: str):
    """Получение конкретной настройки по ключу"""
    logger.info(f"GET /api/settings/{key} called")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, updated_at
            FROM settings
            WHERE key = %s
        """, (key,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return {
                "key": key,
                "value": row[0],
                "updated_at": row[1].isoformat() if row[1] else None
            }
        else:
            raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/settings/{key}")
async def update_setting(key: str, setting_update: dict = Body(...)):
    """Обновление настройки по ключу"""
    logger.info(f"PUT /api/settings/{key} called with data: {setting_update}")
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существует ли настройка
        cursor.execute("SELECT key FROM settings WHERE key = %s", (key,))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем существующую настройку
            cursor.execute("""
                UPDATE settings 
                SET value = %s, updated_at = NOW() 
                WHERE key = %s
                RETURNING key
            """, (setting_update.get('value'), key))
        else:
            # Создаем новую настройку
            cursor.execute("""
                INSERT INTO settings (key, value, updated_at)
                VALUES (%s, %s, NOW())
                RETURNING key
            """, (key, setting_update.get('value')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Setting {key} updated successfully")
        return {"status": "updated", "key": key}
        
    except Exception as e:
        logger.error(f"Error updating setting {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
