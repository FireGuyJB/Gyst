"""App settings, read from environment variables (or a local `.env` file).

Keeping config in one place means switching databases later is a one-line
change: set DATABASE_URL to a Postgres URL instead of SQLite.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The backend/ folder. Paths are built from here so commands behave the same
# whichever folder you run them from.
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    # SQLite file in the backend folder. Later: postgresql+psycopg://user:pass@host/gyst
    database_url: str = f"sqlite:///{BACKEND_DIR / 'gyst.db'}"

    # Websites allowed to call this API from a browser (CORS). The frontend runs
    # on a different port, so the browser asks first. Set as a JSON list, e.g.
    # CORS_ORIGINS='["http://localhost:3000","https://gyst.example"]'
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
