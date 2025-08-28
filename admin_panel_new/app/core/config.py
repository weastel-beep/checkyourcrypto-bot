from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "Check Your Crypto Admin API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # База данных - используем реальную базу бота
    DATABASE_URL: str = "sqlite:///../checkyourcrypto.db"
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com",
        "https://checkyourcrypto-bot-87c446f24699.herokuapp.com"
    ]
    
    # Telegram Bot настройки
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
