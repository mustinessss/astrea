from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Создать engine с оптимальной конфигурацией
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,           # Размер пула соединений
    max_overflow=20,        # Максимально дополнительных соединений
    pool_recycle=3600,      # Пересоздавать соединение каждый час
    pool_pre_ping=True      # Проверять соединение перед использованием
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
