"""Database models (tables) live here, one class per table.

Alembic picks up every model here automatically, because alembic/env.py
imports this module. After adding or changing a model, run:

    uv run alembic revision --autogenerate -m "describe the change"
    uv run alembic upgrade head
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Goal(Base):
    """A primary goal, e.g. "Run a marathon". One row in the `goals` table.

    Supporting goals and tasks will hang off this in feature 002.
    """

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    # server_default: the *database* fills this in on INSERT, so every row gets a
    # timestamp even if it's inserted outside our Python code.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
