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
logger.info("=== SIMPLE API STARTUP ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

app = FastAPI(title="CheckYourCrypto Admin API - SIMPLE VERSION")

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
            FROM texts
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

logger.info("All endpoints created successfully")
