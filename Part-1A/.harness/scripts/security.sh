#!/usr/bin/env bash
# Security gate: bandit on src/
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "=== SECURITY GATE ==="
"$ROOT/.venv/bin/bandit" -r src/ -ll
echo "Security: PASS"
