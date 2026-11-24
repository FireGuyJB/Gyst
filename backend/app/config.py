"""App settings, read from environment variables (or a local `.env` file).

Keeping config in one place means switching databases later is a one-line
change: set DATABASE_URL to a Postgres URL instead of SQLite.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite file in the backend folder. Later: postgresql+psycopg://user:pass@host/gyst
    database_url: str = "sqlite:///./gyst.db"


settings = Settings()
