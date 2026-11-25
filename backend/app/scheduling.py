"""Works out which weekdays each task lands on this week (feature 003).

"Every day", "specific days" and "x times per day" tasks are fixed. "x times
per week" tasks are flexible: Gyst puts them on the days with the least work.
Nothing here is stored. The API runs it every time it returns tasks, so the
weekly tasks rebalance whenever the schedule changes (the user's choice; see
docs/features/003-tasks/spec.md).

This is a "pure function": it only looks at its input, never the database, so
it's easy to test on its own.
"""

from collections.abc import Sequence
from dataclasses import dataclass

DAYS = range(7)  # Monday = 0 ... Sunday = 6


@dataclass(frozen=True)
class Occurrence:
    """The parts of a task the scheduler needs."""

    id: int
    frequency: str  # "daily" | "days" | "weekly" | "per_day"
    duration_minutes: int
    weekdays: list[int]  # only for "days"
    times_per_week: int | None  # only for "weekly"
    times_per_day: int | None  # only for "per_day"


def gap(day: int, chosen: list[int]) -> int:
    """How far `day` is from the nearest chosen day, going round the week.

    Sunday and Monday are 1 apart. With nothing chosen yet, every day ties at 7.
    """
    return min((min(abs(day - c), 7 - abs(day - c)) for c in chosen), default=7)


def schedule_week(tasks: Sequence[Occurrence]) -> dict[int, list[int]]:
    """Map each task's id to the sorted weekdays it's scheduled on."""
    loads = [0] * 7  # minutes of work already on each day
    result: dict[int, list[int]] = {}

    # 1. Fixed tasks: their days are known, they just add to the load.
    for t in tasks:
        if t.frequency == "weekly":
            continue
        days = sorted(t.weekdays) if t.frequency == "days" else list(DAYS)
        minutes = t.duration_minutes * (t.times_per_day or 1)
        for day in days:
            loads[day] += minutes
        result[t.id] = days

    # 2. Weekly tasks, longest first (big tasks are hardest to fit), then by id
    #    so the answer never depends on the order tasks arrive in.
    weekly = sorted(
        (t for t in tasks if t.frequency == "weekly"), key=lambda t: (-t.duration_minutes, t.id)
    )
    for t in weekly:
        chosen: list[int] = []
        for _ in range(t.times_per_week or 0):
            # Lightest day first; on a tie, the day furthest from this task's
            # other days (so 2x a week is Mon + Thu, not Mon + Tue); then earliest.
            day = min(
                (d for d in DAYS if d not in chosen),
                key=lambda d: (loads[d], -gap(d, chosen), d),
            )
            chosen.append(day)
            loads[day] += t.duration_minutes
        result[t.id] = sorted(chosen)

    return result
