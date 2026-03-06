"""Schemas para comunicação e estado do Agent."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    """Mensagem individual no histórico."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class AgentRequest(BaseModel):
    """Request recebido do Backend."""

    session_id: str = Field(..., description="UUID da sessão volátil")
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[HistoryMessage] = Field(default_factory=list)
    context: dict[str, str | int] = Field(default_factory=dict)


class AgentMetadata(BaseModel):
    """Metadados da resposta do Agent."""

    model: str = "gpt-4"
    tokens: int = 0
    should_handover: bool = False
    handover_reason: str | None = None


class AgentResponse(BaseModel):
    """Response enviado ao Backend."""

    session_id: str
    response: str
    metadata: AgentMetadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationState(BaseModel):
    """Estado interno do grafo de conversação."""

    messages: Annotated[list[HistoryMessage], "Histórico de mensagens"]
    current_message: str
    response: str = ""
    session_id: str
    should_handover: bool = False
    handover_reason: str | None = None
