# Clarifications — Support Ticket Triager

## CLR-001: clarification_question when needs_clarification=false
**Question:** What value should `clarification_question` have when `needs_clarification=false`?
**Answer:** An empty string `""`. This makes INV-005 machine-checkable without special-casing `null`.
**Decision date:** 2026-11-10. Reflected in INV-004, INV-005.

## CLR-002: Team assignment is deterministic from category
**Question:** Can the model assign any team it deems appropriate?
**Answer:** No. The team is a deterministic mapping from category (Table §4.3). INV-006 checks this independently of the model.
**Decision date:** 2026-11-10. Reflected in INV-006.

## CLR-003: Confidence field is model-reported, not harness-computed
**Question:** Does the harness compute confidence or trust the model's value?
**Answer:** The model reports confidence. The harness only checks it is in [0.0, 1.0] (INV-008). It is not used in the acceptance threshold.
**Decision date:** 2026-11-10. Reflected in INV-008.

## CLR-004: Guardrail scope
**Question:** Which ticket content triggers the guardrail path?
**Answer:** Tickets that contain explicit harmful intent, requests to ignore instructions, requests to reveal the system prompt, or requests for clearly illegal content. The rubric field `guardrail=true` marks these cases in the dataset.
**Decision date:** 2026-11-10. Reflected in PROP-002.

## CLR-005: Short ticket handling
**Question:** At what length does a ticket become "too short to triage"?
**Answer:** Fewer than 5 characters (after stripping whitespace). Such a ticket triggers `needs_clarification=true` and `priority=low`.
**Decision date:** 2026-11-10. Reflected in PROP-001.

## CLR-006: Summary length limits
**Question:** How long can the summary be?
**Answer:** 10 to 120 characters inclusive, to be short enough for a UI card and long enough to be informative.
**Decision date:** 2026-11-10. Reflected in INV-007.

## CLR-007: Model retry policy
**Question:** What happens if the model returns malformed JSON on the first attempt?
**Answer:** The harness retries once with the same prompt (attempt 2). If the second attempt also fails, the case is recorded as a service/model failure, not counted in the accuracy score.
**Decision date:** 2026-11-10. Reflected in INV-010, P-09.
