#!/usr/bin/env python3
"""
Harness runner — executes all quality gates and writes a JSON report.

Usage: python .harness/harness_runner.py [--report-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = Path(__file__).parent / "scripts"


def run_gate(name: str, cmd: list[str]) -> dict:
    """Run a shell command and capture result."""
    print(f"\n{'='*60}")
    print(f"GATE: {name}")
    print(f"CMD:  {' '.join(cmd)}")
    print("=" * 60)
    result = subprocess.run(
        cmd,
        capture_output=False,
        text=True,
        cwd=ROOT,
    )
    passed = result.returncode == 0
    status = "PASS" if passed else "FAIL"
    print(f"\n>>> {name}: {status} (exit {result.returncode})")
    return {
        "gate": name,
        "command": " ".join(cmd),
        "passed": passed,
        "exit_code": result.returncode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all quality gates")
    parser.add_argument(
        "--report-dir",
        default=str(ROOT / "evidence" / "harness-results"),
        help="Directory to write JSON report",
    )
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    venv_python = ROOT / ".venv" / "bin" / "python"
    venv_ruff = ROOT / ".venv" / "bin" / "ruff"
    venv_bandit = ROOT / ".venv" / "bin" / "bandit"
    venv_pytest = ROOT / ".venv" / "bin" / "pytest"

    gates = [
        run_gate(
            "lint",
            [str(venv_ruff), "check", "src/", "tests/"],
        ),
        run_gate(
            "security",
            [str(venv_bandit), "-r", "src/", "-ll"],
        ),
        run_gate(
            "tests",
            [str(venv_pytest), "tests/", "-v", "--tb=short"],
        ),
    ]

    all_passed = all(g["passed"] for g in gates)
    report = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "overall": "PASS" if all_passed else "FAIL",
        "gates": gates,
    }

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"harness_{ts}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"OVERALL: {report['overall']}")
    print(f"Report:  {report_path}")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
