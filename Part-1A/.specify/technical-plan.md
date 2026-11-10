# Technical Plan — Shopping Cart & Discount Engine

## Architecture

Single Python package `src/cart/` with no third-party runtime dependencies.

```
src/cart/
  __init__.py       — public API re-exports
  models.py         — dataclasses: ErrorCode, DiscountType, CartItem, Discount, Result
  engine.py         — Cart class (pure logic, no I/O)
  persistence.py    — save_json / load_json
  cli.py            — argparse CLI, calls engine and persistence
  __main__.py       — `python -m cart` entry point
tests/
  conftest.py       — shared fixtures and test catalog
  test_engine.py    — AC-001 through AC-020
  test_persistence.py — AC-016 round-trip
  test_cli.py       — CLI smoke tests
.harness/
  harness_runner.py — orchestrates all gates, writes JSON report
  scripts/
    lint.sh         — ruff check src/ tests/
    security.sh     — bandit -r src/
    tests.sh        — pytest tests/ -v
    self_check.sh   — deliberately broken fakes, proves gates fail
```

## Architectural Decisions

### ADR-001: Standard library data models (not Pydantic)
**Decision:** Use Python `dataclasses` and `enum` from the standard library.
**Alternatives considered:** Pydantic v2 (adds validation at construction).
**Reason:** Constitution P-01 requires standard library first; validation belongs in `Cart` logic, not the data model, so Pydantic adds no value here.

### ADR-002: float + round(x, 2) (not Decimal)
**Decision:** Store prices and totals as `float`, round every computed output to 2 decimal places at the boundary.
**Alternatives considered:** `decimal.Decimal` with `ROUND_HALF_UP`.
**Reason:** Simpler code; all values are stored and returned as 2-dp floats, so test assertions are exact. Risk of intermediate drift is mitigated by rounding at every property boundary.

### ADR-003: Result wrapper pattern
**Decision:** Every public Cart method returns `Result(ok, data, error_code)`.
**Alternatives considered:** Raising Python exceptions; returning `None` on failure.
**Reason:** Structured error codes (FR-10, P-07) without exceptions crossing the library API boundary. The CLI maps `ok=False` to exit code 1.

### ADR-004: Coupon catalog injected at Cart construction
**Decision:** `Cart(catalog: dict[str, Discount])` receives the catalog from the caller.
**Alternatives considered:** A singleton global catalog; a file-based catalog loaded at startup.
**Reason:** Testability — tests supply their own catalog without touching any file. The CLI provides a default catalog for interactive use.

## Data Flow

```
CLI args
  → cart.cli.cmd_*()
    → Cart.add_item / apply_discount / ...
      → Result(ok, data, error_code)
    → save_json / load_json
  → stdout (JSON)
```

## Testing Strategy

- One test function per AC, named `test_AC_NNN_description`.
- Expected values computed from the specification text, never from the implementation.
- CLI tests use `subprocess.run` so they test the full call stack.
- Persistence tests use `tempfile.NamedTemporaryFile` for isolation.

## Dependency Summary

| Package | Role | Why needed |
|---|---|---|
| pytest >= 8 | Test runner | Standard Python testing |
| ruff >= 0.9 | Lint/style | Harness gate P-02 |
| bandit[toml] >= 1.8 | SAST | Harness gate P-03 |
