# Supporting goals (002) and tasks (003) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Primary goal → 3×3 grid of 8 supporting goals → 3×3 grid of 8 tasks, each task with a duration, description and frequency, and weekly tasks auto-placed on the least busy days.

**Architecture:** Same path as feature 001: SQLAlchemy model + Alembic migration → FastAPI router + Pydantic schemas (tested first) → client-component page calling `src/lib/api.ts`. Slots are addressed by position (0–7) under their parent. Scheduling is a pure function in `backend/app/scheduling.py`.

**Tech Stack:** FastAPI, SQLAlchemy 2, Alembic, pytest; Next.js 16 (App Router, `cacheComponents` on), React 19, Tailwind.

**Spec:** `docs/features/002-supporting-goals/spec.md`, `docs/features/003-tasks/spec.md`

## Global Constraints

- Titles: trimmed, 1–200 chars (reuse `GoalTitle`). Task description: ≤ 2000 chars, default `""`.
- Positions 0–7, clockwise from top-left; colors by position: rose, mint, blue, peach, taupe, indigo, pink, sage. Primary goal yellow.
- Duration 1–480 min (default 15 in the UI). `times_per_week` 1–6. `times_per_day` 2–20. Weekdays 0–6, Monday = 0.
- No SQLite-only features. Cascades via SQLAlchemy `cascade="all, delete-orphan"`.
- Pages that read URL params wrap them in `<Suspense>` (`cacheComponents`).
- Two PRs: 002 on `feature/002-supporting-goals` (base: `feature/001-walking-skeleton`), 003 on `feature/003-tasks` (base: 002).

## Review Focus

- `PUT` to a slot that already has a goal → replaces the title and keeps the same id (tasks under it survive a rename). Test: `test_overwrite_keeps_id`.
- Clearing a supporting goal that has tasks → its tasks are deleted too. Test: `test_clear_supporting_goal_deletes_its_tasks`.
- Task `frequency="days"` with an empty or duplicate weekday list → `422`; extra fields for other kinds are dropped. Tests in `test_tasks.py`.
- Non-numeric or unknown ids in the URL → `404`/`422`, and the page shows "not found" instead of crashing.
- Scheduling with more weekly occurrences than free days, or all days equal → still deterministic. Tests in `test_scheduling.py`.

---

## Feature 002

### Task 1: SupportingGoal model + migration

**Files:** Modify `backend/app/models.py`; create a migration via autogenerate.

**Produces:** `SupportingGoal(id, goal_id, position, title, created_at)`, `Goal.supporting_goals` (ordered by position), `SupportingGoal.goal`. `UniqueConstraint("goal_id", "position")`, `CheckConstraint("position BETWEEN 0 AND 7", name="position_range")`.

- [ ] Add the model; `uv run alembic revision --autogenerate -m "add supporting goals table"`; read it; `uv run alembic upgrade head`.
- [ ] Commit `feat: add SupportingGoal model and migration`.

### Task 2: API for the goal grid

**Files:** `backend/app/schemas.py`, `backend/app/routers/goals.py`, test `backend/tests/test_supporting_goals.py`.

**Produces:**
- `SupportingGoalSet {title: GoalTitle}`, `SupportingGoalRead {id, goal_id, position, title}`, `GoalDetail(GoalRead) + supporting_goals: list[SupportingGoalRead]`.
- `GET /goals/{goal_id}` → `GoalDetail`; `PUT /goals/{goal_id}/supporting-goals/{position}` → `SupportingGoalRead` (200); `DELETE` same path → 204. `position: Annotated[int, Path(ge=0, le=7)]`. Unknown goal → 404 `{"detail": "Goal not found"}`.

- [ ] Tests first: `test_get_goal_with_no_supporting_goals`, `test_get_unknown_goal_is_404`, `test_set_slot_creates_it`, `test_overwrite_keeps_id`, `test_clear_slot`, `test_clear_empty_slot_is_204`, `test_position_out_of_range_is_422` (8 and -1), `test_blank_title_is_422`, `test_set_slot_on_unknown_goal_is_404`, `test_supporting_goals_ordered_by_position`. Run → fail.
- [ ] Implement; run all tests → pass; ruff. Commit `feat: add supporting goal slots API`.

### Task 3: Goal grid page

**Files:** `frontend/src/lib/api.ts`, create `frontend/src/lib/colors.ts`, `frontend/src/components/Grid.tsx`, `frontend/src/components/SlotTile.tsx`, `frontend/src/app/goals/[id]/page.tsx`; modify `frontend/src/app/page.tsx` (tiles become `<Link href={`/goals/${id}`}>`).

**Produces:**
- `api.ts`: types `SupportingGoal`, `GoalDetail`; `getGoal(id)`, `setSupportingGoal(goalId, position, title)`, `clearSupportingGoal(goalId, position)`; `request()` handles 204 (no JSON).
- `colors.ts`: `PRIMARY_COLOR`, `SLOT_COLORS: string[8]` (Tailwind classes).
- `Grid({center, slots})`: lays out 8 slot nodes clockwise around the center (grid cells map `[0,1,2,7,C,3,6,5,4]`).
- `SlotTile({color, title, onSave, onClear, onOpen?})`: empty shows "+"; click → inline input (Enter/blur saves, Esc cancels); filled shows title, edit and clear (confirm) buttons; `onOpen` (used in 003) makes the body a link/button.

