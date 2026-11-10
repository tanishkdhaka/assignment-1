"""Shopping Cart engine — pure logic, no I/O."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import CartItem, Discount, DiscountType, ErrorCode, Result

if TYPE_CHECKING:
    pass


class Cart:
    """
    A shopping cart supporting PERCENTAGE, FIXED_AMOUNT and BOGO discounts.

    Parameters
    ----------
    catalog:
        Mapping of coupon_code -> Discount.  Injected for testability.
    tax_rate:
        Flat tax percentage applied after discounts (default 10.0).
    """

    def __init__(
        self,
        catalog: dict[str, Discount] | None = None,
        tax_rate: float = 10.0,
    ) -> None:
        self._items: dict[str, CartItem] = {}
        self._catalog: dict[str, Discount] = catalog or {}
        self._tax_rate: float = tax_rate
        # At most one non-BOGO discount active at a time
        self._main_discount: Discount | None = None
        # BOGO discounts: keyed by sku
        self._bogo_discounts: dict[str, Discount] = {}

    # ------------------------------------------------------------------
    def add_item(
        self,
        sku: str,
        name: str,
        price: float,
        qty: int,
    ) -> Result:
        """Add or accumulate a product in the cart (AC-001, AC-002)."""
        if price <= 0:
            return Result(ok=False, error_code=ErrorCode.INVALID_PRICE)
        if qty <= 0:
            return Result(ok=False, error_code=ErrorCode.INVALID_QUANTITY)
        price_r = round(price, 2)
        if sku in self._items:
            self._items[sku].quantity += qty
        else:
            self._items[sku] = CartItem(
                sku=sku,
                name=name,
                unit_price=price_r,
                quantity=qty,
            )
        return Result(ok=True, data=self._snapshot())

    def remove_item(self, sku: str, qty: int) -> Result:
        """Remove units from the cart (AC-003, AC-004)."""
        if sku not in self._items:
            return Result(ok=False, error_code=ErrorCode.ITEM_NOT_FOUND)
        item = self._items[sku]
        if qty >= item.quantity:
            del self._items[sku]
            # Remove any BOGO tied to this SKU
            self._bogo_discounts.pop(sku, None)
        else:
            item.quantity -= qty
        return Result(ok=True, data=self._snapshot())

    def update_quantity(self, sku: str, qty: int) -> Result:
        """Set absolute quantity for a SKU."""
        if sku not in self._items:
            return Result(ok=False, error_code=ErrorCode.ITEM_NOT_FOUND)
        if qty <= 0:
            return self.remove_item(sku, self._items[sku].quantity)
        self._items[sku].quantity = qty
        return Result(ok=True, data=self._snapshot())

    def clear(self) -> Result:
        """Remove all items and all active discounts (AC-017)."""
        self._items.clear()
        self._main_discount = None
        self._bogo_discounts.clear()
        return Result(ok=True, data=self._snapshot())

    # ------------------------------------------------------------------
    def apply_discount(self, coupon_code: str) -> Result:
        """
        Apply a discount by coupon code (AC-005–AC-013).

        PERCENTAGE and FIXED_AMOUNT replace each other (AC-008).
        BOGO stacks independently (AC-010).
        """
        if coupon_code not in self._catalog:
            return Result(ok=False, error_code=ErrorCode.INVALID_COUPON)
        discount = self._catalog[coupon_code]

        if discount.discount_type == DiscountType.FIXED_AMOUNT:
            if self.subtotal < discount.min_subtotal:
                return Result(ok=False, error_code=ErrorCode.MINIMUM_NOT_MET)
            self._main_discount = discount
        elif discount.discount_type == DiscountType.PERCENTAGE:
            self._main_discount = discount
        else:  # BOGO
            self._bogo_discounts[discount.bogo_sku] = discount

        return Result(ok=True, data=self._snapshot())

    def remove_discount(self, coupon_code: str) -> Result:
        """Remove a named active discount."""
        if self._main_discount and self._main_discount.code == coupon_code:
            self._main_discount = None
            return Result(ok=True, data=self._snapshot())
        for sku, d in list(self._bogo_discounts.items()):
            if d.code == coupon_code:
                del self._bogo_discounts[sku]
                return Result(ok=True, data=self._snapshot())
        return Result(ok=False, error_code=ErrorCode.INVALID_COUPON)

    # ------------------------------------------------------------------
    @property
    def subtotal(self) -> float:
        """Sum of all line totals (AC-012)."""
        return round(sum(item.line_total for item in self._items.values()), 2)

    @property
    def discount_total(self) -> float:
        """Total saving from all active discounts, capped at subtotal."""
        saving = 0.0
        sub = self.subtotal

        if self._main_discount:
            d = self._main_discount
            if d.discount_type == DiscountType.PERCENTAGE:
                saving += round(sub * d.rate / 100, 2)
            elif d.discount_type == DiscountType.FIXED_AMOUNT:
                saving += d.amount

        for sku, d in self._bogo_discounts.items():
            if sku in self._items:
                item = self._items[sku]
                cycles = item.quantity // d.buy_qty
                free_units = cycles * d.get_qty
                saving += round(free_units * item.unit_price, 2)

        # Cap so subtotal_after_discounts >= 0 (AC-020)
        return round(min(saving, sub), 2)

    @property
    def subtotal_after_discounts(self) -> float:
        """Subtotal minus discounts, minimum 0.00."""
        return round(max(self.subtotal - self.discount_total, 0.0), 2)

    @property
    def tax(self) -> float:
        """Tax on the discounted subtotal (AC-011)."""
        return round(self.subtotal_after_discounts * self._tax_rate / 100, 2)

    @property
    def total(self) -> float:
        """Grand total (AC-011)."""
        return round(self.subtotal_after_discounts + self.tax, 2)

    # ------------------------------------------------------------------
    def _snapshot(self) -> dict[str, Any]:
        """Return a dict summarising the current cart state."""
        return {
            "items": [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "unit_price": item.unit_price,
                    "quantity": item.quantity,
                    "line_total": item.line_total,
                }
                for item in self._items.values()
            ],
            "subtotal": self.subtotal,
            "discount_total": self.discount_total,
            "subtotal_after_discounts": self.subtotal_after_discounts,
            "tax": self.tax,
            "total": self.total,
            "active_discounts": self._active_discount_codes(),
        }

    def _active_discount_codes(self) -> list[str]:
        codes: list[str] = []
        if self._main_discount:
            codes.append(self._main_discount.code)
        codes.extend(d.code for d in self._bogo_discounts.values())
        return codes

    def to_dict(self) -> dict[str, Any]:
        """Full serialisation for persistence (AC-016)."""
        return {
            "tax_rate": self._tax_rate,
            "items": [
                {
                    "sku": i.sku,
                    "name": i.name,
                    "unit_price": i.unit_price,
                    "quantity": i.quantity,
                }
                for i in self._items.values()
            ],
            "main_discount_code": (
                self._main_discount.code if self._main_discount else None
            ),
            "bogo_discount_codes": [
                d.bogo_sku for d in self._bogo_discounts.values()
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        catalog: dict[str, Discount] | None = None,
    ) -> Cart:
        """Restore a Cart from a serialised dict (AC-016)."""
        cart = cls(catalog=catalog, tax_rate=data["tax_rate"])
        for item_d in data["items"]:
            cart._items[item_d["sku"]] = CartItem(
                sku=item_d["sku"],
                name=item_d["name"],
                unit_price=item_d["unit_price"],
                quantity=item_d["quantity"],
            )
        if data.get("main_discount_code") and catalog:
            code = data["main_discount_code"]
            if code in catalog:
                cart._main_discount = catalog[code]
        for sku in data.get("bogo_discount_codes", []):
            # Find the BOGO discount for this SKU in catalog
            if catalog:
                for d in catalog.values():
                    if d.discount_type == DiscountType.BOGO and d.bogo_sku == sku:
                        cart._bogo_discounts[sku] = d
                        break
        return cart
