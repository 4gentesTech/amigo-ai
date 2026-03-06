"""Main orchestrator graph."""

from langgraph.graph import StateGraph

from ..core.logger import get_logger
from ..core.memory import memory
from ..nodes.generator import generator_node
from ..nodes.guardrails import guardrails_node
from ..nodes.intent_analysis import intent_analysis_node
from ..nodes.validation import validation_node
from ..state.state import GraphState
from .subgraphs.hitl_graph import create_hitl_subgraph
from .subgraphs.rag_graph import create_rag_subgraph

logger = get_logger(__name__)


def should_continue_to_generator(state: GraphState) -> str:
    """Decide whether to continue to generation or route immediately."""
    if state.get("should_route") and state.get("route_target") == 3:
        # Critical intent: immediate HITL routing
        logger.warning("Critical HITL routing - skipping generation", session_id=state["session_id"])
        return "hitl"
    return "continue"


def create_main_graph() -> StateGraph:
    """Create main orchestrator graph."""
    workflow = StateGraph(GraphState)

    # Add main nodes
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("intent_analysis", intent_analysis_node)
    workflow.add_node("rag", create_rag_subgraph())
    workflow.add_node("generator", generator_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("hitl", create_hitl_subgraph())

    # Define flow
    workflow.set_entry_point("guardrails")

    # Linear flow with conditional decision
    workflow.add_edge("guardrails", "intent_analysis")

    # After intent analysis, decide whether to continue or route to HITL
    workflow.add_conditional_edges(
        "intent_analysis",
        should_continue_to_generator,
        {
            "continue": "rag",
            "hitl": "hitl",
        },
    )

    workflow.add_edge("rag", "generator")
    workflow.add_edge("generator", "validation")
    workflow.add_edge("validation", "hitl")

    # HITL is the final point
    workflow.set_finish_point("hitl")

    # Compile with memory checkpoint
    logger.info("Compiling main graph with memory checkpointer")
    return workflow.compile(checkpointer=memory.get_checkpointer())


# Singleton
main_graph = create_main_graph()
