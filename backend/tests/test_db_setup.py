"""Guards for database setup that are painful to change once tables exist."""

import os
import subprocess
from pathlib import Path

from app.config import BACKEND_DIR, Settings
from app.db import Base


def test_constraints_get_predictable_names():
    # Named constraints let migrations drop/alter them the same way on SQLite and Postgres.
    convention = Base.metadata.naming_convention
    assert convention["pk"] == "pk_%(table_name)s"
    assert convention["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    assert convention["uq"] == "uq_%(table_name)s_%(column_0_name)s"


def test_alembic_uses_batch_mode_for_sqlite():
    # SQLite can't ALTER columns; batch mode makes Alembic rebuild the table instead.
    env_py = (BACKEND_DIR / "alembic" / "env.py").read_text()
    assert env_py.count("render_as_batch=True") == 2  # offline + online


def test_default_database_lives_in_backend_folder(monkeypatch):
    # Same database no matter which folder you run commands from.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)
    assert settings.database_url == f"sqlite:///{BACKEND_DIR / 'gyst.db'}"


def test_alembic_accepts_percent_in_database_url(tmp_path: Path):
    # URL-encoded passwords (e.g. p%40ss) contain '%', which Alembic's config would choke on.
    db_url = f"sqlite:///{tmp_path / 'a%40b.db'}"
    result = subprocess.run(
        ["alembic", "current"],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": db_url},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
