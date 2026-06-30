#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="$ROOT/docs/release-evidence/technical-audit/backend-fast-phase02j/$STAMP"
RAW_DIR="$OUT_DIR/raw"
mkdir -p "$RAW_DIR"

python3 "$ROOT/scripts/audit_remediation/verify_backend_fast_phase02j.py" --json > "$RAW_DIR/phase02j_verification.json"
python3 "$ROOT/scripts/audit_remediation/verify_backend_fast_phase02j.py" --json --static-only > "$RAW_DIR/phase02j_static_verification.json"
python3 -m compileall -q "$ROOT/scripts/audit_remediation" > "$RAW_DIR/compileall.txt" 2>&1
python3 -m pytest -q \
  "$ROOT/tests/unit/test_topic_map_worklist.py" \
  "$ROOT/tests/unit/audit_remediation/test_backend_fast_phase02j.py" \
  --no-cov > "$RAW_DIR/focused_tests.txt" 2>&1

cat > "$OUT_DIR/evidence_index.md" <<'EOF'
# Backend Fast Phase 02J Evidence — Tracked Topic-Map Text-Extract Provenance

Status: Phase 02J verification passed — backend-fast retry pending

This evidence is focused remediation evidence only. It does not constitute passing backend-fast gate evidence.
The backend-fast authority gate remains `make test-fast` and may only be recorded as passing when that command exits 0.

Boundary preserved:
- No Phase 02R governance change.
- No product release-readiness claim.
- No live DB migration.
- No runtime knowledge-graph implementation.
EOF

(
  cd "$OUT_DIR"
  find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

echo "$OUT_DIR"
