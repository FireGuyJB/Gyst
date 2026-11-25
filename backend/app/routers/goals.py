"""The /goals endpoints: list and create primary goals.

A "router" is a group of related routes. main.py plugs it into the app.
"""

from fastapi import APIRouter, status
from sqlalchemy import select

from app.db import DbSession
from app.models import Goal
from app.schemas import GoalCreate, GoalRead

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
def list_goals(db: DbSession) -> list[Goal]:
    """All goals, newest first."""
    # created_at only has one-second precision on SQLite, so goals made in the
    # same second are tie-broken by id (higher id = created later).
    query = select(Goal).order_by(Goal.created_at.desc(), Goal.id.desc())
    return list(db.scalars(query))


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(goal_in: GoalCreate, db: DbSession) -> Goal:
    """Save a new goal. FastAPI has already validated `goal_in` against GoalCreate."""
    goal = Goal(title=goal_in.title)
    db.add(goal)
    db.commit()  # INSERT INTO goals ...
    db.refresh(goal)  # reload it, to pick up the id and created_at the database set
    return goal
