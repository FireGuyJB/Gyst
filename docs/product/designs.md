# Designs

**Figma file:** <https://www.figma.com/design/GLscEIaKNkrVg3gGQQKtgu/Gyst>

Early, low-fidelity screens. They set the **layout and flow**; exact styling
will keep changing. When building UI, check the matching Figma page for the
current version.

## What the designs tell us

- **Phone frames are placeholders.** The screens are iPhone-sized, but Gyst is built **laptop-first** ([ADR 0004](../decisions/0004-web-app-laptop-first.md)). Take the content, flow and style from these screens and adapt the layout to a wide screen.
- **Light and dark themes.** Each creation screen has a light and a dark
  version.
- **Two modes:**
  - **Creation:** setting up the chart.
  - **Standard:** using it day to day.
- **The chart is a 3 × 3 grid you drill into, not one big 9 × 9 grid.** The
  center tile is the goal one level up, and the 8 tiles around it are its
  children. This keeps each screen focused and still works when we add phone layouts later.
- **Color identity.** The primary goal is yellow, and each supporting goal has
  its own color: rose, mint, blue, peach, taupe, indigo, pink and sage.
- **Tiles:** large rounded squares. An empty slot shows a white **+**.
- **Header:** a bold "GYST" wordmark. The tagline reads "get your *stuff*
  together", with the empty space in the design standing in for the missing
  word.

## Screens

| Figma page | Mode | What it shows |
|---|---|---|
| `CreationHome` / `CreationHomeDark` | Creation | "+ add primary goal" and one large yellow **+** tile |
| `CreationMid9Light` / `CreationMid9Dark` | Creation | "+ add supporting goal" and a 3 × 3 grid: the yellow primary goal in the center, 8 colored **+** tiles around it |
| `CreationTask9Light` / `CreationTask9Dark` | Creation | The 8 tasks for one supporting goal (the same 3 × 3 pattern) |
| `StandardHomeLight` | Standard | The tagline and the primary goal tile with its title (placeholder text) |
| `StandardMid9Light` | Standard | The filled 3 × 3 grid, plus a button at the bottom (probably checklist/calendar navigation; TBD) |

## Navigation (as understood so far)

```
Home (primary goal) ──tap──▶ Mid 9 (8 supporting goals) ──tap a tile──▶ Task 9 (8 tasks)
```
