"""Database layer: how the API talks to the database.

- `engine`: the connection to the database (created lazily, nothing connects on import).
- `SessionLocal`: makes a "session", one unit of work (a few reads and writes).
- `Base`: every table (model) we define will inherit from this.
- `get_db`: a FastAPI dependency that hands each request its own session.
- `DbSession`: the type to put on a route parameter to receive that session.
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite only allows one thread per connection by default; FastAPI uses several.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for all database models."""

    # Give every constraint a predictable name (e.g. "fk_tasks_goal_id_goals"), so
    # migrations can find and change them identically on SQLite and Postgres.
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def get_db() -> Iterator[Session]:
    """Yield a database session for one request, and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Use in a route as `def my_route(db: DbSession)`. FastAPI sees the Depends(...)
# and calls get_db() for each request, passing the session in as `db`.
DbSession = Annotated[Session, Depends(get_db)]
