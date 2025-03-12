from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Initialize variables
engine = None
SessionLocal = None


def init_db(database_url: str) -> None:
    """Initialize database connection"""
    global engine
    global SessionLocal
    if engine is None:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
