# How we build features

Every feature, big or small, follows the same six steps. The goal is that
anyone (including future-you) can see what was built, why, and how each
layer connects.

## 1. Spec it

Copy the template into a numbered folder:

```bash
cp -r docs/features/_template docs/features/001-goal-chart-model
```

Fill in `spec.md`: the problem, user stories, acceptance criteria, **how the
layers connect**, and open questions. Link the requirement IDs it covers (from
[product/requirements.md](../product/requirements.md)).

## 2. Decide

If the feature forces a significant technical choice, write an ADR in
[decisions/](../decisions/).

## 3. Branch

```bash
git checkout main && git pull
git checkout -b feature/001-goal-chart-model
```

## 4. Build layer by layer, bottom-up

1. **Database:** add or change models in `backend/app/models.py`, then
   generate and apply a migration ([how](../architecture/database.md)).
2. **API:** add a route plus request/response schemas. **Write the test
   first** (in `backend/tests/`), watch it fail, then make it pass.
3. **Frontend:** build the page or component that calls the API.

Commit after each working step (small commits are easier to review and undo).

## 5. Update the docs

- Mark the requirements' status in `product/requirements.md`.
- Update `architecture/` if how the layers connect changed.
- Set the spec's **Status** to `Done`.

## 6. Open a PR

Push and open a PR. Fill in the template, especially **"How the layers
connect"**. CI must pass before merging.

## Feature index

| # | Feature | Status |
|---|---|---|
| [001](001-walking-skeleton/spec.md) | Walking skeleton: connect frontend → API → database (primary goal title only) | Done |
