# 001. Walking skeleton: connect frontend → API → database

- **Status:** Done
- **Requirements:** R1.1 (partially: a primary goal with a title only)
- **Branch / PR:** `feature/001-walking-skeleton` / PR #2

## Problem

PR #1 set up three layers that don't talk to each other yet. Before building
real Gyst features, we want **one thin, real path through every layer**. That
way the developer can see, run and trace exactly how a click in the browser
turns into a row in the database and back. Every later feature reuses this
path.

## User stories

- As a user, I can type a **primary goal** (just a title) and save it.
- As a user, I can see the goals I've saved, and they're still there after I
  refresh the page or restart the apps.

## Acceptance criteria

- [x] With both apps running, the home page lists saved goals, newest first.
- [x] Submitting the form saves a goal, and it appears in the list without a
      full page reload.
- [x] A blank title (or only spaces) is rejected. The API returns `422` and the
      page shows a readable message.
- [x] Titles are trimmed and limited to 1–200 characters.
- [x] If the API isn't running, the page shows "Can't reach the Gyst API"
      instead of crashing.
- [x] Goals survive restarting both apps (they're stored in `backend/gyst.db`).
- [x] Backend tests cover listing, creating and validation, and run against a
      separate temporary database, never `gyst.db`.
- [x] CI is green, and the docs are updated (see "Docs to update").

## How the layers connect

| Layer | Change |
|---|---|
| **Database** | New `Goal` model in `backend/app/models.py`: `id` (int, PK), `title` (`String(200)`, not null), `created_at` (timestamp, set by the server). One Alembic migration: `add goals table`. |
| **API** | `backend/app/schemas.py`: `GoalCreate` (`title`: trimmed, 1–200 chars) and `GoalRead` (`id`, `title`, `created_at`). `backend/app/routers/goals.py`: `GET /goals` (list, newest first) and `POST /goals` (create; returns `201` and the `GoalRead`). Add CORS to `main.py`, allowing origins from a new `cors_origins` setting (default `["http://localhost:3000"]`). |
| **Frontend** | `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) in `frontend/.env.example`. `src/lib/api.ts`: typed `listGoals()` and `createGoal(title)`. The home page becomes a client component with a goal form and a list, plus loading, error and empty states. **Layout loosely follows Figma `CreationHome`** ([designs.md](../../product/designs.md)), adapted for a **laptop screen** ([ADR 0004](../../decisions/0004-web-app-laptop-first.md)): the GYST header, "+ add primary goal", and goals shown as yellow rounded tiles. Pixel-perfect styling, dark mode and the 3×3 grids are out of scope. |

### One request, end to end (the thing to learn)

1. You type "Run a marathon" and click **Save** (`src/app/page.tsx`).
2. `createGoal()` in `src/lib/api.ts` sends `POST http://localhost:8000/goals`
   with `{"title": "Run a marathon"}`. **You can watch this request in the
   browser's DevTools → Network tab.**
3. The browser first checks CORS: the API says "requests from
   localhost:3000 are allowed."
4. FastAPI routes the request to `create_goal()` in `routers/goals.py`, and
   validates the body against `GoalCreate`. A bad title stops here with `422`.
5. `create_goal()` gets a database session via `Depends(get_db)`, adds a
   `Goal` and commits. SQLAlchemy runs `INSERT INTO goals ...` on SQLite.
6. The API returns `201` with the new goal as JSON. React adds it to the
   list.

## Decisions to record

- **ADR 0005: the browser calls the API directly (client-side fetch).** We
  don't route through Next.js server components or route handlers. That way
  every request is visible in DevTools, and there's one obvious path, which
  serves the learning goal. Revisit when auth arrives.

## Build order (bottom-up, test-first)

1. Model + migration → `alembic upgrade head` → inspect the table.
2. Test fixture: a temporary SQLite database plus a `get_db` override. Then
   tests for `GET /goals` and `POST /goals` (valid, blank, too long, trimmed),
   written failing first.
3. Schemas + router + CORS until the tests pass.
4. Frontend API helper → page (list → form → error states).
5. Manual end-to-end check: run both apps, add a goal, refresh, restart.

## Docs to update

- `docs/architecture/overview.md`: "Current state" (the layers are now
  connected); point "Life of a request" at the real files.
- `docs/product/requirements.md`: R1.1 → `in progress`.
- `docs/guides/getting-started.md`: run both apps together;
  `frontend/.env.example`; a "trace a request" exercise using DevTools and
  `/docs`.
- `docs/decisions/0005-client-side-api-calls.md`, plus the ADR index.
- `docs/features/README.md`: feature index row; this spec's status → `Done`.

## Out of scope

- Supporting goals and tasks (the 8 × 8 structure). That's feature 002.
- Editing or deleting goals, accounts/auth, the checklist, the calendar.
- Pixel-perfect Figma styling, dark mode, and the 3×3 drill-down grids.
- Frontend unit tests or end-to-end browser tests (worth an ADR in a later
  PR).

## Open questions

- None that block this PR. The Figma link is still needed before feature 002's UI.
