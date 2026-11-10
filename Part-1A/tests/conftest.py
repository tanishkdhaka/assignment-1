"""Shared pytest fixtures for the Shopping Cart test suite."""

import pytest

from cart.engine import Cart
from cart.models import Discount, DiscountType

CATALOG: dict[str, Discount] = {
    "SAVE10": Discount(
        code="SAVE10",
        discount_type=DiscountType.PERCENTAGE,
        rate=10.0,
    ),
    "SAVE25": Discount(
        code="SAVE25",
        discount_type=DiscountType.PERCENTAGE,
        rate=25.0,
    ),
    "FLAT5": Discount(
        code="FLAT5",
        discount_type=DiscountType.FIXED_AMOUNT,
        amount=5.0,
        min_subtotal=20.0,
    ),
    "FLAT50": Discount(
        code="FLAT50",
        discount_type=DiscountType.FIXED_AMOUNT,
        amount=50.0,
        min_subtotal=0.0,
    ),
    "BOGO2FOR1_WIDGET": Discount(
        code="BOGO2FOR1_WIDGET",
        discount_type=DiscountType.BOGO,
        buy_qty=2,
        get_qty=1,
        bogo_sku="WIDGET",
    ),
    "BOGO3FOR1_GADGET": Discount(
        code="BOGO3FOR1_GADGET",
        discount_type=DiscountType.BOGO,
        buy_qty=3,
        get_qty=1,
        bogo_sku="GADGET",
    ),
    "FLAT5_MIN20": Discount(
        code="FLAT5_MIN20",
        discount_type=DiscountType.FIXED_AMOUNT,
        amount=5.0,
        min_subtotal=20.0,
    ),
}


@pytest.fixture
def cart() -> Cart:
    """A fresh Cart with the standard test catalog and 10% tax."""
    return Cart(catalog=CATALOG, tax_rate=10.0)


@pytest.fixture
def zero_tax_cart() -> Cart:
    """A Cart with 0% tax for isolating discount calculations."""
    return Cart(catalog=CATALOG, tax_rate=0.0)
