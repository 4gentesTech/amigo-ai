"""Input validation and sanitization node."""

import re

from ..core.logger import get_logger
from ..state.node_schemas import GuardrailResult
from ..state.state import GraphState

logger = get_logger(__name__)


class Guardrails:
    """Input validation and threat detection."""

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all)\s+instructions?",
        r"you\s+are\s+now",
        r"system\s*:\s*",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"###\s*instruction",
    ]

    @staticmethod
    def validate(message: str) -> GuardrailResult:
        """Validate and sanitize input message."""
        threats = []

        # Detect injection attempts
        for pattern in Guardrails.INJECTION_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                threats.append(f"Injection pattern detected: {pattern}")

        # Sanitize dangerous characters
        sanitized = message.strip()
        sanitized = re.sub(r"[<>]", "", sanitized)  # Remove HTML tags

        # Enforce length limit
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000]
            threats.append("Message truncated due to length limit")

        is_safe = len(threats) == 0

        if not is_safe:
            logger.warning("Security threats detected", threat_count=len(threats))

        return GuardrailResult(
            is_safe=is_safe,
            sanitized_message=sanitized,
            threats_detected=threats,
        )


def guardrails_node(state: GraphState) -> dict:
    """Guardrails node in graph."""
    logger.info("Executing guardrails node", session_id=state["session_id"])

    result = Guardrails.validate(state["current_message"])

    return {
        "current_message": result.sanitized_message,
    }
