from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduGenie"
    app_env: str = "development"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    demo_mode: bool = True
    use_local_explanation: bool = False

    host: str = "127.0.0.1"
    port: int = 8000

    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()