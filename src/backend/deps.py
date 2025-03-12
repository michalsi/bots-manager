from functools import lru_cache
from typing import Generator

from .config import Settings
from .database import SessionLocal, init_db


@lru_cache()
def get_settings() -> Settings:
    """Cache settings to avoid loading .env file multiple times"""
    return Settings()


def get_db() -> Generator:
    """Database dependency"""
    settings = get_settings()
    if not SessionLocal:
        init_db(settings.DATABASE_URL)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
