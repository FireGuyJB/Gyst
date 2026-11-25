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

Open <http://localhost:3000>. You should see the Gyst home page. **Keep the
backend from step 3 running too:** the page loads its goals from the API, and
shows "Can't reach the Gyst API" if the backend isn't up.

The frontend finds the API through `NEXT_PUBLIC_API_URL` (default
`http://localhost:8000`). You only need to set it if the API runs somewhere
else: copy `frontend/.env.example` to `frontend/.env.local`, edit it, and
restart `npm run dev`.

> Your editor may show a red squiggle on `LayoutProps` until you've run
> `npm run dev` or `npm run build` once. Next.js generates that type; it's harmless.

## 5. Trace a request (try it once)

With both apps running:

1. Open <http://localhost:3000>, then open DevTools (`Cmd+Option+I`) → **Network**.
2. Add a goal, e.g. "Run a marathon", and click **Save**.
3. Click the `goals` request in the list. You may see two: an `OPTIONS` one
   (the browser's CORS check) and the `POST`. Look at the **Payload** (what the
   frontend sent) and **Response** (what the API sent back, with an `id`).
4. Now call the API without the frontend: open <http://localhost:8000/docs>,
   expand `POST /goals`, click **Try it out**, and send `{"title": "   "}`.
   You get `422`: the API's validation rejects it, whichever client calls it.
5. Refresh the home page. Both goals are still there, because they're saved in
   `backend/gyst.db`.

Each step is explained, with file names, in
[architecture/overview.md](../architecture/overview.md#life-of-a-request-a-real-one-saving-a-goal).

## 6. Run the checks (the same ones CI runs)

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
