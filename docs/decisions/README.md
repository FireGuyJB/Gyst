# Architecture Decision Records (ADRs)

An ADR is a short note about one significant decision: the context, what we
decided, and what it costs us. Future-you (and future collaborators) will ask
"why did we do it this way?" These files answer that.

**When to write one:** choosing a library or framework, a data-modeling
choice, a trade-off you debated, anything you'd want to explain in 6 months.

**How:** copy [`0000-template.md`](0000-template.md) to `NNNN-short-title.md`
(next number), fill it in, and include it in the PR that makes the change.
ADRs aren't edited after they're accepted; if a decision changes, write a new
ADR that *supersedes* the old one.

| # | Decision | Status |
|---|---|---|
| [0001](0001-monorepo.md) | One repo for frontend, backend, and docs | Accepted |
| [0002](0002-fastapi-backend.md) | FastAPI for the Python API | Accepted |
| [0003](0003-sqlite-first.md) | SQLite now, PostgreSQL later, via SQLAlchemy + Alembic | Accepted |
| [0004](0004-web-app-laptop-first.md) | A website, designed for laptops first and phones second | Accepted |
| [0005](0005-client-side-api-calls.md) | The browser calls the API directly (client-side fetch) | Accepted |
| [0006](0006-weekly-tasks-scheduled-live.md) | Weekly tasks are scheduled live, not stored | Accepted |
