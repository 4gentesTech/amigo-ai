"""Compliance validation node."""

import re

import yaml

from ..core.config import settings
from ..core.logger import get_logger
from ..state.node_schemas import ValidationResult
from ..state.state import GraphState

logger = get_logger(__name__)


class Validator:
    """Rule-based compliance validator."""

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> dict:
        """Load validation rules from YAML."""
        try:
            with open(settings.validation_policy_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Validation policy file not found, using default rules")
            return self._default_rules()

    def _default_rules(self) -> dict:
        """Default rules if YAML doesn't exist."""
        return {
            "forbidden_patterns": [
                r"\bdiagnóstico\b.*\b(depressão|ansiedade|bipolar|esquizofrenia)\b",
                r"\btome?\b.*\b(remédio|medicamento|antidepressivo)\b",
                r"\bvocê tem\b.*\b(transtorno|doença|síndrome)\b",
            ],
            "required_disclaimers": [
                "não sou profissional",
                "busque ajuda profissional",
            ],
        }

    def validate(self, response: str) -> ValidationResult:
        """Validate response against compliance rules."""
        issues = []

        # Check forbidden patterns
        for pattern in self.rules.get("forbidden_patterns", []):
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f"Forbidden pattern detected: {pattern}")

        # Check minimum length
        if len(response.strip()) < 10:
            issues.append("Response too short")

        is_compliant = len(issues) == 0

        if not is_compliant:
            logger.warning("Compliance issues detected", issues_count=len(issues))

        return ValidationResult(
            is_compliant=is_compliant,
            issues=issues,
            corrected_response=None,
        )


# Singleton
validator = Validator()


def validation_node(state: GraphState) -> dict:
    """Validation node in graph."""
    logger.info("Executing validation", session_id=state["session_id"])

    result = validator.validate(state["response"])

    # If not compliant, replace with safe response
    if not result.is_compliant:
        safe_response = (
            "Sorry, I cannot respond in that way. "
            "Remember that I am only an emotional support assistant, "
            "not a healthcare professional. For medical questions, "
            "please seek a qualified professional."
        )
        return {
            "response": safe_response,
            "is_compliant": False,
            "compliance_issues": result.issues,
        }

    return {
        "is_compliant": True,
        "compliance_issues": [],
    }
