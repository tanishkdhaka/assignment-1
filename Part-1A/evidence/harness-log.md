# Harness Log — Part 1A: Shopping Cart & Discount Engine

> **Notice for the student:** As required by the academic integrity policy [Brief §2], this scaffold provides the verified facts, execution evidence, and section structure. The narrative entries and human acceptance decision must be written by you in your own words.

---

## 1. Environment & Setup Facts (Verified)

| Property | Value | Source |
|---|---|---|
| Operating System | macOS (Darwin 24.x, arm64) | `uname -a` |
| Python Runtime | Python 3.13.2 | `python3 --version` |
| Test Framework | pytest 9.2.0 | `pytest --version` |
| Static Linter | Ruff 0.9.x | `ruff --version` |
| Security Scanner | Bandit 1.8.x | `bandit --version` |
| Spec Kit CLI | specify-cli 1.3.3 | `specify --version` |
| Test Count | 35 passed, 0 failed | `pytest tests/ -v` |
| Execution Time | ~0.25 seconds | `harness_runner.py` output |

---

## 2. Initial Generation & Specification Context

### Specification & Task References
- **Constitution:** `.specify/constitution.md` (Principles P-01 to P-10)
- **Specification:** `.specify/feature-spec.md` (FR-01 to FR-10, AC-001 to AC-020)
- **Clarifications:** `.specify/clarifications.md` (CLR-001 to CLR-006)
- **Technical Plan:** `.specify/technical-plan.md` (ADR-001 to ADR-004)
- **Tasks:** `.specify/tasks.md` (T-01 to T-10)

### Initial Generation Evidence
- Preserved at: `evidence/initial-generation/`
- Timestamp: 2026-11-10T21:50:02Z
- Files generated: `src/cart/models.py`, `src/cart/engine.py`, `src/cart/persistence.py`, `src/cart/cli.py`, `src/cart/__main__.py`, `tests/`

---

## 3. Harness Execution & Failure-and-Repair Cycle

### Run 1: Initial Harness Execution (FAILURE)
- **Timestamp:** 2026-11-10T21:50:09Z
- **Raw outputs:** `evidence/harness-results/run-1/`
  - `lint_output.txt` (35 ruff errors)
  - `security_output.txt` (Bandit: 0 issues)
  - `tests_output.txt` (pytest: ModuleNotFoundError on `cart`)
- **Structured feedback record:** `evidence/harness-results/run-1/feedback.json`

#### Summary of Findings Detected by the Harness:
1. **Linter findings (Ruff):**
   - `F401`: Unused import `field` from `dataclasses` in `src/cart/models.py:5`.
   - `UP037`: Quoted type annotation `"Cart"` in `src/cart/engine.py:225` when `from __future__ import annotations` was in use.
   - `UP042`: Enum classes `ErrorCode` and `DiscountType` inheriting from `(str, Enum)` instead of modern Python 3.11+ `StrEnum`.
   - `N802`: Test function names `test_AC_*` had uppercase characters violating PEP 8 naming conventions.
2. **Dynamic test runner findings (Pytest):**
   - Missing `pythonpath = ["src"]` in `pyproject.toml`, resulting in `ModuleNotFoundError: No module named 'cart'` when tests ran without an editable install.
   - In `pyproject.toml`, build backend was specified as `setuptools.backends.legacy:BuildBackend` which failed pip editable install.
   - In `tests/test_cli.py`, subprocess execution did not inherit `PYTHONPATH`, failing CLI execution in isolated temporary directories.

---

### Repair Actions Applied:
1. `src/cart/models.py`: Removed unused import `field`, updated `ErrorCode` and `DiscountType` to inherit from `StrEnum`.
2. `src/cart/engine.py`: Replaced `"Cart"` type annotation with `Cart`.
3. `tests/test_engine.py` & `tests/test_persistence.py`: Renamed `test_AC_*` to `test_ac_*`, removed unused `pytest` import.
4. `pyproject.toml`: Corrected build backend to `setuptools.build_meta`, added `pythonpath = ["src"]` to pytest configuration.
5. `tests/test_cli.py`: Passed `PYTHONPATH` containing `src/` to subprocess environments.

---

### Run 2: Re-execution After Repair (PASS)
- **Timestamp:** 2026-11-10T21:52:58Z
- **Report file:** `evidence/harness-results/harness_20261110T162258Z.json`
- **Results:**
  - `lint` (Ruff): **PASS** (0 findings)
  - `security` (Bandit): **PASS** (0 findings at `-ll` severity/confidence)
  - `tests` (Pytest): **PASS** (35 passed in 0.23s)
  - `self_check.sh`: **PASS** (verified that lint and test gates detect failures on deliberately broken fakes)

---

## 4. Student Narrative: Failure & Repair Reflection
*(Write 1–2 paragraphs in your own words describing: what broke in the first run, how the harness findings guided the repair, and how you verified that the fix resolved the root cause without weakening any test or gate.)*

[STUDENT TO WRITE]

---

## 5. Human Acceptance Decision & Limitations

### Decision: [ACCEPT / REJECT]
*(Choose one and sign off with your name and date.)*

- **Decision:** [e.g., ACCEPT]
- **Reviewer:** [Student Name]
- **Date:** [Date]

### Justification:
*(Explain why you made this decision based on the automated harness evidence above.)*

[STUDENT TO WRITE]

### Known Limitations & Residual Risks:
*(Identify at least one limitation or edge case not fully covered by the automated tests, e.g., currency rounding with fractional pennies across hundreds of stacked items, or multi-threaded cart access.)*

[STUDENT TO WRITE]
