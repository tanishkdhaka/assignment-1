# Technical Plan — Support Ticket Triager

## Architecture

```
src/triager/
  __init__.py     — public API
  schema.py       — CATEGORIES, PRIORITIES, TEAMS, TEAM_MAP, output JSON schema dict
  prompt.py       — system prompt and user prompt builder
  model_client.py — Gemini API call with retry, service-error handling, JSON extraction
  triager.py      — TriageResult dataclass; triage(ticket_text) -> TriageResult | ErrorRecord
  guardrails.py   — pre/post output guardrail checks
prompts/
  system_prompt.txt — the system prompt given to the model
evals/
  dataset.json    — 20 test cases
  threshold.json  — declared threshold before evaluation
.harness/
  harness_runner.py  — orchestrates all three layers
  layer1_schema.py   — JSON schema validation
  layer2_invariants.py — deterministic invariant and property checks
  layer3_semantic.py — rubric scoring
  eval_runner.py     — runs all 20 cases, writes eval-results.json
  scripts/
    self_check.sh  — fake apps that break each layer
tests/
  test_schema.py     — unit tests for schema module
  test_guardrails.py — unit tests for guardrail module
```

## Architectural Decisions

### ADR-B-001: Gemini API with structured JSON output
**Decision:** Use `google-generativeai` with `response_mime_type="application/json"` and a `response_schema` matching the output contract.
**Alternatives considered:** Plain text with regex extraction; function calling.
**Reason:** JSON mode makes Layer 1 validation simpler and reduces prompt engineering complexity. Layer 1 still runs independently as a double-check.

### ADR-B-002: Team assignment is deterministic post-processing
**Decision:** `assigned_team` is computed by the harness from the model's `category` output using the fixed map in `schema.py`, then the model's value is checked against it.
**Alternatives considered:** Trust the model's team value entirely.
**Reason:** INV-006 must be a machine-checkable invariant. The harness overrides the model's team value and flags a discrepancy as a Layer 2 failure.

### ADR-B-003: Rubric-based Layer 3 (not LLM-as-judge)
**Decision:** Layer 3 uses a deterministic rubric: exact-match for category and priority, boolean match for clarification, keyword coverage for summary.
**Alternatives considered:** LLM-as-judge for summary quality.
**Reason:** A deterministic rubric is reproducible and auditable. LLM-as-judge introduces a second source of non-determinism and would not replace Layers 1 and 2 anyway (brief §5.4).

### ADR-B-004: 20 evaluation cases (exceeds minimum of 15)
**Decision:** 20 cases.
**Alternatives considered:** 15 (minimum), 30 (larger but slower).
**Reason:** 20 gives meaningful threshold statistics while staying within free-tier rate limits for a single formal evaluation run.

## Layer Interaction

```
Ticket text
  → Pre-call guardrail check (guardrails.py)
  → Gemini API call (model_client.py)  — retried up to 2× on 429/503/timeout
  → JSON extraction and parse
  → Layer 1: schema validation (layer1_schema.py)
      FAIL → record finding, skip layers 2 and 3 for this case
  → Layer 2: invariant and property checks (layer2_invariants.py)
      FAIL → record finding, continue to layer 3
  → Layer 3: rubric scoring (layer3_semantic.py)
  → Per-case result written to eval-results.json
  → Aggregate score vs. threshold (eval_runner.py)
  → PASS / FAIL printed
```

## Scoring Formula (declared in threshold.json)

```
per_case_score = mean(
    1.0 if output.category == rubric.expected_category else 0.0,
    1.0 if output.priority == rubric.expected_priority else 0.0,
    1.0 if output.needs_clarification == rubric.expect_clarification else 0.0,
    proportion of rubric.summary_keywords present in output.summary
)
overall_score = mean(per_case_score) across all 20 cases
pass = overall_score >= 0.80
     AND all guardrail cases have per_case_score == 1.0 on (category, priority, clarification)
     AND Layer 1 findings == 0
     AND Layer 2 findings == 0
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini API key (required; never committed) |
| `GEMINI_MODEL` | Model name (default: `gemini-2.0-flash`) |

## Dependency Summary

| Package | Role | Why needed |
|---|---|---|
| google-generativeai | Gemini API client | Model calls for Part B |
| jsonschema | Layer 1 validation | Schema conformance check independent of the model |
| pytest >= 8 | Test runner | Unit tests |
| ruff >= 0.9 | Lint/style | Harness gate P-02 |
| bandit[toml] >= 1.8 | SAST | Harness gate P-03 |
