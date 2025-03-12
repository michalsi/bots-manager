import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic import ConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.config import Settings
from src.backend.database import Base, init_db
from src.backend.deps import get_settings, get_db
from src.backend.main import app

# Test database URLs
SQLITE_TEST_DB = "sqlite:///./test.db"
POSTGRES_TEST_DB = "postgresql://test_user:test_password@localhost:5433/test_db"


class TestSettings(Settings):
    """Test settings that override the main settings"""
    DATABASE_URL: str = SQLITE_TEST_DB
    model_config = ConfigDict(
        env_file=".env.test",
        extra="ignore"
    )


def get_test_db_url() -> str:
    """Get database URL based on test type"""
    return POSTGRES_TEST_DB if os.getenv("USE_POSTGRES_TEST_DB") else SQLITE_TEST_DB


@pytest.fixture(scope="session", autouse=True)
def test_db_engine():
    """Create test database engine"""
    database_url = get_test_db_url()
    engine = create_engine(database_url)

    # Initialize the test database
    init_db(database_url)

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if database_url.startswith("sqlite"):
        try:
            os.remove("./test.db")
        except FileNotFoundError:
            pass


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_settings():
    """Override settings for testing"""
    return TestSettings()


def get_test_db(test_db_engine) -> Generator:
    """Test database dependency"""
    TestingSessionLocal = sessionmaker(bind=test_db_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db_engine):
    """Create test client with overridden dependencies"""

    def override_get_db():
        yield from get_test_db(test_db_engine)

    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test that requires PostgreSQL"
    )
