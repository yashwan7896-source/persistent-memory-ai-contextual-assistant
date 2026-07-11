"""
App entrypoint. Run with:
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

Then visit http://localhost:8000/docs for interactive Swagger UI.
"""

from fastapi import FastAPI
from src.api.routes import router
from src.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    description="Persistent-memory contextual AI assistant — Hinglish-aware.",
    version="0.2.0",  # bump this each Part
)

app.include_router(router, prefix="/api/v1", tags=["core"])


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running. See /docs for API."}
