"""Tests for the weekly scheduler (feature 003). Weekdays: Monday = 0 ... Sunday = 6."""

from app.scheduling import Occurrence, schedule_week

ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]


def task(id: int, frequency: str, duration: int = 15, **kwargs) -> Occurrence:
    return Occurrence(
        id=id,
        frequency=frequency,
        duration_minutes=duration,
        weekdays=kwargs.get("weekdays", []),
        times_per_week=kwargs.get("times_per_week"),
        times_per_day=kwargs.get("times_per_day"),
    )


def test_daily_is_every_day():
    assert schedule_week([task(1, "daily")]) == {1: ALL_DAYS}


def test_specific_days_kept():
    assert schedule_week([task(1, "days", weekdays=[0, 2, 4])]) == {1: [0, 2, 4]}


def test_per_day_is_every_day():
    assert schedule_week([task(1, "per_day", times_per_day=8)]) == {1: ALL_DAYS}


def test_weekly_on_empty_week_spreads_out():
    # Mon + Thu, not Mon + Tue.
    assert schedule_week([task(1, "weekly", times_per_week=2)]) == {1: [0, 3]}


def test_weekly_avoids_busy_days():
    gym = task(1, "days", duration=60, weekdays=[0, 1, 2, 3, 4])

    result = schedule_week([gym, task(2, "weekly", times_per_week=2)])

    assert result[2] == [5, 6]  # the weekend is free


def test_per_day_counts_times_in_load():
    # Water: 2 min x 8 a day = 16 min every day. Reading Mon-Fri: 15 min.
    # So the weekend (16) is lighter than weekdays (31).
    water = task(1, "per_day", duration=2, times_per_day=8)
    reading = task(2, "days", duration=15, weekdays=[0, 1, 2, 3, 4])

    result = schedule_week([water, reading, task(3, "weekly", times_per_week=1)])

    assert result[3] == [5]


def test_longer_weekly_task_placed_first():
    # The 60-min task is placed first (Monday) even though its id is higher,
    # so the 10-min task goes to the next lightest day.
    short = task(1, "weekly", duration=10, times_per_week=1)
    long = task(2, "weekly", duration=60, times_per_week=1)

    result = schedule_week([short, long])

    assert result == {1: [1], 2: [0]}


def test_rebalances_when_schedule_changes():
    weekly = task(1, "weekly", times_per_week=1)
    assert schedule_week([weekly]) == {1: [0]}

    monday_class = task(2, "days", duration=90, weekdays=[0])
    assert schedule_week([weekly, monday_class])[1] == [1]


def test_deterministic_on_ties():
    tasks = [task(i, "weekly", times_per_week=3) for i in (5, 3, 9)]

    assert schedule_week(tasks) == schedule_week(list(reversed(tasks)))
    assert sorted(schedule_week(tasks)[3]) == schedule_week(tasks)[3]


def test_six_times_a_week():
    assert schedule_week([task(1, "weekly", times_per_week=6)]) == {1: [0, 1, 2, 3, 4, 5]}


def test_empty():
    assert schedule_week([]) == {}
