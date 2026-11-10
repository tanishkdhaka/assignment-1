"""Core triage engine coordinating guardrails, model client, and contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .guardrails import check_pre_call_guardrails, sanitize_output
from .model_client import ServiceError, call_model
from .schema import TEAM_MAP


@dataclass
class TriageResult:
    """Validated structured result from a ticket triage operation."""

    category: str
    priority: str
    needs_clarification: bool
    clarification_question: str
    assigned_team: str
    summary: str
    confidence: float
    error_code: str | None = None
    is_service_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict matching the Output Schema Contract."""
        return {
            "category": self.category,
            "priority": self.priority,
            "needs_clarification": self.needs_clarification,
            "clarification_question": self.clarification_question,
            "assigned_team": self.assigned_team,
            "summary": self.summary,
            "confidence": self.confidence,
        }


def _get_system_prompt() -> str:
    """Load system prompt from prompts directory or fallback string."""
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "system_prompt.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "You are a support ticket triager. Return JSON adhering to the schema."


def triage(ticket_text: str) -> TriageResult:
    """
    Triage a support ticket into a structured record.

    1. Applies pre-call guardrails (PROP-001, PROP-002).
    2. Calls model client with bounded retry (INV-010).
    3. Enforces deterministic invariants (INV-005, INV-006).
    4. Sanitises output (PROP-003).
    """
    # 1. Pre-call guardrail check
    guardrail_response = check_pre_call_guardrails(ticket_text)
    if guardrail_response is not None:
        return TriageResult(
            category=guardrail_response["category"],
            priority=guardrail_response["priority"],
            needs_clarification=guardrail_response["needs_clarification"],
            clarification_question=guardrail_response["clarification_question"],
            assigned_team=guardrail_response["assigned_team"],
            summary=guardrail_response["summary"],
            confidence=guardrail_response["confidence"],
        )

    # 2. Model call
    sys_prompt = _get_system_prompt()
    try:
        raw_output = call_model(ticket_text, sys_prompt)
    except ServiceError as se:
        return TriageResult(
            category="other",
            priority="low",
            needs_clarification=True,
            clarification_question=(
                "Service temporarily unavailable; please retry shortly."
            ),
            assigned_team="general-support",
            summary=f"Service error: {se.code}",
            confidence=0.0,
            error_code=se.code,
            is_service_error=True,
        )

    # 3. Post-processing & invariant enforcement
    sanitized = sanitize_output(raw_output)

    # INV-006: assigned_team is strictly deterministic from category
    cat = sanitized.get("category", "other")
    assigned_team = TEAM_MAP.get(cat, "general-support")

    return TriageResult(
        category=cat,
        priority=sanitized.get("priority", "low"),
        needs_clarification=bool(sanitized.get("needs_clarification", False)),
        clarification_question=str(sanitized.get("clarification_question", "")),
        assigned_team=assigned_team,
        summary=str(sanitized.get("summary", "Support ticket requires attention.")),
        confidence=float(sanitized.get("confidence", 0.8)),
    )
