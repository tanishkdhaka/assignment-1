"""CLI smoke tests — verify exit codes and JSON output for key commands."""

import json
import os
import subprocess
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).parent.parent / "src")


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{SRC_DIR}:{existing_pp}" if existing_pp else SRC_DIR
    return subprocess.run(
        [sys.executable, "-m", "cart", *args],
        capture_output=True,
        text=True,
        cwd=cwd or Path("."),
        env=env,
    )


def test_cli_add_valid_item(tmp_path: Path) -> None:
    result = _run("add", "SKU1", "Widget", "9.99", "2", cwd=tmp_path)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True


def test_cli_add_invalid_price(tmp_path: Path) -> None:
    result = _run("add", "SKU1", "Widget", "0", "1", cwd=tmp_path)
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert data["error_code"] == "INVALID_PRICE"


def test_cli_show_empty_cart(tmp_path: Path) -> None:
    result = _run("show", cwd=tmp_path)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["data"]["items"] == []


def test_cli_clear(tmp_path: Path) -> None:
    _run("add", "SKU1", "Widget", "9.99", "2", cwd=tmp_path)
    result = _run("clear", cwd=tmp_path)
    assert result.returncode == 0


def test_cli_invalid_coupon(tmp_path: Path) -> None:
    _run("add", "SKU1", "Widget", "9.99", "2", cwd=tmp_path)
    result = _run("apply-discount", "BADCODE", cwd=tmp_path)
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["error_code"] == "INVALID_COUPON"
