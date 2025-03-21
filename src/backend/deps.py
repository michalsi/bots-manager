from functools import lru_cache
from typing import Generator

from sqlalchemy.orm import Session

from .config import Settings
from .database import init_db, get_session_maker
from .logger import logger


@lru_cache()
def get_settings() -> Settings:
    """Cache settings to avoid loading .env file multiple times"""
    return Settings()


def get_db() -> Generator[Session, None, None]:
    """Database dependency"""
    settings = get_settings()
    try:
        # Initialize database if needed
        init_db(settings.DATABASE_URL)
        # Get session maker
        session_maker = get_session_maker()
        if session_maker is None:
            raise RuntimeError("Database session maker not initialized")
        db = session_maker()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise RuntimeError(f"Database session error: {e}")
