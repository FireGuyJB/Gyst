# 0006. Weekly tasks are scheduled live, not stored

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

A task can be "X times per week" without fixed days. The user wants Gyst to
put those on the days with the least work: add up the minutes already on
each weekday, and pick the lightest ones. The user also wants the days to
**rebalance as the schedule changes**: when they add a routine (or, later, a
one-off task), the flexible tasks should move off the day that got busier.

## Decision

- The days for weekly tasks are **not stored**. `backend/app/scheduling.py`
  has one pure function, `schedule_week()`, that takes every task and returns
  each task's weekdays.
- The API calls it whenever it returns tasks, and sends the result as
  `scheduled_days`. So the answer always reflects the current schedule.
- The rules: fixed tasks count first. Then weekly tasks go longest first
  (then by id), each onto its lightest days. Ties go to the day furthest from
  the task's other days (so 2× a week is Mon + Thu), then the earliest.

## Alternatives considered

- **Store the picked days when the task is saved:** stable, and easy to
  query, but it never rebalances, which is what the user asked for.
- **Store them and re-run placement for every task on each change:** it
  rebalances, but every save has to rewrite many rows and keep them in sync.
  Working it out on read gives the same answer with nothing to keep in sync.

## Consequences

- Same input, same days: the function is deterministic, so the days don't
  flicker between page loads.
- Adding a task can move another weekly task to a different day, which is
  the point. **When the daily checklist arrives**, days that have already
  passed this week (and boxes already ticked) must not move. The checklist
  will need to record what was done on which date and schedule only the rest
  of the week.
- Every task is scheduled on every request. That's cheap for one person's
  ~64 tasks; revisit when there are accounts.
