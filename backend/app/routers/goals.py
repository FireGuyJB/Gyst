"""The /goals endpoints: primary goals and their 8 supporting-goal slots.

A "router" is a group of related routes. main.py plugs it into the app.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status
from sqlalchemy import select

from app.db import DbSession
from app.models import Goal, SupportingGoal
from app.schemas import GoalCreate, GoalDetail, GoalRead, SupportingGoalRead, SupportingGoalSet

router = APIRouter(prefix="/goals", tags=["goals"])

# A slot number in the 3x3 grid. FastAPI rejects anything outside 0-7 with a 422,
# so "at most 8 supporting goals" can't be broken through the API.
Position = Annotated[int, Path(ge=0, le=7, description="Slot 0-7, clockwise from the top-left")]


def get_goal_or_404(db: DbSession, goal_id: int) -> Goal:
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


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


@router.get("/{goal_id}", response_model=GoalDetail)
def get_goal(goal_id: int, db: DbSession) -> Goal:
    """One goal with its supporting goals, for the 3x3 grid page."""
    return get_goal_or_404(db, goal_id)


@router.put("/{goal_id}/supporting-goals/{position}", response_model=SupportingGoalRead)
def set_supporting_goal(
    goal_id: int, position: Position, slot_in: SupportingGoalSet, db: DbSession
) -> SupportingGoal:
    """Fill a slot, or rename what's already in it.

    PUT means "make this slot look like this": sending it twice gives the same
    result. Renaming keeps the row (and its id), so its tasks stay attached.
    """
    goal = get_goal_or_404(db, goal_id)
    slot = next((s for s in goal.supporting_goals if s.position == position), None)
    if slot is None:
        slot = SupportingGoal(position=position, title=slot_in.title)
        goal.supporting_goals.append(slot)
    else:
        slot.title = slot_in.title
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/{goal_id}/supporting-goals/{position}", status_code=status.HTTP_204_NO_CONTENT)
def clear_supporting_goal(goal_id: int, position: Position, db: DbSession) -> Response:
    """Empty a slot. Clearing an already-empty slot is fine (still 204)."""
    goal = get_goal_or_404(db, goal_id)
    # Removing it from the list deletes the row (cascade="all, delete-orphan").
    goal.supporting_goals = [s for s in goal.supporting_goals if s.position != position]
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
