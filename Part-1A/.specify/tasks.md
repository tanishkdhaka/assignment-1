# Tasks — Shopping Cart & Discount Engine

## Task Status Key
- [ ] Pending
- [x] Done
- [~] In progress

---

## T-01 Project setup
**Covers:** FR-06, NFR-01
**Type:** Setup
- [x] Create `pyproject.toml` with ruff, bandit, pytest as dev dependencies.
- [x] Create `src/cart/__init__.py`.
- [x] Verify: `python -m cart --help` produces usage text.

## T-02 Data models
**Covers:** FR-01, FR-03, FR-07, FR-10
**Type:** Agent
- [x] Implement `models.py`: `ErrorCode` enum, `DiscountType` enum, `CartItem` dataclass, `Discount` dataclass, `Result` dataclass.
- [x] All fields typed. No business logic in models.

## T-03 Cart engine — core operations
**Covers:** FR-01, FR-02, AC-001–AC-004, AC-012, AC-014, AC-015, AC-017
**Type:** Agent
- [x] Implement `Cart.__init__(catalog, tax_rate=10.0)`.
- [x] Implement `add_item(sku, name, price, qty) → Result` (validates price > 0, qty > 0).
- [x] Implement `remove_item(sku, qty) → Result`.
- [x] Implement `update_quantity(sku, qty) → Result`.
- [x] Implement `clear() → Result`.
- [x] Implement `subtotal` property.

## T-04 Cart engine — discounts and totals
**Covers:** FR-03, FR-04, FR-05, FR-06, FR-07, AC-005–AC-011, AC-013, AC-018–AC-020
**Type:** Agent
- [x] Implement `apply_discount(coupon_code) → Result` with MINIMUM_NOT_MET guard.
- [x] Implement `discount_total`, `subtotal_after_discounts`, `tax`, `total` properties.
- [x] Clamp `subtotal_after_discounts` to 0.0 (AC-020).

## T-05 Persistence
**Covers:** FR-08, AC-016
**Type:** Agent
- [x] Implement `to_dict()` on `Cart`.
- [x] Implement `Cart.from_dict(d, catalog)` class method.
- [x] Implement `persistence.save_json(cart, path)` and `persistence.load_json(path, catalog)`.

## T-06 CLI
**Covers:** FR-09
**Type:** Agent
- [x] Implement `cli.py` with subcommands: `add`, `remove`, `show`, `apply-discount`, `clear`.
- [x] Each subcommand prints a JSON `Result` to stdout.
- [x] `ok=False` → exit code 1.

## T-07 Tests [Human review required before implementation]
**Covers:** AC-001–AC-020
**Type:** Agent (reviewed by student before marking)
- [x] Write `tests/conftest.py` with fixtures and test catalog.
- [x] Write `tests/test_engine.py` covering AC-001 through AC-020 (at least one test per AC).
- [x] Write `tests/test_persistence.py` for AC-016.
- [x] Write `tests/test_cli.py` for CLI smoke tests.

## T-08 Harness scripts
**Covers:** P-02, P-03, P-04, P-08
**Type:** Agent (self-check run by student)
- [x] Write `.harness/scripts/lint.sh`.
- [x] Write `.harness/scripts/security.sh`.
- [x] Write `.harness/scripts/tests.sh`.
- [x] Write `.harness/harness_runner.py`.
- [x] Write `.harness/scripts/self_check.sh`.

## T-09 Evidence packaging
**Covers:** P-09
**Type:** Human
- [ ] Save first generation in `evidence/initial-generation/` before first formal harness run.
- [ ] Save final generation in `evidence/final-generation/` after last pass.
- [ ] Keep all harness run outputs in `evidence/harness-results/`.

## T-10 Baseline tag
**Covers:** P-08
**Type:** Human
- [ ] After student review: `git tag baseline-part-a-before-implement -m "Harness, tests and spec frozen. N test functions."`.
