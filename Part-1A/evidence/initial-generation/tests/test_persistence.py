"""Persistence tests — AC-016: JSON save/load is a round-trip."""

import json
import tempfile
from pathlib import Path

from cart.engine import Cart
from cart.models import Discount, DiscountType
from cart.persistence import load_json, save_json

CATALOG: dict[str, Discount] = {
    "SAVE10": Discount(
        code="SAVE10",
        discount_type=DiscountType.PERCENTAGE,
        rate=10.0,
    ),
    "BOGO2FOR1_WIDGET": Discount(
        code="BOGO2FOR1_WIDGET",
        discount_type=DiscountType.BOGO,
        buy_qty=2,
        get_qty=1,
        bogo_sku="WIDGET",
    ),
}


def _make_cart() -> Cart:
    c = Cart(catalog=CATALOG, tax_rate=10.0)
    c.add_item("WIDGET", "Blue Widget", 9.99, 3)
    c.add_item("GADGET", "Gadget", 24.99, 1)
    c.apply_discount("SAVE10")
    c.apply_discount("BOGO2FOR1_WIDGET")
    return c


def test_AC_016_round_trip_preserves_items() -> None:
    original = _make_cart()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)

    save_result = save_json(original, path)
    assert save_result.ok

    load_result = load_json(path, catalog=CATALOG)
    assert load_result.ok
    restored: Cart = load_result.data["cart"]

    assert restored.subtotal == original.subtotal
    assert restored.discount_total == original.discount_total
    assert restored.total == original.total


def test_AC_016_saved_file_is_valid_json() -> None:
    original = _make_cart()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    save_json(original, path)
    raw = path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)
    assert "items" in parsed
    assert "tax_rate" in parsed


def test_AC_016_restored_cart_matches_items() -> None:
    original = _make_cart()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    save_json(original, path)
    load_result = load_json(path, catalog=CATALOG)
    restored: Cart = load_result.data["cart"]
    orig_skus = {i.sku for i in original._items.values()}
    rest_skus = {i.sku for i in restored._items.values()}
    assert orig_skus == rest_skus
