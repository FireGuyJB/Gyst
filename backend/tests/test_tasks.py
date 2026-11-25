"""Tests for a supporting goal's 8 task slots (feature 003)."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def goal_id(client: TestClient) -> int:
    return client.post("/goals", json={"title": "Run a marathon"}).json()["id"]


@pytest.fixture
def sg_id(client: TestClient, goal_id: int) -> int:
    """A supporting goal in slot 2 of the goal."""
    return client.put(
        f"/goals/{goal_id}/supporting-goals/2", json={"title": "Build endurance"}
    ).json()["id"]


def set_task(client: TestClient, sg_id: int, position: int, **fields):
    body = {"title": "Run 5k", "duration_minutes": 30, "frequency": "daily"} | fields
    return client.put(f"/supporting-goals/{sg_id}/tasks/{position}", json=body)


def test_get_supporting_goal_with_no_tasks(client: TestClient, goal_id: int, sg_id: int):
    response = client.get(f"/supporting-goals/{sg_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": sg_id,
        "goal_id": goal_id,
        "goal_title": "Run a marathon",
        "position": 2,
        "title": "Build endurance",
        "tasks": [],
    }


def test_unknown_supporting_goal_is_404(client: TestClient):
    response = client.get("/supporting-goals/999")

    assert (response.status_code, response.json()) == (404, {"detail": "Supporting goal not found"})
    put = set_task(client, 999, 0)
    assert (put.status_code, put.json()) == (404, {"detail": "Supporting goal not found"})


def test_set_daily_task(client: TestClient, sg_id: int):
    response = set_task(client, sg_id, 0, title="  Stretch  ", description="Hamstrings")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Stretch"
    assert body["description"] == "Hamstrings"
    assert body["position"] == 0
    assert body["supporting_goal_id"] == sg_id
    assert body["frequency"] == "daily"
    assert body["scheduled_days"] == [0, 1, 2, 3, 4, 5, 6]
    assert client.get(f"/supporting-goals/{sg_id}").json()["tasks"] == [body]


def test_description_defaults_to_empty(client: TestClient, sg_id: int):
    assert set_task(client, sg_id, 0).json()["description"] == ""


def test_overwrite_task_keeps_id(client: TestClient, sg_id: int):
    first = set_task(client, sg_id, 1, title="Run 5k").json()
    second = set_task(client, sg_id, 1, title="Run 10k").json()

    assert second["id"] == first["id"]
    assert len(client.get(f"/supporting-goals/{sg_id}").json()["tasks"]) == 1


def test_set_days_task_sorts_weekdays(client: TestClient, sg_id: int):
    body = set_task(client, sg_id, 0, frequency="days", weekdays=[4, 0, 2]).json()

    assert body["weekdays"] == [0, 2, 4]
    assert body["scheduled_days"] == [0, 2, 4]


@pytest.mark.parametrize("weekdays", [[], [0, 0], [7], [-1]])
def test_bad_weekdays_is_422(client: TestClient, sg_id: int, weekdays: list[int]):
    assert set_task(client, sg_id, 0, frequency="days", weekdays=weekdays).status_code == 422


@pytest.mark.parametrize("times", [None, 0, 7])
def test_weekly_needs_times_per_week_1_to_6(client: TestClient, sg_id: int, times):
    assert set_task(client, sg_id, 0, frequency="weekly", times_per_week=times).status_code == 422


@pytest.mark.parametrize(
    "times, ok", [(None, False), (1, False), (2, True), (20, True), (21, False)]
)
def test_per_day_range(client: TestClient, sg_id: int, times, ok: bool):
    response = set_task(client, sg_id, 0, frequency="per_day", times_per_day=times)

    assert response.status_code == (200 if ok else 422)


@pytest.mark.parametrize("minutes, ok", [(0, False), (1, True), (480, True), (481, False)])
def test_duration_range(client: TestClient, sg_id: int, minutes: int, ok: bool):
    assert set_task(client, sg_id, 0, duration_minutes=minutes).status_code == (200 if ok else 422)


@pytest.mark.parametrize(
    "fields",
    [{"title": "   "}, {"title": "x" * 201}, {"description": "x" * 2001}, {"frequency": "monthly"}],
)
def test_bad_fields_are_422(client: TestClient, sg_id: int, fields: dict):
    assert set_task(client, sg_id, 0, **fields).status_code == 422


@pytest.mark.parametrize("position", [-1, 8])
def test_task_position_out_of_range_is_422(client: TestClient, sg_id: int, position: int):
    assert set_task(client, sg_id, position).status_code == 422


def test_unused_fields_are_dropped(client: TestClient, sg_id: int):
    body = set_task(
        client, sg_id, 0, frequency="daily", weekdays=[1], times_per_week=3, times_per_day=5
    ).json()

    assert (body["weekdays"], body["times_per_week"], body["times_per_day"]) == ([], None, None)


def test_weekly_task_gets_scheduled_days(client: TestClient, sg_id: int):
    body = set_task(client, sg_id, 0, frequency="weekly", times_per_week=2).json()

    assert body["times_per_week"] == 2
    assert body["scheduled_days"] == [0, 3]


def test_weekly_rebalances_when_schedule_changes(client: TestClient, goal_id: int, sg_id: int):
    weekly = set_task(client, sg_id, 0, frequency="weekly", times_per_week=1, duration_minutes=30)
    assert weekly.json()["scheduled_days"] == [0]

    # A task under a *different* supporting goal still counts: the day is shared.
    other_sg = client.put(f"/goals/{goal_id}/supporting-goals/5", json={"title": "Sleep"}).json()
    set_task(client, other_sg["id"], 0, frequency="days", weekdays=[0], duration_minutes=60)

    tasks = client.get(f"/supporting-goals/{sg_id}").json()["tasks"]
    assert tasks[0]["scheduled_days"] == [1]


def test_tasks_ordered_by_position(client: TestClient, sg_id: int):
    for position in (6, 1, 3):
        set_task(client, sg_id, position)

    tasks = client.get(f"/supporting-goals/{sg_id}").json()["tasks"]

    assert [t["position"] for t in tasks] == [1, 3, 6]


def test_clear_task(client: TestClient, sg_id: int):
    set_task(client, sg_id, 4)

    assert client.delete(f"/supporting-goals/{sg_id}/tasks/4").status_code == 204
    assert client.delete(f"/supporting-goals/{sg_id}/tasks/4").status_code == 204  # already empty
    assert client.get(f"/supporting-goals/{sg_id}").json()["tasks"] == []


def test_clear_supporting_goal_deletes_its_tasks(client: TestClient, goal_id: int, sg_id: int):
    set_task(client, sg_id, 0)
    client.delete(f"/goals/{goal_id}/supporting-goals/2")

    assert client.get(f"/supporting-goals/{sg_id}").status_code == 404
    # A new supporting goal in the same slot starts with no tasks.
    new = client.put(f"/goals/{goal_id}/supporting-goals/2", json={"title": "Speed"}).json()
    assert client.get(f"/supporting-goals/{new['id']}").json()["tasks"] == []


def test_renaming_supporting_goal_keeps_tasks(client: TestClient, goal_id: int, sg_id: int):
    set_task(client, sg_id, 0)
    client.put(f"/goals/{goal_id}/supporting-goals/2", json={"title": "Stamina"})

    assert len(client.get(f"/supporting-goals/{sg_id}").json()["tasks"]) == 1
