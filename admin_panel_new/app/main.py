from fastapi import FastAPI
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

logger.info("=== MINIMAL TEST APP STARTUP ===")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    logger.info("Test endpoint called")
    return {"message": "Test works!"}

@app.post("/api/auth/login")
async def login():
    logger.info("Login endpoint called")
    return {"access_token": "demo-token", "token_type": "bearer"}

logger.info("=== MINIMAL TEST APP READY ===")
# Force deploy
