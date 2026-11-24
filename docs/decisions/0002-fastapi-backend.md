# 0002. FastAPI for the Python API

- **Status:** Accepted
- **Date:** 2026-11-24

## Context

We want the API in Python. It mainly serves JSON to the frontend.

## Decision

Use **FastAPI**, managed with **uv** (Python 3.12+), linted/formatted with
**ruff**, tested with **pytest**.

## Alternatives considered

- **Django + Django REST Framework:** batteries included (admin, auth, ORM),
  but heavier and more "magic"; harder to see how the layers connect.
- **Flask:** simple, but no built-in request validation or API docs.

## Consequences

- Type hints drive validation and auto-generated interactive docs at
  `/docs`, which makes it easy to try endpoints by hand.
- We assemble pieces ourselves (SQLAlchemy for data, and auth later), which
  is more to set up but more visible.
