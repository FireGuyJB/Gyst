"""Request and response shapes for the API (Pydantic models).

These are different from the database models in models.py:
- models.py describes how data is *stored* (tables and columns).
- schemas.py describes what the API *accepts and returns* (JSON).

FastAPI uses these to validate incoming JSON (bad input gets a 422 before our
code runs) and to build the interactive docs at /docs.
"""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

# A goal title: surrounding spaces are stripped *first*, then the 1-200 limit is
# checked. So "   " becomes "" and is rejected as too short.
GoalTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class GoalCreate(BaseModel):
    """The JSON body for POST /goals."""

    title: GoalTitle = Field(examples=["Run a marathon"])


class GoalRead(BaseModel):
    """A goal as the API returns it."""

    # Lets Pydantic read the values straight off a SQLAlchemy `Goal` object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def assume_utc(cls, value: datetime) -> datetime:
        """SQLite hands back timestamps with no timezone; they're UTC, so say so.

        Without this the JSON would be "2026-11-24T22:09:40" and a browser would
        read it as local time. (Postgres already includes the timezone.)
        """
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value


class SupportingGoalSet(BaseModel):
    """The JSON body for PUT /goals/{goal_id}/supporting-goals/{position}."""

    title: GoalTitle = Field(examples=["Build endurance"])


class SupportingGoalRead(BaseModel):
    """A supporting goal as the API returns it."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    position: int  # 0-7, clockwise from the top-left of the grid
    title: str


class GoalDetail(GoalRead):
    """One goal plus its supporting goals (only filled slots, in position order)."""

    supporting_goals: list[SupportingGoalRead]
