"""Data models for the Shopping Cart & Discount Engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Structured error codes returned by Cart operations."""

    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"
    INVALID_COUPON = "INVALID_COUPON"
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    MINIMUM_NOT_MET = "MINIMUM_NOT_MET"


class DiscountType(StrEnum):
    """Types of discount supported."""

    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    BOGO = "BOGO"


@dataclass
class Product:
    """A product available for addition to the cart."""

    sku: str
    name: str
    unit_price: float
    category: str = "general"


@dataclass
class CartItem:
    """A product line in the cart."""

    sku: str
    name: str
    unit_price: float
    quantity: int

    @property
    def line_total(self) -> float:
        """Price for all units of this item, rounded to 2 dp."""
        return round(self.unit_price * self.quantity, 2)


@dataclass
class Discount:
    """A discount rule, one of PERCENTAGE, FIXED_AMOUNT or BOGO."""

    code: str
    discount_type: DiscountType
    # PERCENTAGE
    rate: float = 0.0  # 0–100
    # FIXED_AMOUNT
    amount: float = 0.0  # positive
    min_subtotal: float = 0.0  # >= 0
    # BOGO
    buy_qty: int = 0
    get_qty: int = 0
    bogo_sku: str = ""


@dataclass
class Result:
    """Return value for every Cart public operation."""

    ok: bool
    data: dict[str, Any] | None = None
    error_code: ErrorCode | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise for JSON output."""
        return {
            "ok": self.ok,
            "data": self.data,
            "error_code": self.error_code.value if self.error_code else None,
        }
