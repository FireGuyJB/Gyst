"""Database models (tables) live here, one class per table.

Alembic picks up every model here automatically, because alembic/env.py
imports this module. After adding or changing a model, run:

    uv run alembic revision --autogenerate -m "describe the change"
    uv run alembic upgrade head
"""

from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Goal(Base):
    """A primary goal, e.g. "Run a marathon". One row in the `goals` table.

    Its 8 supporting goals hang off it (feature 002).
    """

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    # server_default: the *database* fills this in on INSERT, so every row gets a
    # timestamp even if it's inserted outside our Python code.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # goal.supporting_goals gives this goal's supporting goals, in slot order.
    # cascade: deleting a goal (or removing one from this list) deletes the row.
    # SQLAlchemy does this itself, so it behaves the same on SQLite and Postgres.
    supporting_goals: Mapped[list["SupportingGoal"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="SupportingGoal.position",
    )


class SupportingGoal(Base):
    """One of the 8 pillars around a primary goal, e.g. "Build endurance".

    `position` is its slot in the 3x3 grid, 0-7 clockwise from the top-left.
    The slot also decides its color (see frontend/src/lib/colors.ts).
    """

    __tablename__ = "supporting_goals"
    __table_args__ = (
        # One supporting goal per slot. This is what makes "at most 8" true.
        UniqueConstraint("goal_id", "position"),
        CheckConstraint("position BETWEEN 0 AND 7", name="position_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"))
    position: Mapped[int]
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    goal: Mapped[Goal] = relationship(back_populates="supporting_goals")
    # Its 8 tasks, in slot order. Clearing this supporting goal deletes them.
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="supporting_goal",
        cascade="all, delete-orphan",
        order_by="Task.position",
    )


class Task(Base):
    """One of the 8 tasks around a supporting goal, e.g. "Run 5k".

    How often it happens is stored as plain columns (not free text), so the
    checklist can work with it directly. Which of the columns are used depends
    on `frequency`:

    - "daily":   every day.
    - "days":    on `weekdays` (a list like [0, 2, 4] = Mon, Wed, Fri).
    - "weekly":  `times_per_week` times. Gyst picks the days (app/scheduling.py).
    - "per_day": every day, `times_per_day` times (e.g. drink water 8x).
    """

    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("supporting_goal_id", "position"),
        CheckConstraint("position BETWEEN 0 AND 7", name="position_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    supporting_goal_id: Mapped[int] = mapped_column(ForeignKey("supporting_goals.id"))
    position: Mapped[int]
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(2000), default="")
    duration_minutes: Mapped[int]
    frequency: Mapped[str] = mapped_column(String(20))
    # JSON works the same on SQLite and Postgres.
    weekdays: Mapped[list[int]] = mapped_column(JSON, default=list)
    times_per_week: Mapped[int | None]
    times_per_day: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    supporting_goal: Mapped[SupportingGoal] = relationship(back_populates="tasks")
