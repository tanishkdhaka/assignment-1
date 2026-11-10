#!/usr/bin/env bash
# Test gate: pytest
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "=== TEST GATE ==="
"$ROOT/.venv/bin/pytest" tests/ -v --tb=short
