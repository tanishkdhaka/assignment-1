"""
Specification-derived tests for the Cart engine.

Each test maps to one or more acceptance criteria (AC-NNN).
Expected values are computed from the specification, never from the implementation.
"""

import pytest

from cart.engine import Cart
from cart.models import ErrorCode

# ---------------------------------------------------------------------------
# AC-001: Adding a valid item returns a cart with that item
# ---------------------------------------------------------------------------


def test_AC_001_add_valid_item(cart: Cart) -> None:
    result = cart.add_item("WIDGET", "Blue Widget", 9.99, 1)
    assert result.ok is True
    assert result.error_code is None
    items = result.data["items"]
    assert len(items) == 1
    assert items[0]["sku"] == "WIDGET"
    assert items[0]["unit_price"] == 9.99
    assert items[0]["quantity"] == 1


# ---------------------------------------------------------------------------
# AC-002: Adding the same SKU twice accumulates quantity
# ---------------------------------------------------------------------------


def test_AC_002_add_same_sku_accumulates(cart: Cart) -> None:
    cart.add_item("WIDGET", "Blue Widget", 9.99, 2)
    result = cart.add_item("WIDGET", "Blue Widget", 9.99, 3)
    assert result.ok is True
    items = result.data["items"]
    assert items[0]["quantity"] == 5


# ---------------------------------------------------------------------------
# AC-003: Removing items (qty >= remaining clears; partial decrements)
# ---------------------------------------------------------------------------


def test_AC_003_remove_more_than_available_clears_item(cart: Cart) -> None:
    cart.add_item("WIDGET", "Blue Widget", 9.99, 2)
    result = cart.remove_item("WIDGET", 10)
    assert result.ok is True
    assert result.data["items"] == []


def test_AC_003_remove_exact_quantity_clears_item(cart: Cart) -> None:
    cart.add_item("WIDGET", "Blue Widget", 9.99, 2)
    result = cart.remove_item("WIDGET", 2)
    assert result.ok is True
    assert result.data["items"] == []


def test_AC_003_remove_partial_quantity_decrements(cart: Cart) -> None:
    cart.add_item("WIDGET", "Blue Widget", 9.99, 5)
    result = cart.remove_item("WIDGET", 2)
    assert result.ok is True
    assert result.data["items"][0]["quantity"] == 3


# ---------------------------------------------------------------------------
# AC-004: Removing a non-existent SKU returns ITEM_NOT_FOUND
# ---------------------------------------------------------------------------


def test_AC_004_remove_nonexistent_sku(cart: Cart) -> None:
    result = cart.remove_item("NOSUCHSKU", 1)
    assert result.ok is False
    assert result.error_code == ErrorCode.ITEM_NOT_FOUND


# ---------------------------------------------------------------------------
# AC-005: PERCENTAGE discount reduces subtotal by exactly P%
# ---------------------------------------------------------------------------


