"""Graph state definition using TypedDict."""

from typing import Annotated, TypedDict


from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # --- Campos CORE (Presentes em todos os nós/grafos) ---
    # Histórico unificado de mensagens
    messages: Annotated[List[BaseMessage], add_messages]
    
    # IDs de rastreio (vindo do Go/Gateway)
    session_id: str
    thread_id: str
    
    # Resposta final ou parcial formatada
    response: Optional[str]

    # --- Campos de CONTROLE (Lógica de Fluxo) ---
    # Determina o próximo passo (ex: 'agent', 'handover', 'end')
    next_step: str
    
    # --- Campo METADATA (Extensível e isolado) ---
    # Aqui entram risk_score, flags de segurança, infos do RAG, etc.
    metadata: Dict[str, Any]
    
    # Logs estruturados da execução atual (telemetria volátil)
    execution_logs: List[Dict[str, Any]]
