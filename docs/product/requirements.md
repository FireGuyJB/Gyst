# Requirements

A living document. Each requirement gets an ID so feature specs and PRs can
reference it (e.g. "implements R2.1"). Status: `planned` → `in progress` → `done`.

## R1. Goal chart (Harada structure)

| ID | Requirement | Status |
|---|---|---|
| R1.1 | A user can create a **primary goal** with a title (and optional description). | planned |
| R1.2 | Each primary goal has exactly **8 supporting goals** (slots), which the user fills in. | planned |
| R1.3 | Each supporting goal has exactly **8 tasks** (slots), for 64 per primary goal. | planned |
| R1.4 | The user can view the whole chart at once (the 9×9 grid view). | planned |
| R1.5 | The user can edit or clear any goal or task. | planned |

## R2. Checklist

| ID | Requirement | Status |
|---|---|---|
| R2.1 | Tasks appear in a checklist the user can mark done or not done. | planned |
| R2.2 | Tasks can be one-off or **recurring** (e.g. daily, specific weekdays) to build routines. | planned |
| R2.3 | The checklist shows progress per supporting goal and for the primary goal. | planned |

## R3. Calendar

| ID | Requirement | Status |
|---|---|---|
| R3.1 | Tasks can be scheduled on dates (and, for recurring tasks, on a pattern). | planned |
| R3.2 | A calendar view shows what's scheduled for each day/week. | planned |
| R3.3 | A "today" view shows the day's tasks to check off. | planned |

## Non-functional

| ID | Requirement | Status |
|---|---|---|
| N1 | Local development uses SQLite; production will use PostgreSQL with no code rewrites (see [ADR 0003](../decisions/0003-sqlite-first.md)). | done |
| N2 | Every PR passes automated lint, test, and build checks. | done |

## Open questions

- **Accounts:** do users sign in from the start, or is v1 single-user/local?
- **Multiple goals:** can a user have more than one primary goal at a time?
- **Recurrence rules:** how flexible (daily/weekly only, or "every 3 days")?
- **Partially filled charts:** can a user start using the checklist before all 64 tasks are filled? (Likely yes.)
- **Designs:** Figma link to be added; screens will refine R1.4, R2, R3.
