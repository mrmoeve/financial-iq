from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings(BaseSettings):
    app_name: str = "StatementIQ"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    database_url: str = "sqlite:///statementiq.db"
    secret_key: str = "replace-me"
    admin_email: str = "mrmoeve@gmail.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def normalized_database_url(self) -> str:
        return _normalize_database_url(self.database_url)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
