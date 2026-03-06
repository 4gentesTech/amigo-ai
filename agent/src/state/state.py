"""Graph state definition using TypedDict."""

from typing import Annotated, TypedDict


class GraphState(TypedDict):
    """Shared state across all graph nodes."""

    # Identification
    session_id: str
    thread_id: str

    # Messages
    messages: Annotated[list[dict], "Message history"]
    current_message: str

    # Intent analysis
    intent_score: Annotated[float, "Intent/risk score from 0-1"]
    intent_factors: Annotated[list[str], "Detected intent factors"]

    # Context retrieval
    retrieved_context: Annotated[str, "Context from vector store"]

    # Generation
    response: str

    # Validation
    is_compliant: bool
    compliance_issues: Annotated[list[str], "Detected compliance issues"]

    # Routing
    should_route: bool
    route_reason: str | None
    route_target: Annotated[int, "Target level: 1=AI, 2=Human, 3=Professional"]

    # Metadata
    model_used: str
    tokens_used: int
