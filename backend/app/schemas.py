"""Request and response shapes for the API (Pydantic models).

These are different from the database models in models.py:
- models.py describes how data is *stored* (tables and columns).
- schemas.py describes what the API *accepts and returns* (JSON).

FastAPI uses these to validate incoming JSON (bad input gets a 422 before our
code runs) and to build the interactive docs at /docs.
"""

from datetime import UTC, datetime
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

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


Frequency = Literal["daily", "days", "weekly", "per_day"]
Weekday = Annotated[int, Field(ge=0, le=6)]  # Monday = 0 ... Sunday = 6


class TaskSet(BaseModel):
    """The JSON body for PUT /supporting-goals/{id}/tasks/{position}.

    Only `title`, `duration_minutes` and `frequency` are always needed. Which
    of the other fields are needed depends on the frequency (see models.Task).
    """

    title: GoalTitle = Field(examples=["Run 5k"])
    description: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] = ""
    duration_minutes: int = Field(ge=1, le=480, examples=[30])
    frequency: Frequency
    weekdays: list[Weekday] = []
    times_per_week: int | None = Field(default=None, ge=1, le=6)  # 7 would be "daily"
    times_per_day: int | None = Field(default=None, ge=2, le=20)

    @model_validator(mode="after")
    def check_frequency_fields(self) -> Self:
        """Require the field this frequency needs, and drop the ones it doesn't.

        Dropping means a task switched from "days" to "daily" doesn't keep a
        stale list of weekdays around.
        """
        if self.frequency == "days":
            if not self.weekdays:
                raise ValueError("pick at least one weekday")
            if len(set(self.weekdays)) != len(self.weekdays):
                raise ValueError("each weekday can only be picked once")
            self.weekdays = sorted(self.weekdays)
        else:
            self.weekdays = []

        if self.frequency == "weekly" and self.times_per_week is None:
            raise ValueError("say how many times per week (1-6)")
        if self.frequency != "weekly":
            self.times_per_week = None

        if self.frequency == "per_day" and self.times_per_day is None:
            raise ValueError("say how many times per day (2-20)")
        if self.frequency != "per_day":
            self.times_per_day = None
        return self


class TaskRead(BaseModel):
    """A task as the API returns it."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    supporting_goal_id: int
    position: int
    title: str
    description: str
    duration_minutes: int
    frequency: Frequency
    weekdays: list[int]
    times_per_week: int | None
    times_per_day: int | None
    # Worked out by app/scheduling.py each time, not stored: the weekdays this
    # task lands on this week. For "weekly" tasks, Gyst picks them.
    scheduled_days: list[int]


class SupportingGoalDetail(BaseModel):
    """One supporting goal with its tasks, for the task grid page."""

    id: int
    goal_id: int
    goal_title: str  # for the "back to" link
    position: int  # decides its color
    title: str
    tasks: list[TaskRead]
