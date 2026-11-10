# Tasks — Support Ticket Triager

## Task Status Key
- [ ] Pending
- [x] Done
- [~] In progress

---

## T-B-01 Project setup
**Covers:** P-01, P-05
**Type:** Setup
- [x] Create `pyproject.toml` with all dependencies.
- [x] Create `.env.example` with `GEMINI_API_KEY=your-key-here` and `GEMINI_MODEL=gemini-2.0-flash`.
- [x] Confirm `.env` is in `.gitignore`.

## T-B-02 Schema and constants
**Covers:** §4, INV-001–INV-003, INV-006–INV-009
**Type:** Agent
- [x] Write `src/triager/schema.py` with CATEGORIES, PRIORITIES, TEAMS, TEAM_MAP, JSON_SCHEMA.
- [x] Write `evals/threshold.json` with threshold and scoring formula.

## T-B-03 System prompt
**Covers:** FR-B-01–FR-B-05, PROP-002, PROP-003
**Type:** Agent
- [x] Write `prompts/system_prompt.txt` with output format instructions and guardrail rules.

## T-B-04 Model client
**Covers:** INV-010, P-09, CLR-007
**Type:** Agent
- [x] Write `src/triager/model_client.py` with retry logic (429/503/timeout) and JSON extraction.

## T-B-05 Triager core
**Covers:** All FR-B-*, US-001–US-006
**Type:** Agent
- [x] Write `src/triager/triager.py` with `triage(ticket_text) -> TriageResult | ErrorRecord`.
- [x] Post-process: set `assigned_team` from TEAM_MAP.

## T-B-06 Guardrails module
**Covers:** PROP-002, PROP-003
**Type:** Agent
- [x] Write `src/triager/guardrails.py` with pre/post output checks.

## T-B-07 Evaluation dataset
**Covers:** §9 Traceability matrix, all 20 cases
**Type:** Agent
- [x] Write `evals/dataset.json` with 20 cases covering all categories, priorities, clarification, and guardrails.

## T-B-08 Layer 1: schema validation harness
**Covers:** §4 Output Schema Contract
**Type:** Agent
- [x] Write `.harness/layer1_schema.py`.

## T-B-09 Layer 2: invariant and property checks
**Covers:** INV-001–INV-010, PROP-001–PROP-004
**Type:** Agent
- [x] Write `.harness/layer2_invariants.py`.

## T-B-10 Layer 3: semantic/rubric scoring
**Covers:** §7 Semantic Criteria
**Type:** Agent
- [x] Write `.harness/layer3_semantic.py`.

## T-B-11 Evaluation runner
**Covers:** §8 Acceptance Threshold
**Type:** Agent
- [x] Write `.harness/eval_runner.py` and `.harness/harness_runner.py`.

## T-B-12 Unit tests
**Covers:** schema module, guardrails module
**Type:** Agent
- [x] Write `tests/test_schema.py` and `tests/test_guardrails.py`.

## T-B-13 Self-check and baseline
**Covers:** P-07, P-08
**Type:** Human + Agent
- [x] Write `.harness/scripts/self_check.sh`.
- [ ] Run self-check and confirm each layer fails on deliberately broken input.
- [ ] Create baseline tag: `git tag baseline-part-b-before-implement`.

## T-B-14 Evidence packaging
**Covers:** P-09
**Type:** Human
- [ ] Save first generation in `evidence/initial-generation/`.
- [ ] Save final generation in `evidence/final-generation/` after last pass.
- [ ] Keep all evaluation run outputs in `evidence/`.
