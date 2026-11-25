"""API entry point. Run locally with: uv run fastapi dev app/main.py"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import goals, supporting_goals

app = FastAPI(title="Gyst API", version="0.1.0")

# CORS: the frontend (localhost:3000) and the API (localhost:8000) are different
# "origins", so browsers block the frontend's requests unless the API allows them.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goals.router)
app.include_router(supporting_goals.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple check that the API is up. Used by humans, CI, and (later) hosting."""
    return {"status": "ok"}
