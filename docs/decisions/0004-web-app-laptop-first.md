# 0004. A website, designed for laptops first and phones second

- **Status:** Accepted
- **Date:** 2026-11-24

## Context

The first Figma screens are iPhone frames. That raised a question: should
Gyst be a website or a native phone app, and which screen size should drive
the layout? The phone frames were a placeholder for early design ideas, not a
decision about the platform.

## Decision

- Gyst is a **website** (Next.js). There is no native iOS or Android app for
  now.
- Design and build for **laptop/desktop screens first**. Pages must still not
  break on a phone, but polishing the phone layout is a later phase.
- Use the Figma phone screens for **content, flow and visual style** (the
  3×3 grids, tile colors, wording), adapted to a wider screen.

## Alternatives considered

- **Native app (e.g. React Native):** the App Store experience, but a second
  frontend codebase and App Store review. Not needed now. If it's ever wanted,
  it can reuse the same Python API and database.
- **Phone-first website:** matches the current Figma frames, but the user's
  priority is laptop use.

## Consequences

- Layouts start from wide screens. Tailwind's responsive prefixes (`sm:`,
  `md:`, `lg:`) make it straightforward to add phone layouts later.
- The Figma file will need laptop-sized frames at some point; until then,
  developers adapt the phone screens.
