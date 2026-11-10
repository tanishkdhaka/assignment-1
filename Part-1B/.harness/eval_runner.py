#!/usr/bin/env python3
"""
Non-deterministic evaluation runner for the Support Ticket Triager.

Executes all evaluation cases across:
- Layer 1: Schema conformance
- Layer 2: Invariants and properties
- Layer 3: Semantic rubric quality

Compares aggregate score against declared threshold in evals/threshold.json.
Writes results to evidence/eval-results.json.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Ensure paths
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / ".harness"))


def main() -> None:
    from layer1_schema import validate_schema
    from layer2_invariants import validate_invariants
    from layer3_semantic import evaluate_quality

    from triager.triager import triage

    dataset_file = ROOT / "evals" / "dataset.json"
    threshold_file = ROOT / "evals" / "threshold.json"
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        sys.exit(1)

    dataset = json.loads(dataset_file.read_text(encoding="utf-8"))
    threshold_data = json.loads(threshold_file.read_text(encoding="utf-8"))
    overall_threshold = threshold_data.get("overall_threshold", 0.80)

    print(f"\n{'=' * 70}")
    print("NON-DETERMINISTIC EVALUATION HARNESS — Part 1B")
    print(
        f"Dataset cases: {len(dataset)} | Declared threshold: {overall_threshold:.2f}"
    )
    print(f"{'=' * 70}\n")

    case_results = []
    layer1_violations = 0
    layer2_violations = 0
    guardrail_failures = 0
    scores = []

    header = (
        f"{'ID':<8} | {'Category':<15} | {'Prio':<8} | "
        f"{'L1':<4} | {'L2':<4} | {'Score':<6} | {'Status'}"
    )
    print(header)
    print("-" * 70)

    for case in dataset:
        case_id = case["id"]
        ticket_text = case["ticket_text"]
        is_guardrail = case.get("guardrail", False)
        rubric = case.get("rubric", {})

        # Execute application
        result_obj = triage(ticket_text)
        output = result_obj.to_dict()

        # Layer 1: Schema
        l1_pass, l1_findings = validate_schema(output)
        if not l1_pass:
            layer1_violations += 1

        # Layer 2: Invariants
        l2_pass, l2_findings = validate_invariants(
            output, ticket_text, is_guardrail=is_guardrail
        )
        if not l2_pass:
            layer2_violations += 1

        # Layer 3: Semantic Quality
        score, quality_details = evaluate_quality(
            output, rubric, is_guardrail=is_guardrail
        )
        scores.append(score)

        if is_guardrail and score < 1.0:
            guardrail_failures += 1

        case_passed = (
            l1_pass
            and l2_pass
            and (score >= 0.75 if not is_guardrail else score == 1.0)
        )
        status_str = "PASS" if case_passed else "FAIL"

        print(
            f"{case_id:<8} | {output['category']:<15} | {output['priority']:<8} | "
            f"{'OK' if l1_pass else 'FAIL':<4} | {'OK' if l2_pass else 'FAIL':<4} | "
            f"{score:<6.2f} | {status_str}"
        )

        case_results.append(
            {
                "id": case_id,
                "category_group": case.get("category_group"),
                "is_guardrail": is_guardrail,
                "covers": case.get("covers", []),
                "ticket_text": ticket_text,
                "output": output,
                "layer1_schema": {"passed": l1_pass, "findings": l1_findings},
                "layer2_invariants": {"passed": l2_pass, "findings": l2_findings},
                "layer3_quality": quality_details,
                "case_score": score,
                "passed": case_passed,
            }
        )

    overall_mean = sum(scores) / len(scores) if scores else 0.0
    threshold_met = (
        overall_mean >= overall_threshold
        and layer1_violations == 0
        and layer2_violations == 0
        and guardrail_failures == 0
    )

    summary = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "total_cases": len(dataset),
        "overall_mean_score": round(overall_mean, 3),
        "declared_threshold": overall_threshold,
        "threshold_met": threshold_met,
        "overall_status": "PASS" if threshold_met else "FAIL",
        "layer1_violations_total": layer1_violations,
        "layer2_violations_total": layer2_violations,
        "guardrail_failures_total": guardrail_failures,
        "cases": case_results,
    }

    eval_results_file = evidence_dir / "eval-results.json"
    eval_results_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print(
        f"Overall Mean Score:     {overall_mean:.3f} "
        f"(Threshold: {overall_threshold:.2f})"
    )
    print(f"Layer 1 Violations:     {layer1_violations}")
    print(f"Layer 2 Violations:     {layer2_violations}")
    print(f"Guardrail Failures:     {guardrail_failures}")
    print(f"Overall Verdict:        {summary['overall_status']}")
    print(f"Results File:           {eval_results_file}")
    print("=" * 70 + "\n")

    sys.exit(0 if threshold_met else 1)


if __name__ == "__main__":
    main()
