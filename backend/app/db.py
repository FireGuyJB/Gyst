"""Database layer: how the API talks to the database.

- `engine`: the connection to the database (created lazily, nothing connects on import).
- `SessionLocal`: makes a "session", one unit of work (a few reads and writes).
- `Base`: every table (model) we define will inherit from this.
- `get_db`: a FastAPI dependency that hands each request its own session.

No tables exist yet; the first models arrive with the first feature.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite only allows one thread per connection by default; FastAPI uses several.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for all database models."""


def get_db() -> Iterator[Session]:
    """Yield a database session for one request, and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
