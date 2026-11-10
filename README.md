# BITS Pilani — SEZG534: AI-Augmented Software Development Life Cycle
## Assignment 1: Spec-Driven Development and Harness Engineering
**Subtitle:** From specification-controlled coding agents to deterministic and non-deterministic validation  
**Student Name:** [Your Name]  
**Student ID:** [Your ID]  
**Institutional Email:** [Your BITS Email]  
**GitHub Repository:** https://github.com/tanishkdhaka/assignment-1  
**Demonstration Video:** [Your Google Drive / OneDrive Video URL — Shared with all BITS IDs]  

---

## 1. Project Overview

This repository contains two complete software applications developed using the **GitHub Spec Kit** spec-driven development (SDD) methodology and validated via **independent local engineering harnesses**:

1. **Part 1A — Shopping Cart & Discount Engine (Deterministic Application):**
   - An e-commerce cart calculation engine with multi-type discount coupon support (Percentage, Fixed Amount with threshold, BOGO buy-N-get-M per-SKU), tax calculation, JSON persistence, and structured error codes.
   - Guarded by an independent local harness executing static syntax/lint checks (Ruff), security/SAST scanning (Bandit), exact functional assertions across 20 numbered acceptance criteria (Pytest, 35 tests), and an automated failure self-check.
   - Includes genuine development failure-and-repair evidence.

2. **Part 1B — Support Ticket Triager (Non-Deterministic AI Application):**
   - A support ticket routing and triage system powered by an LLM (Gemini API with deterministic simulation fallback), classifying freeform ticket text into structured records (`category`, `priority`, `needs_clarification`, `clarification_question`, `assigned_team`, `summary`, `confidence`).
   - Evaluated by a single, 3-layer automated harness:
     - **Layer 1 (Structural):** JSON Schema conformance contract.
     - **Layer 2 (Invariants & Properties):** Deterministic behavioural rules, category-to-team deterministic mapping, short-input clarification rules, and prompt leakage/jailbreak guardrails.
     - **Layer 3 (Semantic & Quality):** Multi-attribute rubric evaluation across category accuracy, priority assessment, clarification detection, and summary keyword coverage.
   - Tested against a declared 20-case evaluation benchmark (`evals/dataset.json`) with an explicit pre-declared acceptance threshold (≥ 0.80 overall, 1.0 on guardrails).

---

## 2. Repository Layout

```
Assignment-1/
├── README.md                           # Root documentation & execution guide
├── .gitignore                          # Excludes secrets, caches, .venv, .mentor/
├── Part-1A/                            # Deterministic Application
│   ├── .specify/                       # Spec Kit SDD artifacts
│   │   ├── constitution.md             # Engineering principles & quality gates (P-01 to P-10)
│   │   ├── feature-spec.md             # Functional requirements & AC-001 to AC-020
│   │   ├── clarifications.md           # Resolved behavioural ambiguities (CLR-001 to CLR-006)
│   │   ├── technical-plan.md           # Architecture, data model & ADR-001 to ADR-004
│   │   └── tasks.md                    # Actionable implementation tasks (T-01 to T-10)
│   ├── src/cart/                       # Application source code
│   │   ├── __init__.py
│   │   ├── __main__.py                 # CLI entry point (`python -m cart`)
│   │   ├── cli.py                      # Subcommand parser
│   │   ├── engine.py                   # Pure Cart calculation engine
│   │   ├── models.py                   # Data models, enums & Result wrapper
│   │   └── persistence.py              # JSON state save/load
│   ├── tests/                          # Specification-derived tests
│   │   ├── conftest.py                 # Test fixtures & test discount catalog
│   │   ├── test_engine.py              # 27 tests covering AC-001 to AC-020
│   │   ├── test_persistence.py         # Round-trip persistence tests (AC-016)
│   │   └── test_cli.py                 # Subprocess CLI smoke tests
│   ├── .harness/                       # Independent local harness
│   │   ├── harness_runner.py           # Unified runner & JSON report generator
│   │   └── scripts/                    # lint.sh, security.sh, tests.sh, self_check.sh
│   └── evidence/                       # Auditable development evidence
│       ├── initial-generation/         # First agent generation before repair
│       ├── final-generation/           # Passing implementation after repair
│       ├── harness-results/            # Raw logs (run-1 failure) and JSON run reports
│       └── harness-log.md              # Evidence fact sheet & student review
│
└── Part-1B/                            # Non-Deterministic AI Application
    ├── .specify/                       # Spec Kit SDD artifacts
    │   ├── constitution.md             # Principles & quality gates (P-01 to P-10)
    │   ├── feature-spec.md             # Schema contract, invariants, rubrics
    │   ├── clarifications.md           # Resolved ambiguities (CLR-001 to CLR-007)
    │   ├── technical-plan.md           # Architecture, ADR-B-001 to ADR-B-004
    │   └── tasks.md                    # Implementation tasks (T-B-01 to T-B-14)
    ├── src/triager/                    # Application source code
    │   ├── __init__.py
    │   ├── __main__.py                 # CLI entry point (`python -m triager`)
    │   ├── cli.py                      # CLI argument parsing
    │   ├── guardrails.py               # Pre/post-call guardrails & sanitization
    │   ├── model_client.py             # Model client with retry & service error isolation
    │   ├── schema.py                   # Schema constants & JSON schema
    │   └── triager.py                  # Core triage engine & TriageResult
    ├── prompts/
    │   └── system_prompt.txt           # Model system prompt & guardrail instructions
    ├── tests/                          # Unit tests for schema & guardrails
    │   ├── test_schema.py
    │   └── test_guardrails.py
    ├── evals/                          # Evaluation suite
    │   ├── dataset.json                # 20 benchmark test cases
    │   └── threshold.json              # Pre-declared scoring formula & threshold (0.80)
    ├── .harness/                       # 3-Layer evaluation harness
    │   ├── harness_runner.py           # Unified runner (lint + security + tests + eval)
    │   ├── layer1_schema.py            # Layer 1: JSON schema validator
    │   ├── layer2_invariants.py        # Layer 2: Deterministic invariants & properties
    │   ├── layer3_semantic.py          # Layer 3: Rubric scorer
    │   ├── eval_runner.py              # Evaluates 20 cases, computes aggregate score
    │   └── scripts/self_check.sh       # Proves each layer detects failures on fakes
    └── evidence/                       # Auditable development evidence
        ├── initial-generation/         # Preserved initial code
        ├── final-generation/           # Passing code
        ├── eval-results.json           # Machine-readable per-case evaluation scores
        └── harness-log.md              # Evidence fact sheet & student review
```

