"""The /supporting-goals endpoints: a supporting goal and its 8 task slots.

Works like the supporting-goal slots in goals.py, one level down.
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.db import DbSession
from app.models import SupportingGoal, Task
from app.routers.goals import Position
from app.scheduling import Occurrence, schedule_week
from app.schemas import SupportingGoalDetail, TaskRead, TaskSet

router = APIRouter(prefix="/supporting-goals", tags=["tasks"])


def get_supporting_goal_or_404(db: DbSession, supporting_goal_id: int) -> SupportingGoal:
    supporting_goal = db.get(SupportingGoal, supporting_goal_id)
    if supporting_goal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Supporting goal not found")
    return supporting_goal


def this_weeks_schedule(db: DbSession) -> dict[int, list[int]]:
    """Every task's weekdays this week. Uses *all* tasks, since a day is shared."""
    # shortcut: reschedules every task on each request; fine for one user, revisit with accounts.
    tasks = db.scalars(select(Task)).all()
    return schedule_week(
        [
            Occurrence(
                id=t.id,
                frequency=t.frequency,
                duration_minutes=t.duration_minutes,
                weekdays=t.weekdays,
                times_per_week=t.times_per_week,
                times_per_day=t.times_per_day,
            )
            for t in tasks
        ]
    )


def to_read(task: Task, schedule: dict[int, list[int]]) -> TaskRead:
    """A Task row plus its scheduled days, in the shape the API returns."""
    return TaskRead(
        id=task.id,
        supporting_goal_id=task.supporting_goal_id,
        position=task.position,
        title=task.title,
        description=task.description,
        duration_minutes=task.duration_minutes,
        frequency=task.frequency,
        weekdays=task.weekdays,
        times_per_week=task.times_per_week,
        times_per_day=task.times_per_day,
        scheduled_days=schedule[task.id],
    )


@router.get("/{supporting_goal_id}", response_model=SupportingGoalDetail)
def get_supporting_goal(supporting_goal_id: int, db: DbSession) -> SupportingGoalDetail:
    """One supporting goal with its tasks, for the task grid page."""
    sg = get_supporting_goal_or_404(db, supporting_goal_id)
    schedule = this_weeks_schedule(db)
    return SupportingGoalDetail(
        id=sg.id,
        goal_id=sg.goal_id,
        goal_title=sg.goal.title,
        position=sg.position,
        title=sg.title,
        tasks=[to_read(t, schedule) for t in sg.tasks],
    )


@router.put("/{supporting_goal_id}/tasks/{position}", response_model=TaskRead)
def set_task(
    supporting_goal_id: int, position: Position, task_in: TaskSet, db: DbSession
) -> TaskRead:
    """Fill a task slot, or replace what's in it (keeping the same id)."""
    sg = get_supporting_goal_or_404(db, supporting_goal_id)
    task = next((t for t in sg.tasks if t.position == position), None)
    if task is None:
        task = Task(position=position)
        sg.tasks.append(task)
    # Copy every field from the request onto the row. TaskSet's field names
    # match the Task columns, so this sets title, description, frequency, ...
    for field, value in task_in.model_dump().items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return to_read(task, this_weeks_schedule(db))


@router.delete("/{supporting_goal_id}/tasks/{position}", status_code=status.HTTP_204_NO_CONTENT)
def clear_task(supporting_goal_id: int, position: Position, db: DbSession) -> Response:
    """Empty a task slot. Clearing an already-empty slot is fine (still 204)."""
    sg = get_supporting_goal_or_404(db, supporting_goal_id)
    sg.tasks = [t for t in sg.tasks if t.position != position]
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
