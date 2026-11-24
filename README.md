# Gyst

**Get your stuff together.**

Gyst helps you turn one big goal into a daily routine. Inspired by the
[Harada method](https://en.wikipedia.org/wiki/Harada_method), you break a
**primary goal** into **8 supporting goals**, and each supporting goal into
**8 tasks**, for **64 tasks** in total. Those tasks feed a **checklist** and a
**calendar**, so you always know what to do today to move toward the big goal.

> Status: early development. The repo foundations are in place; features come next.

## Repo layout

```
frontend/   Next.js + React + TypeScript (the UI you see in the browser)
backend/    Python + FastAPI (the API) + SQLAlchemy/Alembic (the database layer)
docs/       Product requirements, architecture, decisions, feature specs, guides
.github/    CI checks and the pull request template
CLAUDE.md   Rules for anyone (human or AI) working in this repo
```

## Quick start

See **[docs/guides/getting-started.md](docs/guides/getting-started.md)** for
full setup. The short version:

```bash
# Backend: http://localhost:8000/docs
cd backend && uv sync && uv run fastapi dev app/main.py

# Frontend: http://localhost:3000  (in a second terminal)
cd frontend && npm install && npm run dev
```

## Documentation

Start at **[docs/README.md](docs/README.md)**.
