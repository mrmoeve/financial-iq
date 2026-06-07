from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StatementIQ"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    database_url: str = "postgresql+psycopg://statementiq:statementiq@localhost:5432/statementiq"
    secret_key: str = "replace-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
