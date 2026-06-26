#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-phase02k/${STAMP}"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

$PYTHON_BIN scripts/audit_remediation/verify_backend_fast_phase02k.py --json > "$RAW_DIR/phase02k_verification.json"
$PYTHON_BIN -m compileall -q scripts/audit_remediation > "$RAW_DIR/compileall.txt" 2>&1
$PYTHON_BIN -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02k.py --no-cov > "$RAW_DIR/focused_tests.txt" 2>&1
find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"

cat > "$EVIDENCE_DIR/evidence_index.md" <<'EOF'
# Backend Fast Phase 02K Evidence — Evidence Authority Harness Repair

Status: Phase 02K verification passed — backend-fast retry pending

This evidence is focused remediation evidence only. It does not constitute passing backend-fast gate evidence.
The backend-fast authority gate remains `make test-fast` and may only be recorded as passing when that command exits 0 and `verify_backend_fast_evidence.py` independently reports `valid: true`.

Boundary preserved:
- No Phase 02R governance change.
- No product release-readiness claim.
- No live DB migration.
- No runtime knowledge-graph implementation.
EOF

sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Collected Phase 02K evidence in %s\n' "$EVIDENCE_DIR"
