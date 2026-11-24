# Database layer

## The pieces

| Piece | What it is | Analogy |
|---|---|---|
| **SQLite / PostgreSQL** | The database itself, where rows are stored | The filing cabinet |
| **SQLAlchemy** | Python library: define tables as classes; read/write with Python instead of raw SQL | A translator between Python and SQL |
| **Alembic** | Tracks changes to the database's *structure* as migration files | Git, but for the shape of your database |

Files:

- `backend/app/config.py`: `DATABASE_URL` (default: `backend/gyst.db`, the same file whichever folder you run from)
- `backend/app/db.py`: `engine`, `SessionLocal`, `Base`, `get_db()`
- `backend/app/models.py`: table classes (empty for now)
- `backend/alembic/versions/`: migration files (none yet)

## Adding or changing a table (the workflow)

```bash
cd backend
# 1. Edit app/models.py, e.g. add a Goal class
# 2. Let Alembic compare your models to the database and write a migration:
uv run alembic revision --autogenerate -m "add goals table"
# 3. READ the generated file in alembic/versions/ (autogenerate isn't perfect)
# 4. Apply it to your local database:
uv run alembic upgrade head
# 5. Commit the model change AND the migration file together.
```

Other useful commands:

```bash
uv run alembic current     # which migration is the database on?
uv run alembic history     # list all migrations
uv run alembic downgrade -1  # undo the last migration (local only!)
```

Rule: **never edit a migration that's already merged to `main`.** Write a new
one instead: other databases may already have run the old one.

## Moving to PostgreSQL later

1. Add a Postgres driver: `uv add "psycopg[binary]"`.
2. Set `DATABASE_URL=postgresql+psycopg://user:password@host:5432/gyst`.
3. Run `uv run alembic upgrade head` against the new database.

That's it, *as long as* we avoid SQLite-only tricks in models and queries.
Postgres is stricter (e.g. about string lengths and types); if something
SQLite allowed fails on Postgres, fix the model, not the database.

Why SQLite first: see [ADR 0003](../decisions/0003-sqlite-first.md).
