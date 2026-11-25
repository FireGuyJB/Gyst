# Architecture overview

Gyst has three layers. Each one has a single job, and each one only talks to
its neighbor.

```mermaid
flowchart LR
    U[You, in a browser] -->|clicks, typing| F

    subgraph F[Frontend: frontend/]
      direction TB
      F1[Next.js + React<br/>pages & components]
    end

    F -->|HTTP request<br/>JSON| A

    subgraph A[API: backend/app/]
      direction TB
      A1[FastAPI route<br/>routers/] --> A2[SQLAlchemy session<br/>db.py]
    end

    A2 -->|SQL| D[(Database<br/>SQLite now,<br/>Postgres later)]
```

| Layer | Folder | Job | Tech |
|---|---|---|---|
| **Frontend** | `frontend/` | Show things and react to the user. Owns *no* permanent data. | Next.js, React, TypeScript, Tailwind |
| **API** | `backend/app/` | The rules: validate input, decide what's allowed, read/write data. | Python, FastAPI |
| **Data access** | `backend/app/db.py`, `models.py` | Translate Python objects ↔ database rows. | SQLAlchemy, Alembic |
| **Database** | `backend/gyst.db` (local) | Store data permanently. | SQLite → PostgreSQL |

## Why separate layers?

- **The frontend can't talk to the database directly.** The API is the
  gatekeeper, so rules (e.g. "a supporting goal has at most 8 tasks") live in
  one place and can't be bypassed.
- **Each layer can change on its own.** Swapping SQLite for Postgres touches
  only the data layer; redesigning a page touches only the frontend.

## Life of a request (a real one: saving a goal)

You type "Run a marathon" on the home page and click **Save**. You can watch
steps 2–6 in the browser's DevTools → Network tab.

1. **Browser → Frontend.** `frontend/src/app/page.tsx` handles the form
   submit and calls `createGoal()`.
2. **Frontend → API.** `createGoal()` in `frontend/src/lib/api.ts` sends
   `POST http://localhost:8000/goals` with JSON `{"title": "Run a marathon"}`.
   The browser calls the API directly ([ADR 0005](../decisions/0005-client-side-api-calls.md)).
3. **CORS check.** Because the frontend (port 3000) and API (port 8000) are
   different origins, the browser first asks the API whether it allows this.
   `CORSMiddleware` in `backend/app/main.py` says yes for the origins in the
   `cors_origins` setting.
4. **API route.** FastAPI matches the URL to `create_goal()` in
   `backend/app/routers/goals.py` and validates the JSON against `GoalCreate`
   in `backend/app/schemas.py`. A blank or too-long title stops here with
   `422`, before our code runs.
5. **API → Database.** `create_goal()` gets a session via `DbSession`
   (`Depends(get_db)` in `backend/app/db.py`), adds a `Goal`
   (`backend/app/models.py`) and commits. SQLAlchemy writes the SQL
   (`INSERT INTO goals ...`).
6. **Back up the chain.** The API returns `201` with the goal as JSON (shaped
   by `GoalRead`). React adds it to the list on screen.

Every feature follows this same path, built **bottom-up**: model + migration
→ API route + tests → UI. See [features/README.md](../features/README.md).

## Current state

- The three layers are **connected** (feature [001](../features/001-walking-skeleton/spec.md)).
- API routes: `GET /health`, `GET /goals` (newest first), `POST /goals`.
- One table: `goals` (see [database.md](database.md)).
- The home page lists and creates primary goals (title only). Supporting
  goals and tasks come in feature 002.

See also: [database.md](database.md).
