"""Layer 3: Semantic and quality evaluation against the rubrics."""

from __future__ import annotations

from typing import Any


def evaluate_quality(
    output: dict[str, Any],
    rubric: dict[str, Any],
    is_guardrail: bool = False,
) -> tuple[float, dict[str, Any]]:
    """
    Score the output against the test case rubric.

    Returns (case_score, details_dict).
    """
    expected_cat = rubric.get("expected_category")
    expected_prio = rubric.get("expected_priority")
    expect_clarification = rubric.get("expect_clarification")
    summary_keywords = rubric.get("summary_keywords", [])

    # Category match
    cat_score = 1.0 if output.get("category") == expected_cat else 0.0

    # Priority match
    prio_score = 1.0 if output.get("priority") == expected_prio else 0.0

    # Clarification match
    clarif_score = (
        1.0 if output.get("needs_clarification") == expect_clarification else 0.0
    )

    # Summary keywords recall
    summary = str(output.get("summary", "")).lower()
    if summary_keywords:
        matched = sum(1 for kw in summary_keywords if kw.lower() in summary)
        keyword_score = matched / len(summary_keywords)
    else:
        keyword_score = 1.0

    # If guardrail case: binary gating
    if is_guardrail:
        if cat_score == 1.0 and prio_score == 1.0 and clarif_score == 1.0:
            case_score = 1.0
        else:
            case_score = 0.0
    else:
        case_score = round(
            (cat_score + prio_score + clarif_score + keyword_score) / 4.0, 3
        )

    details = {
        "category_score": cat_score,
        "priority_score": prio_score,
        "clarification_score": clarif_score,
        "summary_keyword_score": round(keyword_score, 3),
        "case_score": case_score,
    }

    return case_score, details
