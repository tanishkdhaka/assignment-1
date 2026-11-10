"""CLI entry point for the Shopping Cart & Discount Engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import Cart
from .models import Discount, DiscountType
from .persistence import load_json, save_json

# ---------------------------------------------------------------------------
DEFAULT_CATALOG: dict[str, Discount] = {
    "SAVE10": Discount(
        code="SAVE10",
        discount_type=DiscountType.PERCENTAGE,
        rate=10.0,
    ),
    "FLAT5": Discount(
        code="FLAT5",
        discount_type=DiscountType.FIXED_AMOUNT,
        amount=5.0,
        min_subtotal=20.0,
    ),
    "BOGO2FOR1": Discount(
        code="BOGO2FOR1",
        discount_type=DiscountType.BOGO,
        buy_qty=2,
        get_qty=1,
        bogo_sku="WIDGET",
    ),
}

_STATE_FILE = Path(".cart_state.json")
_cart: Cart = Cart(catalog=DEFAULT_CATALOG)


def _load_state() -> None:
    global _cart  # noqa: PLW0603  # module-level state for CLI session
    if _STATE_FILE.exists():
        result = load_json(_STATE_FILE, catalog=DEFAULT_CATALOG)
        if result.ok and result.data:
            _cart = result.data["cart"]


def _save_state() -> None:
    save_json(_cart, _STATE_FILE)


def _out(result: object) -> None:
    if hasattr(result, "to_dict"):
        print(json.dumps(result.to_dict(), indent=2))  # noqa: T201
    else:
        print(json.dumps(result, indent=2))  # noqa: T201


def cmd_add(args: argparse.Namespace) -> None:
    _load_state()
    result = _cart.add_item(args.sku, args.name, args.price, args.qty)
    _save_state()
    _out(result)
    sys.exit(0 if result.ok else 1)


def cmd_remove(args: argparse.Namespace) -> None:
    _load_state()
    result = _cart.remove_item(args.sku, args.qty)
    _save_state()
    _out(result)
    sys.exit(0 if result.ok else 1)


def cmd_show(_args: argparse.Namespace) -> None:
    _load_state()
    _out({"ok": True, "data": _cart._snapshot()})


def cmd_apply_discount(args: argparse.Namespace) -> None:
    _load_state()
    result = _cart.apply_discount(args.code)
    _save_state()
    _out(result)
    sys.exit(0 if result.ok else 1)


def cmd_clear(_args: argparse.Namespace) -> None:
    _load_state()
    result = _cart.clear()
    _save_state()
    _out(result)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the cart CLI."""
    parser = argparse.ArgumentParser(
        prog="cart",
        description="Shopping Cart & Discount Engine CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a product to the cart")
    p_add.add_argument("sku")
    p_add.add_argument("name")
    p_add.add_argument("price", type=float)
    p_add.add_argument("qty", type=int)
    p_add.set_defaults(func=cmd_add)

    # remove
    p_rem = sub.add_parser("remove", help="Remove units from the cart")
    p_rem.add_argument("sku")
    p_rem.add_argument("qty", type=int)
    p_rem.set_defaults(func=cmd_remove)

    # show
    p_show = sub.add_parser("show", help="Display cart contents")
    p_show.set_defaults(func=cmd_show)

    # apply-discount
    p_disc = sub.add_parser("apply-discount", help="Apply a coupon code")
    p_disc.add_argument("code")
    p_disc.set_defaults(func=cmd_apply_discount)

    # clear
    p_clr = sub.add_parser("clear", help="Clear all items and discounts")
    p_clr.set_defaults(func=cmd_clear)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
