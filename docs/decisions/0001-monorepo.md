# 0001. One repo for frontend, backend, and docs

- **Status:** Accepted
- **Date:** 2026-11-24

## Context

Gyst has a Next.js frontend and a Python API. Most features touch both (plus
docs). The team is one developer who is learning.

## Decision

Keep everything in one repository: `frontend/`, `backend/`, `docs/`.

## Alternatives considered

- **Separate repos per app:** cleaner boundaries, but one feature becomes
  two PRs that must be kept in sync. Overkill for one developer.

## Consequences

- One PR can show a feature end to end, which is great for learning how the
  layers connect.
- CI runs both apps' checks; each app keeps its own tooling (npm / uv).
