"""Tests for a goal's 8 supporting-goal slots (feature 002)."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def goal_id(client: TestClient) -> int:
    return client.post("/goals", json={"title": "Run a marathon"}).json()["id"]


def set_slot(client: TestClient, goal_id: int, position: int, title: str):
    return client.put(f"/goals/{goal_id}/supporting-goals/{position}", json={"title": title})


def test_get_goal_with_no_supporting_goals(client: TestClient, goal_id: int):
    response = client.get(f"/goals/{goal_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == goal_id
    assert body["title"] == "Run a marathon"
    assert body["supporting_goals"] == []


def test_get_unknown_goal_is_404(client: TestClient):
    response = client.get("/goals/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Goal not found"}


def test_set_slot_creates_it(client: TestClient, goal_id: int):
    response = set_slot(client, goal_id, 0, "  Build endurance  ")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Build endurance"  # trimmed
    assert body["position"] == 0
    assert body["goal_id"] == goal_id
    assert client.get(f"/goals/{goal_id}").json()["supporting_goals"] == [body]


def test_overwrite_keeps_id(client: TestClient, goal_id: int):
    first = set_slot(client, goal_id, 3, "Diet").json()
    second = set_slot(client, goal_id, 3, "Nutrition").json()

    assert second["id"] == first["id"]  # a rename, not a new row
    assert second["title"] == "Nutrition"
    assert len(client.get(f"/goals/{goal_id}").json()["supporting_goals"]) == 1


def test_clear_slot(client: TestClient, goal_id: int):
    set_slot(client, goal_id, 2, "Sleep")

    response = client.delete(f"/goals/{goal_id}/supporting-goals/2")

    assert response.status_code == 204
    assert client.get(f"/goals/{goal_id}").json()["supporting_goals"] == []


def test_clear_empty_slot_is_204(client: TestClient, goal_id: int):
    assert client.delete(f"/goals/{goal_id}/supporting-goals/5").status_code == 204


@pytest.mark.parametrize("position", [-1, 8])
def test_position_out_of_range_is_422(client: TestClient, goal_id: int, position: int):
    assert set_slot(client, goal_id, position, "Sleep").status_code == 422
    assert client.delete(f"/goals/{goal_id}/supporting-goals/{position}").status_code == 422


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_bad_title_is_422(client: TestClient, goal_id: int, title: str):
    assert set_slot(client, goal_id, 0, title).status_code == 422


def test_set_slot_on_unknown_goal_is_404(client: TestClient):
    put = set_slot(client, 999, 0, "Sleep")
    delete = client.delete("/goals/999/supporting-goals/0")

    assert (put.status_code, put.json()) == (404, {"detail": "Goal not found"})
    assert (delete.status_code, delete.json()) == (404, {"detail": "Goal not found"})


def test_supporting_goals_ordered_by_position(client: TestClient, goal_id: int):
    for position, title in [(7, "Seventh"), (0, "First"), (4, "Fifth")]:
        set_slot(client, goal_id, position, title)

    slots = client.get(f"/goals/{goal_id}").json()["supporting_goals"]

    assert [s["position"] for s in slots] == [0, 4, 7]


def test_slots_belong_to_their_own_goal(client: TestClient, goal_id: int):
    other = client.post("/goals", json={"title": "Learn piano"}).json()["id"]
    set_slot(client, goal_id, 0, "Build endurance")
    set_slot(client, other, 0, "Practice daily")

    assert (
        client.get(f"/goals/{goal_id}").json()["supporting_goals"][0]["title"] == "Build endurance"
    )
    assert client.get(f"/goals/{other}").json()["supporting_goals"][0]["title"] == "Practice daily"
