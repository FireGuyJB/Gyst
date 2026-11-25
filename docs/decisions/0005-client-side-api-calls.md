# 0005. The browser calls the API directly (client-side fetch)

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

Next.js offers several ways for a page to get data. It can call the API from
the browser, or from the Next.js server (in server components or route
handlers) and then send the result to the browser. Feature 001 was the first
time the frontend talked to the API, so we had to pick one. The developer is
learning, so being able to see every request matters more than performance
right now.

## Decision

Pages call the FastAPI backend **straight from the browser**, using `fetch()`
through the typed helpers in `frontend/src/lib/api.ts`. Pages that load data
are client components (`"use client"`). The API allows the frontend's origin
via CORS (the `cors_origins` setting in `backend/app/config.py`).

## Alternatives considered

- **Server components fetch from the API:** faster first paint, and the API
  could stay private. But those requests run on the Next.js server and don't
  show up in the browser's DevTools, and it means two places where requests
  happen.
- **Next.js route handlers as a proxy (browser → Next.js → FastAPI):** this
  avoids CORS, but adds a middle layer that every request passes through and
  that has to be kept in sync with the API.

## Consequences

- Every request is visible in DevTools → Network, so there's one obvious path
  to trace.
- The API must be reachable from the browser, and CORS has to list every
  frontend origin. In production that means setting `CORS_ORIGINS`.
- Pages show a loading state on first render instead of arriving with data
  already filled in.
- **Revisit when auth arrives:** login tokens and cookies may make a
  server-side or proxy approach the better choice.
