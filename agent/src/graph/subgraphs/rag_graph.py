"""RAG (Retrieval-Augmented Generation) subgraph."""

from langgraph.graph import StateGraph

from ...core.logger import get_logger
from ...state.state import GraphState
from ...tools.vector_store import vector_store

logger = get_logger(__name__)


def rag_retrieval_node(state: GraphState) -> dict:
    """RAG context retrieval node."""
    logger.info("Executing RAG context retrieval", session_id=state["session_id"])

    # Search relevant context
    context = vector_store.search(state["current_message"])

    return {
        "retrieved_context": context,
    }


def create_rag_subgraph() -> StateGraph:
    """Create RAG retrieval subgraph."""
    workflow = StateGraph(GraphState)

    # Add node
    workflow.add_node("rag_retrieve", rag_retrieval_node)

    # Define flow
    workflow.set_entry_point("rag_retrieve")
    workflow.set_finish_point("rag_retrieve")

    return workflow.compile()
