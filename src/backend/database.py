from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# SessionLocal is used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency function that creates a new SQLAlchemy SessionLocal
    that will be used in a single request, and then closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()