from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "ToolStack Advisor API")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "UTC")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

@lru_cache
def get_settings():
    return Settings()
