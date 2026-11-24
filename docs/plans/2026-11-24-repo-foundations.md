# Repo Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up Gyst's monorepo foundations (empty frontend and backend apps,
project rules, docs structure, CI) and open PR #1.

**Architecture:** Monorepo with `frontend/` (Next.js), `backend/` (FastAPI +
SQLAlchemy/Alembic, no tables yet) and `docs/`. The two apps are not connected
yet. CI runs each app's checks independently.

**Tech Stack:** Next.js (App Router, TypeScript, Tailwind, ESLint, npm),
Python 3.12 via uv, FastAPI, SQLAlchemy 2, Alembic, pydantic-settings, ruff,
pytest, GitHub Actions.

**Spec:** `docs/specs/2026-11-24-repo-foundations-design.md`

## Global Constraints

- No product features, data models, or frontend→API calls in this PR.
- Python `>=3.12`, managed by `uv`. JS package manager: npm.
- `DATABASE_URL` default: `sqlite:///./gyst.db`. The `*.db` files are git-ignored.
- All work goes on branch `chore/repo-foundations`; never commit to `main`.
- Docs explain *why* and *how layers connect*, in plain language for a beginner.

## Review Focus

- A fresh clone following `docs/guides/getting-started.md` must run both apps;
  verify the commands in the guide by actually running them.
- CI must pass on the first push; run each CI command locally before pushing.
- `.gitignore` must keep `node_modules/`, `.venv/`, `.next/`, `*.db`, `.env`
  out of git; check `git status` before the commit.
- Alembic must be wired to `app.db.Base.metadata` and `settings.database_url`,
  so that PR #2's `alembic revision --autogenerate` works; verify with
  `uv run alembic current` (exits 0).
- The backend test must not create a stray `gyst.db` in the repo root.

---

### Task 1: Machine tooling + branch

- [ ] Run `brew install node gh uv`. Verify that `node -v`, `npm -v`, `gh --version` and `uv --version` all print versions.
- [ ] Ask the user to run `! gh auth login` (interactive). Verify that `gh auth status` shows logged in.
- [ ] Run `git checkout -b chore/repo-foundations`.

### Task 2: Root files

**Files:** Create `.gitignore`, `.editorconfig`. Modify `README.md`.

- [ ] Add a `.gitignore` covering Node (`node_modules/`, `.next/`, `out/`), Python (`.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`), `*.db`, `.env*` (except `.env.example`), and `.DS_Store`.
- [ ] Add an `.editorconfig`: utf-8, lf, final newline, 2-space indent, 4-space indent for `*.py`.
- [ ] Update the README: a one-paragraph pitch (the Harada goal → 8 → 64 model), the repo layout, a quick start pointing to `docs/guides/getting-started.md`, and a link to `docs/README.md`.
- [ ] Commit: `chore: add root config and README`.

### Task 3: Backend shell

**Files:** Create `backend/pyproject.toml`, `backend/.python-version`,
`backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`,
`backend/app/db.py`, `backend/alembic.ini`, `backend/alembic/env.py` (+ the
Alembic scaffold), `backend/tests/test_health.py`, `backend/.env.example`.

**Interfaces (Produces):**
- `app.config.settings: Settings` with `database_url: str` (env `DATABASE_URL`)
- `app.db.Base` (SQLAlchemy `DeclarativeBase`), `app.db.engine`, `app.db.SessionLocal`, `app.db.get_db() -> Iterator[Session]`
- `app.main.app: FastAPI`; `GET /health` → `200 {"status": "ok"}`

- [ ] Run `cd backend && uv init --app --python 3.12 --name gyst-backend`, then remove the generated `main.py`. Add deps with `uv add fastapi "uvicorn[standard]" sqlalchemy alembic pydantic-settings` and dev deps with `uv add --dev pytest httpx ruff`.
- [ ] Write the failing test `tests/test_health.py::test_health_returns_ok`: use `TestClient(app).get("/health")`, then assert `status_code == 200` and `json() == {"status": "ok"}`.
- [ ] Run `uv run pytest` and expect a FAIL (import error).
- [ ] Implement `config.py`, `db.py` and `main.py` per the Interfaces block. `db.py` passes `connect_args={"check_same_thread": False}` only when the URL starts with `sqlite`. Leave the engine lazy (no connection on import). Add short comments explaining each layer's role.
- [ ] Run `uv run pytest` and expect a PASS. Confirm that no `gyst.db` was created.
- [ ] Run `uv run alembic init alembic`. Edit `env.py` to set `sqlalchemy.url` from `settings.database_url` and `target_metadata = Base.metadata`. Run `uv run alembic current`; it should exit 0.
- [ ] Configure ruff in `pyproject.toml` (line-length 100; select `E,F,I,UP,B`). Run `uv run ruff check . && uv run ruff format --check .` and expect it to be clean.
- [ ] Commit: `feat(backend): add FastAPI shell with health check and DB config`.

