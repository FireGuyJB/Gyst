# Development workflow

## The golden rules

1. **Never commit directly to `main`.** `main` should always work.
2. **One branch and one PR per change.**
3. **Docs change in the same PR as the code.**
4. **CI must be green before merging.**

## Branch names

| Prefix | Use for | Example |
|---|---|---|
| `feature/NNN-name` | A new feature (matches `docs/features/NNN-*`) | `feature/001-goal-chart-model` |
| `fix/name` | A bug fix | `fix/checklist-date-off-by-one` |
| `docs/name` | Docs only | `docs/add-figma-link` |
| `chore/name` | Tooling, config, dependencies | `chore/repo-foundations` |

## Commit messages

A short prefix, then what changed, in the present tense:

```
feat: add goals table and migration
fix: show tasks due today in local time
docs: add calendar requirements
chore: upgrade Next.js
test: cover 8-task limit on supporting goals
```

## The loop

```bash
git checkout main && git pull           # start from the latest main
git checkout -b feature/001-...          # make a branch
# ...edit, run checks, commit small steps...
git add <files> && git commit -m "feat: ..."
git push -u origin feature/001-...       # first push of the branch
gh pr create                             # open a PR (fills in the template)
gh pr checks --watch                     # watch CI
```

After the PR is merged on GitHub:

```bash
git checkout main && git pull
git branch -d feature/001-...            # delete the local branch
```

## Working with Claude Code

`CLAUDE.md` at the repo root holds the rules Claude follows here. For a
new feature, ask Claude to brainstorm and spec it first (step 1 of
[features/README.md](../features/README.md)), then build.
