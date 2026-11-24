# Design: Repo Foundations (PR #1)

**Date:** 2026-11-24
**Status:** Approved

## Intent

Gyst helps a user break one **primary goal** into **8 supporting goals** and
**64 tasks** (a Harada-chart structure). Those tasks then feed a checklist and
a calendar so the user can build routines. The developer is new to software
engineering and wants to **learn how each layer (frontend → API → database)
connects** while building.

PR #1 sets up the foundations so that every later feature has a clear home, a
clear process, and automated checks. It contains **no product features**.

## Goals

- A repo layout that separates the frontend and the backend.
- An empty Next.js app and an empty FastAPI app that each start up and pass
  their checks.
- Project rules in `CLAUDE.md` so every Claude session follows the same
  conventions.
- A `docs/` structure covering the product vision and requirements,
  architecture, decisions, guides, and a **repeatable workflow for building
  future features**.
- CI (GitHub Actions) that lints and tests both apps on every PR.

## Non-goals

- Gyst features: goal/task data models, the chart UI, the checklist, the
  calendar.
- Connecting the frontend to the API (that is PR #2's "walking skeleton").
- Auth, deployment, and Postgres.
- Implementing the Figma designs (the link will be recorded in the docs when
  it's available).

## Anti-goals

- Heavy process or tooling that a solo beginner won't maintain.
- Docs that explain *what* the code does but not *why*, or *how the layers
  connect*.

## Approaches considered

1. **Foundations + a "hello, every layer" slice.** Teaches the connections
   right away, but more to review in one PR.
2. **Foundations only (chosen).** Small, easy-to-review first PR. The
   connections come in PR #2, where they can be explained on their own.
3. **Foundations + the first real feature.** Too big for a first PR.

## Tooling decisions (Claude's calls; easy to revisit)

| Area | Choice | Why |
|---|---|---|
| Repo layout | Monorepo: `frontend/`, `backend/`, `docs/` | One place, one PR per feature across layers |
| Frontend | Next.js (App Router) + TypeScript + Tailwind + ESLint, via `create-next-app` | Standard, well-documented defaults |
| JS package manager | npm | Ships with Node; fewest tools to learn |
| Python tooling | `uv` (Python 3.12) | Fast; manages the Python version and dependencies together |
| API | FastAPI with a `/health` endpoint only | Modern, typed, generates API docs automatically |
| DB access | SQLAlchemy 2 + Alembic, configured with **no tables** | Swap SQLite → Postgres with a connection-string change |
| Database | SQLite (file is git-ignored) | Zero setup locally |
| Python quality | `ruff` (lint + format), `pytest` | One fast tool for style; standard test runner |
| CI | GitHub Actions: frontend lint/build, backend ruff/pytest | Catches breakage on every PR |
| Machine setup | `brew install node gh uv` | Missing on the dev machine today |

## Repo layout

```
Gyst/
├── CLAUDE.md                  # rules for Claude (and humans) working here
├── README.md                  # what Gyst is + quick start
├── .gitignore  .editorconfig
├── .github/
│   ├── workflows/ci.yml
│   └── pull_request_template.md
├── frontend/                  # Next.js app (default starter page)
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py            # FastAPI app + /health
│   │   ├── config.py          # settings (DATABASE_URL, etc.)
│   │   └── db.py              # SQLAlchemy engine/session + Base
│   ├── alembic/  alembic.ini  # migrations (none yet)
│   └── tests/test_health.py
└── docs/
    ├── README.md              # map of the docs + how to use them
    ├── product/
    │   ├── vision.md          # why Gyst exists, who it's for
    │   └── requirements.md    # Harada model, checklist, calendar (living doc)
    ├── architecture/
    │   ├── overview.md        # the layers and how a request flows through them
    │   └── database.md        # SQLAlchemy/Alembic explained, SQLite → Postgres path
    ├── decisions/             # ADRs: one short file per significant decision
    │   ├── README.md  0000-template.md
    │   ├── 0001-monorepo.md  0002-fastapi-backend.md  0003-sqlite-first.md
    ├── features/
    │   ├── README.md          # the feature workflow (below)
    │   └── _template/spec.md
    ├── guides/
    │   ├── getting-started.md # install tools, run both apps
    │   └── development-workflow.md  # branch → spec → build → test → PR
    └── specs/                 # design docs like this one
```

## Feature workflow (documented in `docs/features/README.md`)

1. **Spec:** copy `_template/` to `docs/features/NNN-short-name/` and fill in
   the problem, the user stories, the acceptance criteria, the layers
   touched, and open questions.
2. **Decide:** record any significant technical choice as an ADR.
3. **Branch:** `feature/NNN-short-name`.
4. **Build layer by layer:** database model + migration → API endpoint +
   tests → frontend UI. Each feature spec has a "how the layers connect"
   section.
5. **Update docs:** requirements, architecture, and the spec's status.
6. **PR:** use the template, and CI must pass.

## CLAUDE.md rules (summary)

- Read `docs/` before changing behavior, and keep the docs in sync in the
  same PR.
- Never commit to `main`; use one branch and one PR per feature.
- Every backend change needs tests; run the checks before committing.
- Explain *why* and *how the layers connect* in PRs, because the developer is
  learning.
- Commands for running, linting, and testing each app.

## Left to the builder

The exact config file contents, the wording of the docs, and the CI job
details.
