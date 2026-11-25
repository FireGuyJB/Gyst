# 003. Tasks: creation and scheduling

- **Status:** Draft (decisions captured; finish after 002)
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

## Proposed (not yet confirmed)

- **A day's load** = for each task on that day, duration × times that day.
  So "Drink water, 1 min, 8×/day" adds 8 minutes to every day.
- **Placement runs on the server** when a weekly task is saved, or when its
  count or duration changes. The result is stored as normal weekdays and
  shown in the panel ("Gyst picked Tue + Thu"). The user can change them.
- **Placed days stay put** when other tasks change later, so routines don't
  jump around. (Open question 1.)
- **Ties:** among equally light days, prefer ones furthest from days already
  picked, then the earliest. So 2× on an empty week gives Mon + Thu, not
  Mon + Tue.
- **Limits:** "× per week" is 1–6 (7 is "every day"). "× per day" is 2–20.
  Duration is 1–480 minutes.
- **Storage:** structured columns, not free text: `frequency_kind`,
  `weekdays` (7 on/off flags), `times_per_week`, `times_per_day`,
  `duration_minutes`. The checklist can then query them directly.

## Open questions

1. Should auto-placed days stay fixed (proposed), or be re-balanced each
   week as the schedule changes?
2. A specific time of day (morning/evening) or a start date: later, with
   the calendar (R3)?
