from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Исправляем URL для PostgreSQL на Heroku
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔗 Подключаемся к базе данных: {DATABASE_URL}")

# Создаем движок базы данных
try:
    engine = create_engine(DATABASE_URL)
    print("✅ Движок базы данных создан успешно")
except Exception as e:
    print(f"❌ Ошибка создания движка БД: {e}")
    raise

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        print("🔍 Получена сессия базы данных")
        yield db
    except Exception as e:
        print(f"❌ Ошибка в сессии БД: {e}")
        db.rollback()
        raise
    finally:
        print("🔒 Закрываем сессию базы данных")
        db.close()
