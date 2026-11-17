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

The first harness run on the initial generated implementation failed on both the static and dynamic gates. The Ruff linter reported 35 findings: `F401` for an unused `field` import in `models.py`, `UP042` because the `ErrorCode` and `DiscountType` enums inherited from `(str, Enum)` instead of the modern `StrEnum` available in Python 3.11+, `UP037` for a quoted type annotation `"Cart"` in `engine.py` that was unnecessary given the `from __future__ import annotations` already in scope, and `N802` violations across all test functions whose names followed the pattern `test_AC_*` with uppercase letters. The pytest runner also crashed before running a single test because `pythonpath = ["src"]` was absent from `pyproject.toml`, causing a `ModuleNotFoundError: No module named 'cart'` when the test suite tried to import the application.

The harness findings from Run 1 were fed back as a structured `feedback.json` document that mapped each finding code to the violated principle in the constitution (P-02 for lint, P-04 for test isolation). The repair addressed each finding at its root: `StrEnum` was used instead of patching the inheritance tuple, function names were renamed to `test_ac_*` throughout, the unused import was removed, and `pythonpath` was added to `pyproject.toml`. Crucially, no test was deleted or weakened — the same 35 assertions still ran. Run 2 produced a clean PASS on all three gates (Ruff 0 findings, Bandit 0 findings, Pytest 35/35) confirming the repairs solved the root causes without compromising the harness bar.

---

## 5. Human Acceptance Decision & Limitations

### Decision: ACCEPT

- **Decision:** ACCEPT
- **Reviewer:** Tanishk Dhaka
- **Date:** 2026-11-17

### Justification:

The automated harness completed two full runs: Run 1 exposed genuine defects (Ruff findings and a broken import path) which were repaired through a documented feedback cycle; Run 2 passed all three gates — lint, security SAST, and 35 unit/contract tests covering all 20 acceptance criteria — with zero suppressions or test deletions. The evidence trail from `evidence/harness-results/run-1/` to `evidence/harness-results/harness_20261110T162258Z.json` is complete and unedited. On this basis I accept the implementation as meeting the specified engineering bar.

### Known Limitations & Residual Risks:

The harness does not cover concurrent or multi-threaded access to the JSON persistence layer. If two processes write the cart file simultaneously, the last write wins and earlier changes are silently lost. Additionally, the discount engine truncates intermediate floating-point values using Python's default IEEE 754 arithmetic; for large carts with many BOGO line items, cumulative rounding errors of up to ±$0.01 per line are possible but not asserted. These residual risks were accepted for this academic context but would require a database-backed persistence layer and decimal-precision arithmetic (`decimal.Decimal`) before production deployment.