- [ ] Build; `npm run lint && npm run build`; manual run. Commit `feat: goal page with 3x3 supporting goal grid`.

### Task 4: Docs + PR

- [ ] Requirements R1.2 → `done`, R1.6 → `in progress` (tasks colored in 003), R1.4/R1.5 → `in progress`; `database.md` table row; `overview.md` current state; spec → `Done`; feature index.
- [ ] Commit, push, open PR (base `feature/001-walking-skeleton`).

## Feature 003

### Task 5: Scheduling function

**Files:** create `backend/app/scheduling.py`, test `backend/tests/test_scheduling.py`.

**Produces:** `@dataclass(frozen=True) class Occurrence: id: int; frequency: str; duration_minutes: int; weekdays: list[int]; times_per_week: int | None; times_per_day: int | None` and `schedule_week(tasks: Sequence[Occurrence]) -> dict[int, list[int]]` (task id → sorted weekdays).

Algorithm (the tests don't fully determine it):
```
loads = [0]*7
fixed: daily → all days, +duration; days → its weekdays, +duration; per_day → all days, +duration*times
weekly, sorted by (-duration, id): pick times_per_week days one at a time,
  each = min over unchosen days of (loads[d], -gap(d, chosen), d)
  where gap = min circular distance (min(|a-b|, 7-|a-b|)) to chosen days, 7 if none
  then loads[d] += duration
```

- [ ] Tests first: `test_daily_is_every_day`, `test_specific_days_kept`, `test_per_day_is_every_day`, `test_weekly_on_empty_week_spreads_out` (2× → [0, 3]), `test_weekly_avoids_busy_days` (a 60-min M-F task → 2× weekly lands on [5, 6]), `test_per_day_counts_times_in_load`, `test_longer_weekly_task_placed_first`, `test_deterministic_on_ties`. Run → fail; implement → pass. Commit `feat: add weekly scheduling function`.

### Task 6: Task model, migration, API

**Files:** `models.py`, migration `add tasks table`, `schemas.py`, create `backend/app/routers/supporting_goals.py`, register in `main.py`, test `backend/tests/test_tasks.py`.

**Produces:**
- `Task` (columns in the 003 spec); `SupportingGoal.tasks` cascade.
- `TaskSet {title, description="", duration_minutes: 1–480, frequency: Literal["daily","days","weekly","per_day"], weekdays: list[int]=[], times_per_week: int|None, times_per_day: int|None}` with a `model_validator(mode="after")`: `days` needs ≥1 unique weekdays 0–6 (stored sorted); `weekly` needs `times_per_week` 1–6; `per_day` needs `times_per_day` 2–20; fields not used by the kind are reset (`[]`/`None`).
- `TaskRead` = stored fields + `id, supporting_goal_id, position, scheduled_days: list[int]`.
- `SupportingGoalDetail {id, goal_id, goal_title, position, title, tasks: list[TaskRead]}`.
- `GET /supporting-goals/{id}`, `PUT`/`DELETE /supporting-goals/{id}/tasks/{position}`. `scheduled_days` comes from `schedule_week` over **all** tasks in the database.

- [ ] Tests first: `test_get_supporting_goal_with_no_tasks`, `test_unknown_supporting_goal_is_404`, `test_set_daily_task`, `test_set_days_task_sorts_weekdays`, `test_days_task_needs_weekdays`, `test_duplicate_weekdays_is_422`, `test_weekly_needs_times_per_week`, `test_times_per_week_7_is_422`, `test_per_day_range`, `test_duration_range`, `test_unused_fields_are_dropped`, `test_weekly_task_gets_scheduled_days`, `test_weekly_rebalances_when_schedule_changes`, `test_clear_task`, `test_clear_supporting_goal_deletes_its_tasks`. Run → fail; implement → pass. Commit `feat: add tasks API with auto-scheduled weekly tasks`.

### Task 7: Task grid page + side panel

**Files:** `api.ts` (types `Frequency`, `Task`, `TaskInput`, `SupportingGoalDetail`; `getSupportingGoal`, `setTask`, `clearTask`), create `frontend/src/components/TaskPanel.tsx`, `frontend/src/app/supporting-goals/[id]/page.tsx`; goal page passes `onOpen` for filled tiles.

- Task tiles: tinted with the supporting goal's color; show title + a short schedule line ("Every day", "Mon Wed Fri", "2× / week", "8× / day").
- `TaskPanel({task?, position, onSave, onClear, onClose})`: title, duration chips 5/15/30/60 + custom number, frequency chips, weekday toggles M T W T F S S (for `days`), a number for ×/week or ×/day, optional notes. Defaults: 15 min, `daily`. For saved weekly tasks it shows "This week: Tue, Thu". Shows API errors.

- [ ] Build; lint + build; manual run. Commit `feat: task grid page with task side panel`.

### Task 8: Docs + PR

- [ ] Requirements R1.3 → `done`, R1.6 → `done`, R2.2 → `in progress`; `database.md`; `overview.md`; ADR 0006 (weekly tasks are scheduled live, not stored); 003 spec → `Done`; index.
- [ ] Commit, push, open PR (base `feature/002-supporting-goals`).
