from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.backend.logger import logger


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation and environment loading.
    Pydantic will automatically load these values from environment variables.
    """
    APP_NAME: str = "Trading Bot Manager"
    DEBUG: bool = True
    DATABASE_URL: str
    API_KEY: str
    API_SECRET: str
    BYBIT_SECURE_TOKEN: str
    BYBIT_DEVICE_ID: str
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    LOG_LEVEL: str = "INFO"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
        env_nested_delimiter='__'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug("Settings initialized")
