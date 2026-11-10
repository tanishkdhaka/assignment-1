"""Unit tests for Part 1B schema and constants."""

from __future__ import annotations

import jsonschema

from triager.schema import CATEGORIES, OUTPUT_SCHEMA, PRIORITIES, TEAM_MAP, TEAMS


def test_categories_enumeration() -> None:
    assert len(CATEGORIES) == 5
    assert "billing" in CATEGORIES
    assert "technical" in CATEGORIES
    assert "account" in CATEGORIES
    assert "feature_request" in CATEGORIES
    assert "other" in CATEGORIES


def test_priorities_enumeration() -> None:
    assert len(PRIORITIES) == 4
    assert set(PRIORITIES) == {"critical", "high", "medium", "low"}


def test_team_map_covers_all_categories() -> None:
    for cat in CATEGORIES:
        assert cat in TEAM_MAP
        assert TEAM_MAP[cat] in TEAMS


def test_schema_validates_conforming_output() -> None:
    valid_record = {
        "category": "technical",
        "priority": "high",
        "needs_clarification": False,
        "clarification_question": "",
        "assigned_team": "engineering",
        "summary": "Database connectivity loss affecting checkout.",
        "confidence": 0.95,
    }
    validator = jsonschema.Draft202012Validator(OUTPUT_SCHEMA)
    assert validator.is_valid(valid_record)


def test_schema_rejects_missing_field() -> None:
    record = {
        "category": "technical",
        "priority": "high",
        "needs_clarification": False,
        # missing clarification_question
        "assigned_team": "engineering",
        "summary": "Database connectivity loss affecting checkout.",
        "confidence": 0.95,
    }
    validator = jsonschema.Draft202012Validator(OUTPUT_SCHEMA)
    assert not validator.is_valid(record)


def test_schema_rejects_extra_field() -> None:
    record = {
        "category": "technical",
        "priority": "high",
        "needs_clarification": False,
        "clarification_question": "",
        "assigned_team": "engineering",
        "summary": "Database connectivity loss affecting checkout.",
        "confidence": 0.95,
        "unexpected_extra_field": "disallowed",
    }
    validator = jsonschema.Draft202012Validator(OUTPUT_SCHEMA)
    assert not validator.is_valid(record)
