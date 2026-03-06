"""API request/response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================================
# API Input/Output Models
# ============================================================================


class HistoryMessage(BaseModel):
    """Mensagem individual no histórico."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime


class AgentRequest(BaseModel):
    """Request recebido do Backend."""

    session_id: str = Field(..., description="UUID da sessão volátil")
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[HistoryMessage] = Field(default_factory=list)
    context: dict[str, str | int] = Field(default_factory=dict)


class IntentMetadata(BaseModel):
    """Intent analysis metadata."""

    score: float = Field(..., ge=0.0, le=1.0)
    factors: list[str] = Field(default_factory=list)
    level: Literal["low", "medium", "high", "critical"]


class RoutingMetadata(BaseModel):
    """Routing decision metadata."""

    should_route: bool
    reason: str | None = None
    target_level: Literal[1, 2, 3] = 1


class ResponseMetadata(BaseModel):
    """Complete response metadata."""

    model: str
    tokens: int
    intent: IntentMetadata
    routing: RoutingMetadata
    compliance_passed: bool


class AgentResponse(BaseModel):
    """API response to backend."""

    session_id: str
    response: str
    metadata: ResponseMetadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
