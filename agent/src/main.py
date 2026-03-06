"""FastAPI server para o Agent."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .graph import create_graph
from .schemas import AgentMetadata, AgentRequest, AgentResponse, ConversationState, HistoryMessage

# Configuração de logging seguro (sem conteúdo de mensagens)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle do app."""
    logger.info("Agent iniciado")
    yield
    logger.info("Agent finalizado")


app = FastAPI(
    title="AMIGO Agent",
    description="Motor de IA para assistência em saúde mental",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS para comunicação com Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Grafo global (em produção, considerar pool)
graph = create_graph()


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "healthy"}


@app.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest) -> AgentResponse:
    """Endpoint principal de chat."""
    # Log seguro: apenas session_id, sem conteúdo
    logger.info(f"Processando mensagem para sessão: {request.session_id}")

    try:
        # Prepara estado inicial
        state = ConversationState(
            messages=request.history,
            current_message=request.message,
            session_id=request.session_id,
        )

        # Invoca grafo com checkpoint
        config = {"configurable": {"thread_id": request.session_id}}
        result = graph.invoke(state, config)

        # Constrói resposta
        return AgentResponse(
            session_id=request.session_id,
            response=result["response"],
            metadata=AgentMetadata(
                model="gpt-4",
                tokens=len(result["response"].split()),  # Aproximação
                should_handover=result.get("should_handover", False),
                handover_reason=result.get("handover_reason"),
            ),
        )

    except Exception as e:
        logger.error(f"Erro ao processar sessão {request.session_id}: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Erro interno do agent") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
