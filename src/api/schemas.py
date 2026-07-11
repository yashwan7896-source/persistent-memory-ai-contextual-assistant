"""
API request/response schemas.
Part 2: just chat + health. Part 3 onward will add memory-specific schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique id for the user/session")
    message: str = Field(..., min_length=1, description="The user's message")


class ChatResponse(BaseModel):
    reply: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Placeholder — Part 3+ will populate this with actual retrieved memories
    memories_used: Optional[list] = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    env: str
