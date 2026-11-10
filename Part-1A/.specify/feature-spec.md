# Feature Specification — Shopping Cart & Discount Engine

## 1. Overview
A Python library and CLI for managing a shopping cart with configurable discount rules and tax calculation. Designed for deterministic, fully-testable behaviour.

## 2. Users
Developers integrating a cart module; students demonstrating spec-driven development.

## 3. User Stories
US-001: As a developer, I want to add products to the cart so that I can build an order.
US-002: As a developer, I want to remove or update quantities so that I can correct mistakes.
US-003: As a developer, I want to apply discount coupons so that promotional pricing is reflected.
US-004: As a developer, I want BOGO discounts applied per-SKU so that volume promotions work.
US-005: As a developer, I want tax calculated after discounts so that the total is legally correct.
US-006: As a developer, I want to save and restore cart state to JSON so that sessions can persist.
US-007: As a developer, I want structured error codes so that callers can handle failures programmatically.

## 4. Functional Requirements
FR-01: Cart maintains a list of CartItems (SKU, name, unit_price, quantity).
FR-02: Cart supports add_item, remove_item, update_quantity, clear, apply_discount, remove_discount operations.
FR-03: Discount types: PERCENTAGE (rate 0–100), FIXED_AMOUNT (amount > 0, min_subtotal >= 0), BOGO (buy_qty, get_qty, sku).
FR-04: At most one PERCENTAGE or FIXED_AMOUNT discount may be active simultaneously; BOGO discounts are independent.
FR-05: Tax rate is a constructor parameter (default 10.0%). Tax = round(subtotal_after_discounts * tax_rate / 100, 2).
FR-06: subtotal = sum(item.unit_price * item.quantity) for all items.
FR-07: discount_total = percentage/fixed discount amount + sum of BOGO savings. Capped so subtotal_after_discounts >= 0.
FR-08: Cart serialises to/from JSON via to_dict() / from_dict().
FR-09: CLI commands: add, remove, show, apply-discount, clear, save, load.
FR-10: All operations return a Result object with ok: bool, data: dict|None, error_code: str|None.

## 5. Non-Functional Requirements
NFR-01: Pure Python standard library for core logic (json, dataclasses, enum, decimal or float with round()).
NFR-02: Ruff and Bandit pass with zero findings on all src/ files.
NFR-03: All 20 acceptance criteria have passing tests before acceptance.
NFR-04: JSON save/load is round-trip exact (no floating-point drift beyond 2 dp).

## 6. Acceptance Criteria
(See constitution §P-04 and the full numbered list AC-001–AC-020 in tasks.md)

## 7. Error Codes
| Code | Meaning |
|---|---|
| ITEM_NOT_FOUND | SKU not in cart |
| INVALID_COUPON | Coupon code not in catalog |
| INVALID_PRICE | price <= 0 |
| INVALID_QUANTITY | quantity <= 0 |
| MINIMUM_NOT_MET | Cart subtotal below discount minimum |

## 8. Out of Scope
- Authentication or user accounts
- Persistent product catalog (catalog is passed in at call time)
- Currency conversion
- UI beyond CLI
- Networking

## 9. Assumptions
- Prices are floats rounded to 2 decimal places throughout.
- The coupon catalog is a dict passed into the Cart constructor.
- BOGO free items are the cheapest units of that SKU (since all units have the same price, savings = get_qty * unit_price per buy cycle).
