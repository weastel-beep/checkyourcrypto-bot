"""
Конфигурация базы данных с SQLAlchemy async
"""
import logging
import os
import traceback
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from .config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""

    pass


# Используем правильный URL для SQLAlchemy
database_url = settings.database_url

logger.info(f"🔍 DEBUG: Original database URL: {database_url}")

# Конвертируем URL для async драйвера
if database_url.startswith("postgresql://"):
    # Используем postgresql+asyncpg для async engine (SQLAlchemy 2.0 синтаксис)
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info(f"🔍 DEBUG: Converting postgresql:// to postgresql+asyncpg://")
elif database_url.startswith("sqlite://"):
    # Для SQLite используем правильный формат
    if database_url.startswith("sqlite:///"):
        # Абсолютный путь
        async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    else:
        # Относительный путь
        async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    logger.info(f"🔍 DEBUG: Converting sqlite:// to sqlite+aiosqlite://")
else:
    async_database_url = database_url
    logger.info(f"🔍 DEBUG: No conversion needed")

logger.info(f"🔍 DEBUG: Final async URL: {async_database_url}")

# Добавляем больше диагностики
print(f"🔍 DEBUG: Original database URL: {database_url}")
print(f"🔍 DEBUG: Final async URL: {async_database_url}")
print(f"🔍 DEBUG: Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
print(f"🔍 DEBUG: DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT_SET')}")

# Проверяем доступность драйверов
try:
    import asyncpg

    logger.info(f"✅ asyncpg version: {asyncpg.__version__}")
except ImportError as e:
    logger.error(f"❌ asyncpg not available: {e}")

try:
    import psycopg2

    logger.info(f"✅ psycopg2 version: {psycopg2.__version__}")
except ImportError as e:
    logger.error(f"❌ psycopg2 not available: {e}")

logger.info(f"🔍 DEBUG: About to create async engine with URL: {async_database_url}")

# Создание async engine
try:
    logger.info("🔍 DEBUG: Creating async engine...")
    engine = create_async_engine(
        async_database_url,
        echo=settings.debug,
        poolclass=NullPool,  # Для Heroku
        future=True,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    )
    logger.info(f"✅ Async engine created successfully")
    logger.info("🔍 DEBUG: Engine creation completed")
except Exception as e:
    logger.error(f"❌ Failed to create async engine: {e}")
    logger.error(f"❌ Error type: {type(e)}")
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    raise

# Создание session factory
logger.info("🔍 DEBUG: Creating session factory...")
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
logger.info("🔍 DEBUG: Session factory created successfully")


async def get_async_session() -> AsyncSession:
    """Получить async сессию базы данных"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных"""
    logger.info("🔍 init_db: Начинаем инициализацию БД...")

    # Импортируем модели здесь, чтобы избежать циклического импорта
    try:
        from . import models

        logger.info("✅ init_db: Модели импортированы успешно")
    except Exception as e:
        logger.error(f"❌ init_db: Ошибка импорта моделей: {e}")
        raise

    try:
        async with engine.begin() as conn:
            logger.info("🔍 init_db: Создаем таблицы...")
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ init_db: Таблицы созданы успешно")
    except Exception as e:
        logger.error(f"❌ init_db: Ошибка создания таблиц: {e}")
        raise

    logger.info("✅ init_db: Инициализация БД завершена успешно")


async def close_db():
    """Закрытие соединений с базой данных"""
    await engine.dispose()
