# 003. Tasks: creation and scheduling

- **Status:** Draft (approved 2026-11-25)
- **Requirements:** R1.3, R1.5 (for tasks), R2.2 (routines), R3.1 (in part)
- **Branch / PR:** `feature/003-tasks` / #?

## Problem

Each supporting goal needs 8 tasks, and the tasks feed the daily checklist.
So unlike a paper Harada chart, a task needs to know **how long it takes**
and **when it happens**. Setting up 64 of them must still be quick.

## Decided with the user (2026-11-25)

- **The task grid:** clicking a supporting goal opens its own 3×3 grid: the
  supporting goal in the center (in its color), 8 task slots around it. This
  reuses 002's grid.
- **Editing in a side panel**, not a pop-up, so the grid stays visible:

  ```
  ┌──────── 3×3 tasks ────────┐  ┌──── Task ──────────────────┐
  │ [Run 5k] [ + ]   [ + ]    │  │ Title     [Run 5k        ] │
  │ [ + ]  (Endurance) [ + ]  │  │ Duration  (5)(15)(30)(60)  │
  │ [ + ]    [ + ]   [ + ]    │  │ How often (Daily)(Days)    │
  └───────────────────────────┘  │           (×/week)(×/day)  │
                                 │ Days      M T W T F S S    │
                                 │ Notes     [optional...]    │
                                 └────────────────────────────┘
  ```

- **Low friction:** only a short **title** and **how often** are needed. The
  duration starts at 15 min (quick picks 5 / 15 / 30 / 60, or custom). The
  description is optional.
- **Four frequency kinds:**

  | Kind | Example | Scheduled on |
  |---|---|---|
  | **Every day** | Stretch | All 7 days |
  | **Specific days** | Gym M W F | The days the user ticks |
  | **X times per week** | Long run 2× | Days **Gyst picks**: the least busy ones (see below) |
  | **X times per day** | Drink water 8× | Every day. The checklist shows a counter (3/8) |

- **Auto-placing "X times per week":** add up the minutes already scheduled
  on each weekday (across all the user's tasks), and put the task on the X
  days with the least work.
- **One-off tasks** ("buy running shoes") are not part of the chart. They're
  added straight into the daily checklist and show every day until they're
  done. That belongs to the checklist feature, not 003.

## Scheduling rules (proposed by Claude, accepted with the spec)

- **A day's load** = for each task on that day, duration × times that day.
  So "Drink water, 1 min, 8×/day" adds 8 minutes to every day.
- **Days rebalance as the schedule changes (decided).** The user chose this
  so that new routines (and, later, one-off tasks) spread the load. So the
  days are **not stored**. The API works them out from the current tasks
  every time it returns them, and the panel shows the result ("This week:
  Tue, Thu"). The user doesn't pick days for a weekly task; if they want
  fixed days, they choose "specific days" instead.
- **Placement runs on the server** (it's a business rule), in
  `backend/app/scheduling.py`, as a pure function that's easy to test.
- **Order:** fixed tasks (every day, specific days, × per day) count first.
  Then the weekly tasks are placed one by one, longest first (then by id),
  each onto its X lightest days.
- **Ties:** among equally light days, prefer ones furthest from days already
  picked, then the earliest. So 2× on an empty week gives Mon + Thu, not
  Mon + Tue.
- **Limits:** "× per week" is 1–6 (7 is "every day"). "× per day" is 2–20.
  Duration is 1–480 minutes.
- **Storage:** structured columns, not free text: `frequency`
  (`daily` / `days` / `weekly` / `per_day`), `weekdays` (a JSON list of
  0–6, Monday = 0, only for `days`), `times_per_week`, `times_per_day`,
  `duration_minutes`, `description`.

## How the layers connect

| Layer | Change |
|---|---|
| **Database** | `Task` model: `id`, `supporting_goal_id` (FK), `position` 0–7 (unique per supporting goal, same as 002), `title` (200), `description` (up to 2000, default empty), `duration_minutes`, `frequency`, `weekdays` (JSON), `times_per_week`, `times_per_day`, `created_at`. Deleting a supporting goal deletes its tasks. |
| **API** | `GET /supporting-goals/{id}` returns the supporting goal (with its goal id, title and position) and its tasks. `PUT` / `DELETE /supporting-goals/{id}/tasks/{position}` set and clear a slot, like 002. Each task in a response includes `scheduled_days`: the weekdays it lands on this week. |
| **Frontend** | `/supporting-goals/[id]`: the same 3×3 grid, the supporting goal in the center, and a side panel to create or edit a task. On the goal grid, clicking a filled supporting goal now opens its task grid; renaming moves to a small "edit" button on the tile. |

## Later: the checklist

Because days are worked out live, adding a task mid-week can move a weekly
task to a different day. When the checklist arrives, days that have already
passed (and ticks already made) must not move.

## Open questions

1. ~~Fixed or rebalanced?~~ Rebalanced (decided 2026-11-25).
2. A specific time of day (morning/evening) or a start date: later, with
   the calendar (R3)?