### Task 4: Frontend shell

**Files:** Create `frontend/` via the generator.

- [ ] Run `npx create-next-app@latest frontend --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-turbopack --yes` (drop any flag the current CLI rejects). Delete `frontend/.git` if the generator created one.
- [ ] Change the page title/metadata to "Gyst" and replace the starter page body with a simple "Gyst — Get your stuff together." heading.
- [ ] Run `npm run lint && npm run build` in `frontend/` and expect both to succeed.
- [ ] Commit: `feat(frontend): add Next.js shell`.

### Task 5: Docs structure

**Files:** Create every `docs/` file listed in the spec's layout (plus this
`docs/plans/` folder, which `docs/README.md` mentions).

- [ ] `docs/README.md`: a map of each folder and when to use it.
- [ ] `product/vision.md` and `product/requirements.md`. The requirements cover the primary goal → 8 supporting goals → 64 tasks; the checklist; the calendar/routines; and open questions (Figma link TBD, auth, recurring tasks).
- [ ] `architecture/overview.md`: a Mermaid diagram of Browser → Next.js → FastAPI → SQLAlchemy → SQLite, plus the life of a future request, step by step. `architecture/database.md`: SQLAlchemy vs. Alembic, the migration workflow commands, and the switch to Postgres.
- [ ] `decisions/README.md`, `0000-template.md` (Context / Decision / Consequences), `0001-monorepo.md`, `0002-fastapi-backend.md`, `0003-sqlite-first.md`.
- [ ] `features/README.md`: the 6-step workflow from the spec. `features/_template/spec.md`: Problem, User stories, Acceptance criteria, How the layers connect (DB / API / UI), Open questions, Status.
- [ ] `guides/getting-started.md`: the tool installs, running the backend (`uv sync`, `uv run fastapi dev app/main.py` → http://localhost:8000/docs), running the frontend (`npm install`, `npm run dev` → http://localhost:3000), and running the checks. `guides/development-workflow.md`: branch naming, commit style (`feat:`, `fix:`, `docs:`, `chore:`), and the PR flow.
- [ ] Update the spec's Status to "Approved".
- [ ] Commit: `docs: add docs structure, requirements, ADRs and guides`.

### Task 6: CLAUDE.md, PR template, CI

**Files:** Create `CLAUDE.md`, `.github/pull_request_template.md`,
`.github/workflows/ci.yml`.

- [ ] `CLAUDE.md`: the project summary, the layout, the commands (from the guides), and the rules from the spec's "CLAUDE.md rules" section.
- [ ] PR template sections: What & why, How the layers connect, Docs updated (checkbox), How I tested.
- [ ] `ci.yml`: runs on `pull_request` and on `push` to `main`. Job `backend`: `astral-sh/setup-uv`, `uv sync`, `ruff check`, `ruff format --check`, `pytest` (working-directory `backend`). Job `frontend`: `actions/setup-node` (node 22, npm cache on `frontend/package-lock.json`), `npm ci`, `npm run lint`, `npm run build`.
- [ ] Commit: `chore: add CLAUDE.md, PR template and CI`.

### Task 7: Verify + open PR

- [ ] From a clean state, run every command in `getting-started.md`. Both apps should start, `/health` should return ok, and all checks should pass. Run `git status` and confirm no ignored artifacts are tracked.
- [ ] `git push -u origin chore/repo-foundations`. Then run `gh pr create` with a body that explains each folder and what's next (PR #2: the walking skeleton).
- [ ] Watch CI with `gh pr checks --watch` and confirm it's green.
