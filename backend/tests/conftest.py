"""Shared test setup. pytest loads this file automatically.

The key idea: tests must never touch the real `gyst.db`. So each test gets a
brand-new, empty SQLite file in a temporary folder, and we tell FastAPI to hand
routes a session for *that* database instead of the real one.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.db import Base, get_db
from app.main import app


@pytest.fixture
def db_session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """A session factory bound to a fresh, empty test database."""
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    # Build the tables straight from the models. (CI separately checks that the
    # Alembic migrations apply cleanly.)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(db_session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    """A test client whose routes use the test database."""

    def get_test_db() -> Iterator[Session]:
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    # Swap the real `get_db` for the test one, for every route that depends on it.
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()
