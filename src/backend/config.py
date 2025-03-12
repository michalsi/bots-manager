from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation and environment loading.
    Pydantic will automatically load these values from environment variables.
    """
    APP_NAME: str = "Trading Bot Manager"
    DEBUG: bool = True
    DATABASE_URL: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )
