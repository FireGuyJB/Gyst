# Shortcuts for running Gyst locally. Run from the repo root, e.g. `make dev`.
# Each target just runs the same commands documented in docs/guides/getting-started.md.

.PHONY: setup dev backend frontend health check

# Install everything and bring the local database up to date.
setup:
	cd backend && uv sync && uv run alembic upgrade head
	cd frontend && npm install

# Run the API and the frontend together. Ctrl+C stops both.
# `trap 'kill 0' EXIT` kills every process this line started when it exits.
dev:
	trap 'kill 0' EXIT; $(MAKE) backend & $(MAKE) frontend & wait

backend:
	cd backend && uv run fastapi dev app/main.py

frontend:
	cd frontend && npm run dev

# Ask the running API whether it's up. Prints {"status":"ok"} if so.
health:
	@curl -sf http://localhost:8000/health && echo || echo "API is not reachable at http://localhost:8000 (is \`make dev\` running?)"

# The same checks CI runs.
check:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
	cd frontend && npm run lint && npm run build
