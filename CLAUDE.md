# CLAUDE.md

Rules and context for anyone (Claude or human) working in this repo.

## Project

**Gyst** ("get your stuff together"): users break one primary goal into 8
supporting goals and 64 tasks (a Harada chart), which feed a checklist and a
calendar to build daily routines. See `docs/product/`.

The developer is **new to software engineering and learning as they build**.
Explain *why*, and *how the layers connect*, in PR descriptions and when
asked. Prefer clear, conventional code over clever code.

## Layout

```
frontend/   Next.js (App Router) + React + TypeScript + Tailwind, npm
backend/    FastAPI (app/), SQLAlchemy 2 (app/db.py, app/models.py), Alembic (alembic/), uv, Python 3.12+
docs/       product/ architecture/ decisions/ features/ guides/ specs/ plans/
.github/    CI workflow + PR template
```

## Commands

```bash
# backend (run from backend/)
uv sync
uv run fastapi dev app/main.py          # http://localhost:8000 (/docs for API docs)
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run alembic revision --autogenerate -m "..."   # after changing models
uv run alembic upgrade head

# frontend (run from frontend/)
npm install
npm run dev                             # http://localhost:3000
npm run lint && npm run build
```

## Rules

1. **Read the docs first.** Before changing behavior, read the relevant
   `docs/product/requirements.md` entries, `docs/architecture/`, and the
   feature's spec in `docs/features/`.
2. **Keep the docs in sync, in the same PR.** Requirement status, the
   architecture docs, and the feature spec's status. Significant technical
   choices get an ADR in `docs/decisions/`.
3. **New features follow `docs/features/README.md`:** spec → (ADR) →
   branch → build bottom-up (model + migration → API + tests → UI) → docs → PR.
4. **Never commit to `main`.** Branches: `feature/NNN-name`, `fix/…`,
   `docs/…`, `chore/…`. Commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`,
   `test:`.
5. **Tests:** every backend change gets pytest tests, written first. Run the
   checks above before committing; CI runs the same ones.
6. **Database:** all access goes through SQLAlchemy; all schema changes go
   through Alembic migrations. No SQLite-only features (we're moving to
   Postgres). Never edit a migration already merged to `main`.
7. **Layers:** the frontend talks only to the API, never to the database.
   Business rules (e.g. "8 supporting goals, 8 tasks each") are enforced in
   the API.
8. **Secrets** go in `.env` files (git-ignored). Commit only `.env.example`.
9. **Next.js:** this is a recent Next.js version; check `frontend/AGENTS.md`
   and `frontend/node_modules/next/dist/docs/` before relying on memory.
