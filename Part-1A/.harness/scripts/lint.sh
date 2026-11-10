#!/usr/bin/env bash
# Lint gate: ruff check on src/ and tests/
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "=== LINT GATE ==="
"$ROOT/.venv/bin/ruff" check src/ tests/
echo "Lint: PASS"
