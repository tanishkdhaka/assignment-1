"""JSON persistence for Cart state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .engine import Cart
from .models import Discount, ErrorCode, Result

if TYPE_CHECKING:
    pass


def save_json(cart: Cart, path: str | Path) -> Result:
    """Serialise cart state to a JSON file (AC-016)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = cart.to_dict()
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return Result(ok=True, data={"saved_to": str(p)})


def load_json(
    path: str | Path,
    catalog: dict[str, Discount] | None = None,
) -> Result:
    """Restore a Cart from a JSON file (AC-016)."""
    p = Path(path)
    if not p.exists():
        return Result(
            ok=False,
            error_code=ErrorCode.ITEM_NOT_FOUND,
            data={"detail": f"File not found: {p}"},
        )
    raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    cart = Cart.from_dict(raw, catalog=catalog)
    return Result(ok=True, data={"cart": cart})
