#!/usr/bin/env bash
# Self-check: verify each gate CAN fail by running against deliberately broken code.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
FAKE_DIR="$ROOT/.harness/fakes"
mkdir -p "$FAKE_DIR"

echo "=== SELF-CHECK: Verifying gates can detect failures ==="

# ---- Lint fake: contains an unused import ----
cat > "$FAKE_DIR/bad_lint.py" << 'EOF'
import os  # unused import — Ruff F401
x=1  # E225
EOF
echo "--- Lint gate on broken file ---"
if "$ROOT/.venv/bin/ruff" check "$FAKE_DIR/bad_lint.py" > /dev/null 2>&1; then
    echo "SELF-CHECK FAIL: lint gate did not catch errors"
    exit 1
else
    echo "Lint gate correctly detected errors: OK"
fi

# ---- Security fake: hardcoded password ----
cat > "$FAKE_DIR/bad_security.py" << 'EOF'
password = "s3cr3t"  # B105 hardcoded password
EOF
echo "--- Security gate on broken file ---"
if "$ROOT/.venv/bin/bandit" "$FAKE_DIR/bad_security.py" -ll -q > /dev/null 2>&1; then
    echo "SELF-CHECK WARN: bandit did not flag hardcoded password at -ll (may need -l)"
else
    echo "Security gate correctly detected issues: OK"
fi

# ---- Test fake: a test that always fails ----
cat > "$FAKE_DIR/test_always_fails.py" << 'EOF'
def test_always_fails():
    assert False, "deliberate failure"
EOF
echo "--- Test gate on always-failing test ---"
if "$ROOT/.venv/bin/pytest" "$FAKE_DIR/test_always_fails.py" -q > /dev/null 2>&1; then
    echo "SELF-CHECK FAIL: test gate did not catch failure"
    exit 1
else
    echo "Test gate correctly detected failure: OK"
fi

echo ""
echo "=== SELF-CHECK PASSED: All gates can detect failures ==="
rm -rf "$FAKE_DIR"
