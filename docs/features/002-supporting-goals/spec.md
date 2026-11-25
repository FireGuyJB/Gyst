# 002. Supporting goals: the 3×3 grid

- **Status:** Draft (awaiting approval)
- **Requirements:** R1.2, R1.4 (first level), R1.5 (for supporting goals), R1.6
- **Branch / PR:** `feature/002-supporting-goals` / #? (branched from 001 while PR #2 is open)

## Problem

A user can save a primary goal, but can't break it down. The Harada method
needs 8 supporting goals around each primary goal: the pillars that make it
happen. Feature 003 hangs tasks off these, so they come first.

## User stories

- As a user, I click one of my primary goals and see it in the center of a
  3×3 grid, with 8 slots around it.
- As a user, I click an empty slot, type a supporting goal, and save it, right
  on the tile.
- As a user, I can fill the slots in any order and come back later. A partly
  filled grid is fine.
- As a user, I can rename or clear a supporting goal.
- As a user, each supporting goal has its own color, and it keeps that color.

## Acceptance criteria

- [ ] Clicking a goal tile on the home page opens `/goals/{id}`.
- [ ] That page shows a 3×3 grid: the yellow primary goal in the center and 8
      slots around it, each in its slot's color. Empty slots show a white **+**.
- [ ] Clicking a slot turns it into a text box. Enter (or clicking away) saves;
      Escape cancels. A saved slot shows its title.
- [ ] Clicking a filled slot edits its title. Saving a blank title is rejected
      with a readable message. A separate "clear" control on the tile empties
      the slot (with a confirm step).
- [ ] The API stores at most 8 supporting goals per primary goal, one per
      position 0–7. Positions outside 0–7 are rejected (`422`).
- [ ] Titles are trimmed and limited to 1–200 characters, like primary goals.
- [ ] An unknown goal id returns `404`, and the page shows "Goal not found"
      with a link home.
- [ ] Everything survives a refresh and a restart.
- [ ] Backend tests cover: get a goal with its supporting goals, set a slot,
      overwrite a slot, clear a slot, bad position, blank title, unknown goal.
- [ ] CI is green and the docs are updated.

## How the layers connect

| Layer | Change |
|---|---|
| **Database** | New `SupportingGoal` model: `id` (PK), `goal_id` (FK → `goals.id`), `position` (int, 0–7), `title` (`String(200)`), `created_at`. A **unique constraint on (`goal_id`, `position`)**, so a slot can never hold two goals, plus a **check constraint `position BETWEEN 0 AND 7`**. `Goal.supporting_goals` relationship with `cascade="all, delete-orphan"` (handled by SQLAlchemy, so it works the same on SQLite and Postgres). One migration: `add supporting goals table`. |
| **API** | `GET /goals/{goal_id}` returns the goal with its `supporting_goals` (a list ordered by position; empty slots are simply missing). `PUT /goals/{goal_id}/supporting-goals/{position}` with `{"title": ...}` creates or replaces the slot (`200` with the supporting goal). `DELETE /goals/{goal_id}/supporting-goals/{position}` clears it (`204`; clearing an empty slot is also `204`). `position` is validated as 0–7 in the path. Unknown goal → `404`. |
| **Frontend** | Home-page goal tiles become links to `/goals/[id]`. New page `src/app/goals/[id]/page.tsx` (client component, like the home page) with a `GoalGrid` of 9 tiles. `src/lib/api.ts` gains `getGoal(id)`, `setSupportingGoal(goalId, position, title)` and `clearSupportingGoal(goalId, position)`. Slot colors come from a fixed list in `src/lib/colors.ts`, indexed by position. |

### Why "slots by position" (the API shape)

We considered three ways for the API to treat supporting goals:

- **Slots, `PUT` by position (chosen).** The grid *is* 8 fixed slots, so the
  API mirrors it. "Max 8" is enforced by the position range and the unique
  constraint, not by counting. `PUT` is safe to repeat: saving the same slot
  twice gives the same result.
- **Classic `POST` / `PATCH` / `DELETE` by id:** more conventional, but the
  API would have to count rows and find free positions, and the frontend
  would juggle ids *and* positions.
- **Save the whole grid at once (`PUT` all 8):** simple, but one edit sends
  everything, and two tabs could overwrite each other's work.

### Grid layout and colors (my call)

Positions run clockwise from the top-left. The center is the primary goal:

```
┌───────┬───────┬───────┐
│ 0     │ 1     │ 2     │   0 rose    1 mint    2 blue
│ rose  │ mint  │ blue  │   3 peach   4 taupe   5 indigo
├───────┼───────┼───────┤   6 pink    7 sage
│ 7     │ GOAL  │ 3     │
│ sage  │yellow │ peach │   Color follows the slot, so a supporting
├───────┼───────┼───────┤   goal keeps its color everywhere (tasks,
│ 6     │ 5     │ 4     │   checklist) without storing it.
│ pink  │indigo │ taupe │
└───────┴───────┴───────┘
```

Exact shades come from Figma (`CreationMid9Light`) when building. If users
can pick colors later, that becomes a new column then.

### One request, end to end

1. On `/goals/1` you click the top-left **+**, type "Build endurance" and
   press Enter.
2. `setSupportingGoal(1, 0, "Build endurance")` sends
   `PUT /goals/1/supporting-goals/0`.
3. FastAPI checks that `position` is 0–7 and validates the title, loads goal 1
   (or returns `404`), then finds the slot-0 row and updates it, or adds a new
   one. Commit.
4. `200` + the supporting goal as JSON comes back. React puts it in slot 0.

## Out of scope

- Tasks, and clicking into a supporting goal (feature 003). In 002, clicking a
  filled tile edits its title.
- Editing or deleting the primary goal itself.
- Reordering or dragging slots, and picking custom colors.
- Dark mode, and the exact Figma styling.

## Docs to update

- `docs/product/requirements.md`: R1.2, R1.6 → `in progress`/`done`; R1.4 and R1.5 → `in progress`.
- `docs/architecture/database.md`: add the `supporting_goals` table.
- `docs/architecture/overview.md`: "Current state".
- This spec → `Done`; feature index row.

## Open questions

- None blocking.