def test_AC_005_percentage_discount(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("WIDGET", "Blue Widget", 9.99, 2)
    result = zero_tax_cart.apply_discount("SAVE10")
    assert result.ok is True
    # subtotal = 19.98; 10% = 1.998 → rounds to 2.00
    assert result.data["discount_total"] == 2.00
    assert result.data["subtotal_after_discounts"] == 17.98


def test_AC_005_percentage_25_percent(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 20.00, 1)
    zero_tax_cart.apply_discount("SAVE25")
    snapshot = zero_tax_cart._snapshot()
    # 25% of 20.00 = 5.00
    assert snapshot["discount_total"] == 5.00
    assert snapshot["subtotal_after_discounts"] == 15.00


# ---------------------------------------------------------------------------
# AC-006: FIXED_AMOUNT discount reduces subtotal by exactly F when >= min
# ---------------------------------------------------------------------------


def test_AC_006_fixed_amount_discount(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 30.00, 1)
    result = zero_tax_cart.apply_discount("FLAT5")
    assert result.ok is True
    assert result.data["discount_total"] == 5.00
    assert result.data["subtotal_after_discounts"] == 25.00


# ---------------------------------------------------------------------------
# AC-007: FIXED_AMOUNT when subtotal < minimum returns MINIMUM_NOT_MET
# ---------------------------------------------------------------------------


def test_AC_007_fixed_minimum_not_met(cart: Cart) -> None:
    cart.add_item("ITEM", "Item", 10.00, 1)  # subtotal £10, min £20
    result = cart.apply_discount("FLAT5")
    assert result.ok is False
    assert result.error_code == ErrorCode.MINIMUM_NOT_MET


# ---------------------------------------------------------------------------
# AC-008: Second PERCENTAGE or FIXED_AMOUNT replaces the first
# ---------------------------------------------------------------------------


def test_AC_008_second_percentage_replaces_first(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 100.00, 1)
    zero_tax_cart.apply_discount("SAVE10")  # 10% → saves £10
    zero_tax_cart.apply_discount("SAVE25")  # 25% → saves £25
    snapshot = zero_tax_cart._snapshot()
    assert snapshot["discount_total"] == 25.00
    assert "SAVE25" in snapshot["active_discounts"]
    assert "SAVE10" not in snapshot["active_discounts"]


def test_AC_008_fixed_replaces_percentage(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 100.00, 1)
    zero_tax_cart.apply_discount("SAVE10")
    zero_tax_cart.apply_discount("FLAT50")  # FLAT50: £50 off, no minimum
    snapshot = zero_tax_cart._snapshot()
    assert snapshot["discount_total"] == 50.00


# ---------------------------------------------------------------------------
# AC-009: BOGO(buy=2, get=1) — free units = floor(qty / buy_qty) * get_qty
# ---------------------------------------------------------------------------


def test_AC_009_bogo_basic(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("WIDGET", "Blue Widget", 10.00, 5)
    result = zero_tax_cart.apply_discount("BOGO2FOR1_WIDGET")
    assert result.ok is True
    # floor(5/2)=2 free, savings = 2 * 10.00 = 20.00
    assert result.data["discount_total"] == 20.00
    assert result.data["subtotal_after_discounts"] == 30.00


def test_AC_009_bogo_exact_multiple(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("WIDGET", "Blue Widget", 10.00, 4)
    zero_tax_cart.apply_discount("BOGO2FOR1_WIDGET")
    # floor(4/2)=2 free → saves 20.00
    assert zero_tax_cart.discount_total == 20.00


# ---------------------------------------------------------------------------
# AC-010: BOGO stacks with PERCENTAGE or FIXED discount
# ---------------------------------------------------------------------------


def test_AC_010_bogo_stacks_with_percentage(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("WIDGET", "Blue Widget", 10.00, 5)
    zero_tax_cart.apply_discount("SAVE10")  # 10% of 50 = 5
    zero_tax_cart.apply_discount("BOGO2FOR1_WIDGET")  # saves 20
    snapshot = zero_tax_cart._snapshot()
    assert snapshot["discount_total"] == 25.00
    assert snapshot["subtotal_after_discounts"] == 25.00
    assert "SAVE10" in snapshot["active_discounts"]
    assert "BOGO2FOR1_WIDGET" in snapshot["active_discounts"]


# ---------------------------------------------------------------------------
# AC-011: Tax at T% applied to subtotal_after_discounts
# ---------------------------------------------------------------------------


def test_AC_011_tax_on_discounted_subtotal(cart: Cart) -> None:
    cart.add_item("ITEM", "Item", 100.00, 1)
    cart.apply_discount("SAVE10")  # saves 10.00; after discount 90.00
    # tax = 90 * 10% = 9.00; total = 99.00
    assert cart.tax == 9.00
    assert cart.total == 99.00


def test_AC_011_tax_rounding(cart: Cart) -> None:
    # subtotal_after_discounts = 19.99; 10% tax = 1.999 → rounds to 2.00
    cart.add_item("ITEM", "Item", 19.99, 1)
    # no discount
    assert cart.tax == 2.00
    assert cart.total == 21.99


# ---------------------------------------------------------------------------
# AC-012: Empty cart returns all zeros
# ---------------------------------------------------------------------------


def test_AC_012_empty_cart_all_zeros(cart: Cart) -> None:
    assert cart.subtotal == 0.00
    assert cart.discount_total == 0.00
    assert cart.tax == 0.00
    assert cart.total == 0.00


# ---------------------------------------------------------------------------
# AC-013: Unknown coupon code returns INVALID_COUPON
# ---------------------------------------------------------------------------


def test_AC_013_invalid_coupon(cart: Cart) -> None:
    result = cart.apply_discount("NOSUCHCODE")
    assert result.ok is False
    assert result.error_code == ErrorCode.INVALID_COUPON


# ---------------------------------------------------------------------------
# AC-014: price <= 0 returns INVALID_PRICE
# ---------------------------------------------------------------------------


def test_AC_014_invalid_price_zero(cart: Cart) -> None:
    result = cart.add_item("SKU1", "Item", 0.0, 1)
    assert result.ok is False
    assert result.error_code == ErrorCode.INVALID_PRICE


def test_AC_014_invalid_price_negative(cart: Cart) -> None:
    result = cart.add_item("SKU1", "Item", -5.0, 1)
    assert result.ok is False
    assert result.error_code == ErrorCode.INVALID_PRICE


# ---------------------------------------------------------------------------
# AC-015: quantity <= 0 returns INVALID_QUANTITY
# ---------------------------------------------------------------------------


def test_AC_015_invalid_quantity_zero(cart: Cart) -> None:
    result = cart.add_item("SKU1", "Item", 10.00, 0)
    assert result.ok is False
    assert result.error_code == ErrorCode.INVALID_QUANTITY


def test_AC_015_invalid_quantity_negative(cart: Cart) -> None:
    result = cart.add_item("SKU1", "Item", 10.00, -3)
    assert result.ok is False
    assert result.error_code == ErrorCode.INVALID_QUANTITY


# ---------------------------------------------------------------------------
# AC-017: Clearing the cart removes items and resets discounts
# ---------------------------------------------------------------------------


def test_AC_017_clear_removes_items_and_discounts(cart: Cart) -> None:
    cart.add_item("WIDGET", "Widget", 10.00, 3)
    cart.apply_discount("SAVE10")
    result = cart.clear()
    assert result.ok is True
    assert result.data["items"] == []
    assert result.data["subtotal"] == 0.00
    assert result.data["active_discounts"] == []


# ---------------------------------------------------------------------------
# AC-018: FIXED_AMOUNT at exact minimum is accepted
# ---------------------------------------------------------------------------


def test_AC_018_fixed_discount_at_exact_minimum(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 20.00, 1)  # exactly at minimum
    result = zero_tax_cart.apply_discount("FLAT5")
    assert result.ok is True
    assert result.data["discount_total"] == 5.00


# ---------------------------------------------------------------------------
# AC-019: BOGO with qty below buy threshold → 0 free items
# ---------------------------------------------------------------------------


def test_AC_019_bogo_below_threshold(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("WIDGET", "Blue Widget", 10.00, 1)
    result = zero_tax_cart.apply_discount("BOGO2FOR1_WIDGET")
    assert result.ok is True
    assert result.data["discount_total"] == 0.00


# ---------------------------------------------------------------------------
# AC-020: Total cannot be negative; clamped to 0
# ---------------------------------------------------------------------------


def test_AC_020_total_cannot_be_negative(zero_tax_cart: Cart) -> None:
    zero_tax_cart.add_item("ITEM", "Item", 10.00, 1)
    zero_tax_cart.apply_discount("FLAT50")  # £50 off, no min; would go negative
    assert zero_tax_cart.subtotal_after_discounts == 0.00
    assert zero_tax_cart.tax == 0.00
    assert zero_tax_cart.total == 0.00
    # discount_total is capped at subtotal (10.00), not 50.00
    assert zero_tax_cart.discount_total == 10.00
