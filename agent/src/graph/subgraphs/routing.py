"""Routing decision subgraph."""

from langgraph.graph import StateGraph

from ...core.config import settings
from ...core.logger import get_logger
from ...state.state import GraphState
from ...tools.routing_signal import routing_signal

logger = get_logger(__name__)


async def routing_decision_node(state: GraphState) -> dict:
    """Routing decision logic."""
    logger.info("Evaluating routing decision", session_id=state["session_id"])

    should_route = False
    reason = None
    target_level = 1

    # Check critical intent
    if state["intent_score"] >= settings.intent_threshold_critical:
        should_route = True
        reason = "Critical intent detected - professional assistance required"
        target_level = 3  # Professional

    # Check routing keywords
    elif any(
        keyword in state["current_message"].lower()
        for keyword in settings.routing_keywords
    ):
        should_route = True
        reason = "Routing keyword detected"
        target_level = 2  # Human volunteer

    # Check explicit request
    elif any(
        phrase in state["current_message"].lower()
        for phrase in ["falar com humano", "quero um humano", "pessoa real"]
    ):
        should_route = True
        reason = "Explicit request for human assistance"
        target_level = 2

    if should_route:
        logger.info(
            "Routing required",
            session_id=state["session_id"],
            reason=reason,
            target_level=target_level,
        )

        # Emit signal to gateway
        if settings.auto_route_on_critical:
            await routing_signal.emit(
                session_id=state["session_id"],
                reason=reason,
                target_level=target_level,
                intent_score=state["intent_score"],
            )

    return {
        "should_route": should_route,
        "route_reason": reason,
        "route_target": target_level,
    }


def create_routing_subgraph() -> StateGraph:
    """Create routing decision subgraph."""
    workflow = StateGraph(GraphState)

    # Add node
    workflow.add_node("decide", routing_decision_node)

    # Define flow
    workflow.set_entry_point("decide")
    workflow.set_finish_point("decide")

    return workflow.compile()
