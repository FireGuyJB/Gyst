"""API entry point. Run locally with: uv run fastapi dev app/main.py"""

from fastapi import FastAPI

app = FastAPI(title="Gyst API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Simple check that the API is up. Used by humans, CI, and (later) hosting."""
    return {"status": "ok"}
