# Project Constitution — Shopping Cart & Discount Engine

## Principles

### P-01 Language and runtime
Python 3.11 or later. Standard library preferred; external dependencies must be listed in pyproject.toml and justified.

### P-02 Lint and style gate
All source code must pass Ruff with no errors and no suppression comments (# noqa). This gate must pass before any implementation is accepted.

### P-03 Security gate
All source code must pass Bandit with severity HIGH findings = 0 and confidence HIGH findings = 0. This gate must pass before any implementation is accepted.

### P-04 Test-first with specification as oracle
Tests are derived from numbered acceptance criteria (AC-001 through AC-020). No test may import or read the implementation to decide its expected value; the expected value comes only from the acceptance criteria.

### P-05 No secrets
No API keys, passwords or tokens in source, tests, harness scripts or committed files. Secrets live in .env (gitignored). .env.example lists variable names only.

### P-06 Modular structure
Core logic in src/cart/. CLI entry point in src/cart/__main__.py. Tests in tests/. Harness in .harness/.

### P-07 Error codes
Every failure returns a structured result with an error_code string from the defined enumeration. No bare exceptions bubble to the user; all are caught and mapped.

### P-08 Protected paths
The coding agent must not modify tests/, .harness/, or the .specify/ artifacts after the baseline tag is set. Changes to those paths require a documented specification amendment.

### P-09 Save first generation
The first output of the coding agent is saved unchanged in evidence/initial-generation/ before the first formal harness run.

### P-10 Bounded repair
The repair loop is capped at 2 attempts per cycle. If the harness still fails after 2 attempts, a manual review is conducted before proceeding.
