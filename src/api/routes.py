"""
API routes.
Part 2: chat endpoint is a STUB — it echoes back for now.
Part 6 will wire this to the real conversation manager (LLM + memory).
"""

from fastapi import APIRouter
from src.api.schemas import ChatRequest, ChatResponse, HealthResponse
from src.config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        env=settings.app_env,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # --- STUB ---
    # Real logic arrives in Part 6 (conversation manager).
    # For now: prove the request/response cycle + validation works end-to-end.
    reply = f"(stub) You said: '{request.message}'. Memory + LLM wiring comes in Part 6."

    return ChatResponse(
        reply=reply,
        user_id=request.user_id,
        memories_used=[],
    )

