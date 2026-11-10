"""Layer 1: Structural validation — Output Schema Contract conformance."""

from __future__ import annotations

from typing import Any

import jsonschema

from triager.schema import OUTPUT_SCHEMA


def validate_schema(output: dict[str, Any]) -> tuple[bool, list[dict[str, str]]]:
    """
    Validate output against the JSON Schema contract.

    Returns (passed, list_of_findings).
    """
    findings: list[dict[str, str]] = []
    validator = jsonschema.Draft202012Validator(OUTPUT_SCHEMA)
    errors = sorted(validator.iter_errors(output), key=lambda e: e.path)

    for err in errors:
        field = ".".join(str(p) for p in err.path) or "root"
        findings.append(
            {
                "layer": "LAYER_1_SCHEMA",
                "code": "SCHEMA_VIOLATION",
                "field": field,
                "message": err.message,
            }
        )

    passed = len(findings) == 0
    return passed, findings
