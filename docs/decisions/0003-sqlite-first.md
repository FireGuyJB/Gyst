# 0003. SQLite now, PostgreSQL later, via SQLAlchemy + Alembic

- **Status:** Accepted
- **Date:** 2026-11-24

## Context

We need a database for local development now, and a production database when
Gyst is deployed. Switching later shouldn't mean rewriting code.

## Decision

- Use **SQLite** locally (a single file, `backend/gyst.db`, zero setup).
- Access it only through **SQLAlchemy 2** models and sessions.
- Manage all schema changes with **Alembic** migrations.
- Move to **PostgreSQL** at deployment by changing `DATABASE_URL`.

## Alternatives considered

- **Postgres from day one:** most production-like, but needs Docker or a
  local install before writing any code.
- **Raw SQL with no ORM:** fewer concepts, but queries and schema changes
  may not port cleanly between databases, and there's no record of changes.

## Consequences

- Local setup is instant.
- We must avoid SQLite-only behavior. Postgres is stricter, so issues show up
  at migration time; test against Postgres before the first deploy.
