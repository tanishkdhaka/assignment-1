"""Schema constants and JSON schema for the Support Ticket Triager."""
from __future__ import annotations

CATEGORIES: list[str] = [
    "billing",
    "technical",
    "account",
    "feature_request",
    "other",
]

PRIORITIES: list[str] = [
    "critical",
    "high",
    "medium",
    "low",
]

TEAMS: list[str] = [
    "billing-ops",
    "engineering",
    "account-support",
    "product",
    "general-support",
]

# Deterministic mapping: category -> team (INV-006)
TEAM_MAP: dict[str, str] = {
    "billing": "billing-ops",
    "technical": "engineering",
    "account": "account-support",
    "feature_request": "product",
    "other": "general-support",
}

# JSON Schema for Layer 1 validation
OUTPUT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": CATEGORIES},
        "priority": {"type": "string", "enum": PRIORITIES},
        "needs_clarification": {"type": "boolean"},
        "clarification_question": {"type": "string"},
        "assigned_team": {"type": "string", "enum": TEAMS},
        "summary": {"type": "string", "minLength": 10, "maxLength": 120},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": [
        "category",
        "priority",
        "needs_clarification",
        "clarification_question",
        "assigned_team",
        "summary",
        "confidence",
    ],
    "additionalProperties": False,
}

# Gemini response schema (mirrors OUTPUT_SCHEMA for structured output mode)
GEMINI_RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": CATEGORIES,
            "description": "Ticket category",
        },
        "priority": {
            "type": "string",
            "enum": PRIORITIES,
            "description": "Urgency level",
        },
        "needs_clarification": {
            "type": "boolean",
            "description": "True if the ticket lacks enough information to route",
        },
        "clarification_question": {
            "type": "string",
            "description": "Question to ask the user; empty string when needs_clarification is false",
        },
        "assigned_team": {
            "type": "string",
            "enum": TEAMS,
            "description": "Team to route this ticket to",
        },
        "summary": {
            "type": "string",
            "description": "Brief summary of the ticket, 10 to 120 characters",
        },
        "confidence": {
            "type": "number",
            "description": "Model confidence in the classification, 0.0 to 1.0",
        },
    },
    "required": [
        "category",
        "priority",
        "needs_clarification",
        "clarification_question",
        "assigned_team",
        "summary",
        "confidence",
    ],
}
