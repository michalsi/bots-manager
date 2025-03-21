import logging
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Initialize these as None
_engine = None
_session_maker = None


def get_session_maker() -> Optional[sessionmaker]:
    """Get the current session maker"""
    global _session_maker
    return _session_maker

def init_db(database_url: str) -> None:
    """Initialize database connection"""
    global _engine, _session_maker

    if _session_maker is not None:
        return

    logger.info(f"Initializing database connection with URL: {database_url}")

    try:
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,
            echo=True
        )

        _session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )

        with _session_maker() as session:
            session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")

        # Create all tables
        Base.metadata.create_all(bind=_engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        _engine = None
        _session_maker = None
        raise
