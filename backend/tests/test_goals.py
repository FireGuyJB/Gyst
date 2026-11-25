"""Tests for the /goals endpoints (feature 001)."""

from fastapi.testclient import TestClient


def test_list_goals_is_empty_at_first(client: TestClient):
    response = client.get("/goals")

    assert response.status_code == 200
    assert response.json() == []


def test_create_goal_returns_201_and_the_goal(client: TestClient):
    response = client.post("/goals", json={"title": "Run a marathon"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Run a marathon"
    assert isinstance(body["id"], int)
    assert body["created_at"]  # set by the database


def test_created_goal_appears_in_list(client: TestClient):
    created = client.post("/goals", json={"title": "Run a marathon"}).json()

    assert client.get("/goals").json() == [created]


def test_list_goals_is_newest_first(client: TestClient):
    # Created within the same second, so this also checks the tie-breaker.
    for title in ["first", "second", "third"]:
        client.post("/goals", json={"title": title})

    titles = [goal["title"] for goal in client.get("/goals").json()]

    assert titles == ["third", "second", "first"]


def test_title_is_trimmed(client: TestClient):
    response = client.post("/goals", json={"title": "  Run a marathon  "})

    assert response.status_code == 201
    assert response.json()["title"] == "Run a marathon"


def test_blank_title_is_rejected(client: TestClient):
    for title in ["", "   "]:
        response = client.post("/goals", json={"title": title})
        assert response.status_code == 422, title

    assert client.get("/goals").json() == []


def test_missing_title_is_rejected(client: TestClient):
    assert client.post("/goals", json={}).status_code == 422


def test_title_up_to_200_characters_is_allowed(client: TestClient):
    response = client.post("/goals", json={"title": "x" * 200})

    assert response.status_code == 201


def test_title_over_200_characters_is_rejected(client: TestClient):
    response = client.post("/goals", json={"title": "x" * 201})

    assert response.status_code == 422


def test_length_limit_applies_after_trimming(client: TestClient):
    # 200 real characters plus padding is fine: the spaces are trimmed first.
    response = client.post("/goals", json={"title": "  " + "x" * 200 + "  "})

    assert response.status_code == 201


def test_cors_allows_the_frontend_origin(client: TestClient):
    # The browser sends this "preflight" before a cross-origin POST with JSON.
    response = client.options(
        "/goals",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_ignores_other_origins(client: TestClient):
    response = client.get("/goals", headers={"Origin": "http://evil.example"})

    assert "access-control-allow-origin" not in response.headers


def test_created_at_is_marked_as_utc(client: TestClient):
    # SQLite stores timestamps without a timezone. Without the "Z"/"+00:00" a browser
    # would read the time as *local* time and show it hours off.
    created_at = client.post("/goals", json={"title": "Run a marathon"}).json()["created_at"]

    assert created_at.endswith(("Z", "+00:00"))
