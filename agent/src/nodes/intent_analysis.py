"""Intent analysis and classification node."""

import re

from ..core.config import settings
from ..core.logger import get_logger
from ..state.node_schemas import IntentAnalysisResult
from ..state.state import GraphState

logger = get_logger(__name__)


class IntentAnalyzer:
    """Keyword and pattern-based intent analyzer."""

    # Critical intent keywords
    CRITICAL_KEYWORDS = [
        "suicídio",
        "me matar",
        "quero morrer",
        "acabar com tudo",
        "não vale a pena viver",
    ]

    HIGH_INTENT_KEYWORDS = [
        "desespero",
        "sem saída",
        "não aguento",
        "sozinho",
        "ninguém se importa",
    ]

    @staticmethod
    def analyze(message: str, history: list[dict]) -> IntentAnalysisResult:
        """Analyze message intent and urgency."""
        factors = []
        score = 0.0

        # Keyword analysis
        message_lower = message.lower()

        for keyword in IntentAnalyzer.CRITICAL_KEYWORDS:
            if keyword in message_lower:
                factors.append(f"Critical keyword: {keyword}")
                score += 0.3

        for keyword in IntentAnalyzer.HIGH_INTENT_KEYWORDS:
            if keyword in message_lower:
                factors.append(f"High intent keyword: {keyword}")
                score += 0.15

        # Pattern analysis
        if re.search(r"\b(adeus|tchau|despedida)\b.*\b(para sempre|última vez)\b", message_lower):
            factors.append("Farewell pattern detected")
            score += 0.25

        # Normalize score
        score = min(score, 1.0)

        # Determine sentiment
        if score >= settings.intent_threshold_critical:
            sentiment = "critical"
        elif score >= settings.intent_threshold_high:
            sentiment = "negative"
        elif score >= settings.intent_threshold_medium:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        requires_immediate_routing = score >= settings.intent_threshold_critical

        logger.info(
            "Intent analysis completed",
            intent_score=score,
            sentiment=sentiment,
            factors_count=len(factors),
        )

        return IntentAnalysisResult(
            score=score,
            factors=factors,
            sentiment=sentiment,
            requires_immediate_routing=requires_immediate_routing,
        )


def intent_analysis_node(state: GraphState) -> dict:
    """Intent analysis node in graph."""
    logger.info("Executing intent analysis", session_id=state["session_id"])

    result = IntentAnalyzer.analyze(
        state["current_message"],
        state.get("messages", []),
    )

    return {
        "intent_score": result.score,
        "intent_factors": result.factors,
        "should_route": result.requires_immediate_routing,
        "route_reason": "Critical intent detected" if result.requires_immediate_routing else None,
        "route_target": 3 if result.requires_immediate_routing else 1,
    }
