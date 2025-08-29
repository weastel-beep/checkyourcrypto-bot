from fastapi import FastAPI, HTTPException, Body, Request
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
import uuid

# Простая настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Логируем запуск приложения
logger.info("=== ADMIN API STARTUP ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

app = FastAPI(title="CheckYourCrypto Admin API")

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

@app.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    logger.info("Test endpoint called")
    return {"message": "Test endpoint works!", "timestamp": datetime.now().isoformat()}

@app.get("/api/test")
async def api_test_endpoint():
    """Тестовый API эндпоинт"""
    logger.info("API test endpoint called")
    return {"message": "API test endpoint works!", "timestamp": datetime.now().isoformat()}

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware added")

# Создаем простой auth эндпоинт
logger.info("Creating simple auth endpoint...")

@app.post("/api/auth/login")
async def simple_login():
    """Простой эндпоинт для логина"""
    logger.info("Simple login endpoint called")
    return {"access_token": "demo-token", "token_type": "bearer"}

logger.info("Simple auth endpoint created successfully")
logger.info("Auth setup completed")

# API endpoints для Admin Panel
@app.get("/api/users")
async def get_users():
    """Получение списка пользователей"""
    try:
        logger.info("GET /api/users called")
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Получаем пользователей из базы данных
        cursor.execute("""
            SELECT tg_id, username, language, balance, referral_code, is_blocked, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],  # tg_id как id
                "tg_id": row[0],
                "username": row[1],
                "language": row[2],
                "balance": float(row[3]) if row[3] else 0.0,
                "referral_code": row[4],
                "is_blocked": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(users)} users")
        return {"users": users, "total": len(users)}
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

@app.get("/api/messages")
async def get_messages():
    """Получение сообщений"""
    try:
        logger.info("GET /api/messages called")
        return {"messages": [], "total": 0}
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Получение статистики дашборда"""
    try:
        logger.info("GET /api/dashboard/stats called")
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Получаем статистику
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '24 hours'")
        new_users_24h = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '7 days'")
        new_users_7d = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "total_users": total_users,
            "new_users_24h": new_users_24h,
            "new_users_7d": new_users_7d,
            "active_users": 0,
            "total_checks": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

@app.get("/api/settings/paid_check_price")
async def get_paid_check_price():
    """Получение цены платной проверки"""
    try:
        logger.info("GET /api/settings/paid_check_price called")
        return {"paid_check_price": 1.0}
    except Exception as e:
        logger.error(f"Error getting paid check price: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting paid check price: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user():
    """Получение текущего пользователя"""
    try:
        logger.info("GET /api/auth/me called")
        return {
            "id": 1,
            "username": "admin",
            "email": "admin@checkyourcrypto.com",
            "role": "admin"
        }
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting current user: {str(e)}")

@app.get("/api/dashboard/charts/user-activity")
async def get_user_activity():
    """Получение активности пользователей"""
    try:
        logger.info("GET /api/dashboard/charts/user-activity called")
        return {"data": [], "labels": []}
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user activity: {str(e)}")

# API endpoints для Flow Designer
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
        return scenarios
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting scenarios: {str(e)}")

@app.get("/api/bot-flow/texts")
async def get_texts_for_flow():
    """Получение текстов для Flow Designer"""
    try:
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
        
        texts = []
        for row in cursor.fetchall():
            category = row[0]
            content = row[2]
            
            name = category.replace('_', ' ').title()
            
            texts.append({
                "key": category,
                "name": name,
                "content": content
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Returning {len(texts)} texts for Flow Designer")
        return texts
        
    except Exception as e:
        logger.error(f"Error getting texts for flow: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting texts for flow: {str(e)}")

@app.get("/api/texts")
async def get_texts_for_bot():
    """Получение текстов для бота (старый формат)"""
    try:
        logger.info("GET /api/texts called")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, language, content, version, created_at, updated_at
            FROM bot_texts
            WHERE is_active = true
            ORDER BY category, language
        """)
        
        texts = []
        for row in cursor.fetchall():
            text_id, category, language, content, version, created_at, updated_at = row
            
            texts.append({
                "id": text_id,
                "category": category,
                "language": language,
                "content": content,
                "version": version,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Returning {len(texts)} texts for bot (old format)")
        return {"texts": texts}  # Старый формат для бота
        
    except Exception as e:
        logger.error(f"Error getting texts for bot: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting texts for bot: {str(e)}")

# Эндпоинты для обновления сценариев
@app.put("/api/bot-flow/scenarios/{scenario_id}")
async def update_scenario(scenario_id: str, scenario_data: dict = Body(...)):
    """Обновление сценария"""
    try:
        logger.info(f"PUT /api/bot-flow/scenarios/{scenario_id} called")
        logger.info(f"Scenario data: {scenario_data}")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Обновляем сценарий
        cursor.execute("""
            UPDATE scenarios 
            SET name = %s, description = %s, is_active = %s, updated_at = NOW()
            WHERE id = %s
        """, (
            scenario_data.get('name', ''),
            scenario_data.get('description', ''),
            scenario_data.get('is_active', False),
            scenario_id
        ))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Scenario {scenario_id} updated successfully")
        return {"status": "success", "message": f"Scenario {scenario_id} updated"}
        
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating scenario: {str(e)}")

@app.post("/api/bot-flow/scenarios")
async def create_scenario(scenario_data: dict = Body(...)):
    """Создание нового сценария"""
    try:
        logger.info("POST /api/bot-flow/scenarios called")
        logger.info(f"Scenario data: {scenario_data}")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Создаем новый сценарий
        cursor.execute("""
            INSERT INTO scenarios (id, name, description, is_active, stages, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            scenario_data.get('id', f"scenario_{int(time.time())}"),
            scenario_data.get('name', ''),
            scenario_data.get('description', ''),
            scenario_data.get('is_active', False),
            json.dumps(scenario_data.get('stages', []))
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Scenario created successfully")
        return {"status": "success", "message": "Scenario created"}
        
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating scenario: {str(e)}")

@app.delete("/api/bot-flow/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Удаление сценария"""
    try:
        logger.info(f"DELETE /api/bot-flow/scenarios/{scenario_id} called")
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM scenarios WHERE id = %s", (scenario_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Scenario {scenario_id} deleted successfully")
        return {"status": "success", "message": f"Scenario {scenario_id} deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting scenario: {str(e)}")

logger.info("All endpoints created successfully")
