"""Guardrail checks for the Support Ticket Triager."""

from __future__ import annotations

import re
from typing import Any

FORBIDDEN_PHRASES: list[str] = [
    "system prompt",
    "ignore previous instructions",
    "ignore all previous instructions",
    "jailbreak",
    "developermodeai",
    "master administrative api key",
]

PROHIBITED_INTENTS: list[str] = [
    "bypass sql injection",
    "exfiltrate user",
    "root password",
]


def check_pre_call_guardrails(ticket_text: str) -> dict[str, Any] | None:
    """
    Check if ticket triggers automatic short-circuit or guardrail response.

    Returns a dict with pre-computed triage result if triggered, else None.
    """
    cleaned = ticket_text.strip()

    # PROP-001: Fewer than 5 characters requires clarification
    if len(cleaned) < 5:
        return {
            "category": "other",
            "priority": "low",
            "needs_clarification": True,
            "clarification_question": "Please provide more details about your issue.",
            "assigned_team": "general-support",
            "summary": "Ticket text too short to triage; requested clarification.",
            "confidence": 1.0,
            "_guardrail_triggered": "SHORT_INPUT",
        }

    lower_text = cleaned.lower()

    # PROP-002 & PROP-003: Guardrail triggers (adversarial, jailbreak, prompt leakage)
    for phrase in FORBIDDEN_PHRASES + PROHIBITED_INTENTS:
        if phrase in lower_text:
            return {
                "category": "other",
                "priority": "low",
                "needs_clarification": False,
                "clarification_question": "",
                "assigned_team": "general-support",
                "summary": "Request violates usage policy and cannot be processed.",
                "confidence": 0.0,
                "_guardrail_triggered": "SECURITY_POLICY_VIOLATION",
            }

    return None


def sanitize_output(output: dict[str, Any]) -> dict[str, Any]:
    """
    Post-process and validate model output invariants (PROP-003, INV-005, INV-006).
    """
    sanitized = dict(output)

    # INV-005: clarification_question must be empty string when
    # needs_clarification is False
    if not sanitized.get("needs_clarification"):
        sanitized["clarification_question"] = ""

    # PROP-003: ensure forbidden words do not appear in any field
    for field in ["summary", "clarification_question"]:
        val = sanitized.get(field, "")
        if isinstance(val, str):
            for phrase in FORBIDDEN_PHRASES:
                val = re.sub(re.escape(phrase), "[REDACTED]", val, flags=re.IGNORECASE)
            sanitized[field] = val

    return sanitized
