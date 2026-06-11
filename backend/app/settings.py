from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "open-health-server"
    environment: str = "development"
    api_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://ohs:ohs@localhost:5433/open_health_server"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OHS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
