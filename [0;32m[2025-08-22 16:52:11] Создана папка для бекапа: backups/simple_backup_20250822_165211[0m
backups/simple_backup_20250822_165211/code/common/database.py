"""
Конфигурация базы данных с SQLAlchemy async
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from .config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


# Используем правильный URL для SQLAlchemy
database_url = settings.sqlalchemy_database_url

# Создание async engine
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    poolclass=NullPool,  # Для Heroku
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

# Создание session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncSession:
    """Получить async сессию базы данных"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрытие соединений с базой данных"""
    await engine.dispose()
