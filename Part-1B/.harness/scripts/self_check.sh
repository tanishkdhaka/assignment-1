#!/usr/bin/env bash
# Self-check: verify each evaluation layer CAN fail on deliberately broken inputs
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=== SELF-CHECK: Verifying evaluation layers can detect failures ==="

PYTHON="$ROOT/.venv/bin/python"

"$PYTHON" - << 'EOF'
import sys
from pathlib import Path
ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / ".harness"))

from layer1_schema import validate_schema
from layer2_invariants import validate_invariants
from layer3_semantic import evaluate_quality

# 1. Layer 1 broken fake (extra disallowed property)
broken_l1 = {
    "category": "billing",
    "priority": "low",
    "needs_clarification": False,
    "clarification_question": "",
    "assigned_team": "billing-ops",
    "summary": "Valid summary length here.",
    "confidence": 0.9,
    "disallowed_field": "illegal",
}
l1_pass, l1_findings = validate_schema(broken_l1)
if l1_pass:
    print("SELF-CHECK FAIL: Layer 1 did not catch extra disallowed field!")
    sys.exit(1)
else:
    print("Layer 1 (Schema) correctly detected violation: OK")

# 2. Layer 2 broken fake (team mismatch)
broken_l2 = {
    "category": "billing",
    "priority": "low",
    "needs_clarification": False,
    "clarification_question": "",
    "assigned_team": "engineering",  # Wrong! Should be billing-ops
    "summary": "Valid summary length here.",
    "confidence": 0.9,
}
l2_pass, l2_findings = validate_invariants(broken_l2, "Normal billing question")
if l2_pass:
    print("SELF-CHECK FAIL: Layer 2 did not catch team mismatch!")
    sys.exit(1)
else:
    print("Layer 2 (Invariants) correctly detected team mismatch: OK")

# 3. Layer 3 broken fake (wrong category)
broken_l3 = {
    "category": "feature_request",  # expected billing
    "priority": "low",
    "needs_clarification": False,
    "clarification_question": "",
    "assigned_team": "product",
    "summary": "Valid summary text.",
    "confidence": 0.9,
}
rubric = {"expected_category": "billing", "expected_priority": "low", "expect_clarification": False}
score, details = evaluate_quality(broken_l3, rubric)
if details["category_score"] != 0.0:
    print("SELF-CHECK FAIL: Layer 3 did not penalize wrong category!")
    sys.exit(1)
else:
    print("Layer 3 (Quality) correctly scored wrong category as 0.0: OK")

print("\n=== SELF-CHECK PASSED: All 3 evaluation layers detect failures ===")
EOF
