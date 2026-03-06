"""FastAPI server with streaming support."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .core.config import settings
from .core.logger import get_logger
from .graph.main_graph import main_graph
from .state.schema import (
    AgentRequest,
    AgentResponse,
    IntentMetadata,
    ResponseMetadata,
    RoutingMetadata,
)

# Logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle."""
    logger.info("Agent service started", version="0.2.0")
    yield
    logger.info("Agent service stopped")


app = FastAPI(
    title="Agent Service",
    description="Multi-level AI inference engine",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.2.0"}


@app.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest) -> AgentResponse:
    """Main chat endpoint."""
    logger.info("Processing message", session_id=request.session_id)

    try:
        # Prepare initial state
        initial_state = {
            "session_id": request.session_id,
            "thread_id": request.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in request.history
            ],
            "current_message": request.message,
            "intent_score": 0.0,
            "intent_factors": [],
            "retrieved_context": "",
            "response": "",
            "is_compliant": True,
            "compliance_issues": [],
            "should_route": False,
            "route_reason": None,
            "route_target": 1,
            "model_used": settings.default_model,
            "tokens_used": 0,
        }

        # Invoke main graph
        config = {"configurable": {"thread_id": request.session_id}}
        result = main_graph.invoke(initial_state, config)

        # Determine intent level
        intent_score = result.get("intent_score", 0.0)
        if intent_score >= settings.intent_threshold_critical:
            intent_level = "critical"
        elif intent_score >= settings.intent_threshold_high:
            intent_level = "high"
        elif intent_score >= settings.intent_threshold_medium:
            intent_level = "medium"
        else:
            intent_level = "low"

        # Build response
        return AgentResponse(
            session_id=request.session_id,
            response=result.get("response", ""),
            metadata=ResponseMetadata(
                model=result.get("model_used", settings.default_model),
                tokens=result.get("tokens_used", 0),
                intent=IntentMetadata(
                    score=intent_score,
                    factors=result.get("intent_factors", []),
                    level=intent_level,
                ),
                routing=RoutingMetadata(
                    should_route=result.get("should_route", False),
                    reason=result.get("route_reason"),
                    target_level=result.get("route_target", 1),
                ),
                compliance_passed=result.get("is_compliant", True),
            ),
        )

    except Exception as e:
        logger.error(
            "Error processing message",
            session_id=request.session_id,
            error=str(type(e).__name__),
        )
        raise HTTPException(status_code=500, detail="Internal agent error") from e


@app.post("/chat/stream")
async def chat_stream(request: AgentRequest) -> StreamingResponse:
    """Streaming chat endpoint (future implementation)."""
    # TODO: Implement streaming with astream()
    raise HTTPException(status_code=501, detail="Streaming not implemented yet")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
    )
