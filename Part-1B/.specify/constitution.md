# Project Constitution — Support Ticket Triager

## Principles

### P-01 Language and runtime
Python 3.11 or later. Standard library preferred; external dependencies (google-generativeai, jsonschema) must be listed in pyproject.toml and justified.

### P-02 Lint and style gate
All source code must pass Ruff with no errors and no suppression comments (# noqa). This gate must pass before any implementation is accepted.

### P-03 Security gate
All source code must pass Bandit with severity HIGH findings = 0 and confidence HIGH findings = 0. This gate must pass before any implementation is accepted.

### P-04 Output schema contract first
The JSON output schema (fields, types, enumerations) is defined in the specification and frozen in `src/triager/schema.py` before implementation. The schema is the single source of truth for Layer 1 validation.

### P-05 No secrets
No API keys, passwords or tokens in source, tests, harness scripts or committed files. The Gemini API key lives only in `.env` (gitignored). `.env.example` lists the variable name and an obviously-fake placeholder value.

### P-06 Independent harness
The evaluation harness (`evals/`) and the dataset (`evals/dataset.json`) must not import from `src/triager/` internals. They treat the application as a black box called through a thin runner interface.

### P-07 Protected paths
After the baseline tag, the coding agent must not modify `evals/dataset.json`, `.harness/`, or the `.specify/` artifacts. Changes require a documented specification amendment.

### P-08 Threshold declared before evaluation
The acceptance threshold and scoring formula are written in the specification and in `evals/threshold.json` before the first formal evaluation run. The threshold must not be lowered after evaluation begins.

### P-09 Model and service failures are recorded separately
HTTP 429 / 503 / timeouts are retried up to 3 times and then recorded as a service failure, not counted as a wrong answer.

### P-10 Bounded repair
The repair loop is capped at 2 attempts per cycle. If the harness still fails after 2 attempts, a manual review is conducted.
