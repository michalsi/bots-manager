import os

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
        env_nested_delimiter='__'
    )

    def __init__(self, **kwargs):
        print("Current working directory:", os.getcwd())  # Debug line
        print("Environment variables:", dict(os.environ))  # Debug line
        super().__init__(**kwargs)
