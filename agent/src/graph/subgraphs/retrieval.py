"""Context retrieval subgraph using RAG."""

from langgraph.graph import StateGraph

from ...core.logger import get_logger
from ...state.state import GraphState
from ...tools.vector_store import vector_store

logger = get_logger(__name__)


def retrieval_node(state: GraphState) -> dict:
    """Context retrieval node."""
    logger.info("Executing context retrieval", session_id=state["session_id"])

    # Search relevant context
    context = vector_store.search(state["current_message"])

    return {
        "retrieved_context": context,
    }


def create_retrieval_subgraph() -> StateGraph:
    """Create RAG retrieval subgraph."""
    workflow = StateGraph(GraphState)

    # Add node
    workflow.add_node("retrieve", retrieval_node)

    # Define flow
    workflow.set_entry_point("retrieve")
    workflow.set_finish_point("retrieve")

    return workflow.compile()