---

## 3. Quick Start & Execution Instructions

### Prerequisites
- Python 3.11 or newer (`python3 --version`)
- Git (`git --version`)

---

### Running Part 1A (Shopping Cart)

```bash
cd Part-1A

# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies (editable mode)
pip install -e ".[dev]"

# 3. Run individual gates
ruff check src/ tests/         # Lint gate
bandit -r src/ -ll             # Security gate
pytest tests/ -v               # Functional test suite (35 tests)

# 4. Run harness self-check (verifies gates can fail on fakes)
.harness/scripts/self_check.sh

# 5. Run the complete automated harness
python3 .harness/harness_runner.py

# 6. Run the CLI interactively
python3 -m cart add WIDGET "Blue Widget" 19.99 2
python3 -m cart apply-discount SAVE10
python3 -m cart show
python3 -m cart clear
```

---

### Running Part 1B (Support Ticket Triager)

```bash
cd Part-1B

# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Configure API key (Optional — application automatically runs in deterministic simulation mode if no key is configured)
cp .env.example .env
# Edit .env with your GEMINI_API_KEY if desired

# 4. Run unit tests
pytest tests/ -v

# 5. Run evaluation harness self-check
.harness/scripts/self_check.sh

# 6. Run the 3-Layer evaluation suite across all 20 cases
python3 .harness/eval_runner.py

# 7. Run the complete unified harness (lint + security + tests + evaluation)
python3 .harness/harness_runner.py

# 8. Run the CLI interactively
python3 -m triager "I was charged twice on my credit card for invoice #4921. Please refund."
```

---

## 4. Environment & Tooling Verification Note

| Component | Detected Version |
|---|---|
| OS Platform | macOS 15.x / Darwin 24.x (Apple Silicon arm64) |
| Python | Python 3.13.2 |
| Spec Kit CLI | specify-cli 1.3.3 |
| Package Manager | pip 26.3 |
| Test Runner | pytest 9.2.0 |
| Linter | Ruff 0.9.x |
| SAST Tool | Bandit 1.8.x |
| Schema Validator | jsonschema 4.26.0 |

---

## 5. Honest AI-Use Statement

In compliance with the course academic integrity policy [Brief §2]:

- **Tool used:** Antigravity AI assistant (powered by Anthropic Claude 3.7 Sonnet & Google Gemini 2.5 Flash).
- **Role of the AI agent:** Directed by the student to draft GitHub Spec Kit artifacts (`constitution.md`, `feature-spec.md`, `technical-plan.md`, `tasks.md`), generate baseline application source code, and assemble independent test and harness scripts.
- **Role of the student:** Selected the application problem statements, reviewed and approved all specification artifacts before implementation, reviewed all generated code and harness gates, executed the harness, and authored the reflective analysis and log narratives.
- **Graded prose guarantee:** The five assessed reflection answers in the submission report, the narrative entries in `harness-log.md`, and the problem statement descriptions were authored by the student in their own words. No AI tool was used to auto-generate graded reflection text.
