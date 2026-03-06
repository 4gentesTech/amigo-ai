"""Pydantic schemas for node inputs/outputs."""

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """Result from guardrails validation."""

    is_safe: bool
    sanitized_message: str
    threats_detected: list[str] = Field(default_factory=list)


class IntentAnalysisResult(BaseModel):
    """Result from intent analysis."""

    score: float = Field(..., ge=0.0, le=1.0)
    factors: list[str]
    sentiment: str
    requires_immediate_routing: bool


class ValidationResult(BaseModel):
    """Result from compliance validation."""

    is_compliant: bool
    issues: list[str] = Field(default_factory=list)
    corrected_response: str | None = None
