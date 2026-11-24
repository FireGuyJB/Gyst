# Getting started

## 1. Install the tools (once per computer)

On macOS with [Homebrew](https://brew.sh):

```bash
brew install git node gh uv
```

| Tool | What it's for |
|---|---|
| `git` | Version control: saves history of every change |
| `node` / `npm` | Runs and installs packages for the Next.js frontend |
| `uv` | Installs Python (3.12+) and the backend's packages; runs Python commands |
| `gh` | GitHub from the terminal: open PRs, check CI |

Then log in to GitHub: `gh auth login`.

## 2. Get the code

```bash
git clone https://github.com/FireGuyJB/Gyst.git
cd Gyst
```

## 3. Run the backend (API)

```bash
cd backend
uv sync                          # installs Python 3.12 + packages into backend/.venv
uv run alembic upgrade head      # brings the local database up to date
uv run fastapi dev app/main.py   # starts the API with auto-reload
```

Open <http://localhost:8000/health>. You should see `{"status":"ok"}`.
Open <http://localhost:8000/docs> for FastAPI's interactive API docs.

## 4. Run the frontend (in a second terminal)

Open a new terminal tab; it starts in your home folder, so go to the repo first:

```bash
cd path/to/Gyst/frontend
npm install
npm run dev
```

Open <http://localhost:3000>. You should see the Gyst home page.

> Your editor may show a red squiggle on `LayoutProps` until you've run
> `npm run dev` or `npm run build` once. Next.js generates that type; it's harmless.

## 5. Run the checks (the same ones CI runs)

From the `Gyst` folder:

```bash
# backend
cd backend
uv run ruff check .          # lint: common mistakes
uv run ruff format --check . # formatting (run `uv run ruff format .` to fix)
uv run pytest                # tests
uv run alembic upgrade head  # migrations apply cleanly

# frontend
cd ../frontend
npm run lint
npm run build
```

Next: read [development-workflow.md](development-workflow.md).
