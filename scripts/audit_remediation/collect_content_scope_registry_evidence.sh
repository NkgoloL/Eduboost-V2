#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-scope-registry/${STAMP}"
RAW_DIR="${EVIDENCE_DIR}/raw"
mkdir -p "$RAW_DIR"

SOURCE_COMMIT="$(git rev-parse HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

"$PYTHON_BIN" scripts/audit_remediation/verify_content_scope_registry_expansion.py --json \
  > "$RAW_DIR/content_scope_registry_verification.json"

"$PYTHON_BIN" scripts/audit_remediation/verify_content_scope_registry_expansion.py --json --static-only \
  > "$RAW_DIR/content_scope_registry_static_verification.json"

{
  "$PYTHON_BIN" -m pytest -q \
    tests/unit/test_content_scope_registry.py \
    tests/unit/audit_remediation/test_content_scope_registry_expansion.py \
    --no-cov
} > "$RAW_DIR/focused_tests.txt" 2>&1

"$PYTHON_BIN" - <<'PY' > "$RAW_DIR/registry_summary.json"
import json
from pathlib import Path
raw = json.loads(Path("data/content_factory/scopes.json").read_text(encoding="utf-8"))
scopes = raw["scopes"]
summary = {
    "scope_count": len(scopes),
    "active_scopes": sorted(s["scope_id"] for s in scopes if s["status"] == "active"),
    "review_scope_count": sum(1 for s in scopes if s["status"] == "review"),
    "grade5_mathematics_en": next(s for s in scopes if s["scope_id"] == "grade5_mathematics_en"),
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

(
  cd "$EVIDENCE_DIR"
  find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Technical Audit Backend Fast Scope Registry Evidence

**Stream:** Technical Audit Remediation  
**Phase:** 02C — Backend Fast Scope Registry Expansion  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Status:** Scope registry verification passed — backend-fast retry pending

## Boundary

This is not passing backend-fast evidence. It records that the dominant
function-backed scope-registry blocker has been remediated so the backend-fast
authority gate can be retried honestly.

No Phase 02R governance is changed. No product release-readiness claim is made.
No live DB migration is executed. No runtime knowledge-graph implementation is
added; the expanded registry preserves source/curriculum hooks for future KG work.

## Raw evidence

- raw/content_scope_registry_verification.json
- raw/content_scope_registry_static_verification.json
- raw/focused_tests.txt
- raw/registry_summary.json
- SHA256SUMS.txt
EOF

python3 - <<PY
from pathlib import Path
import hashlib
path = Path("$EVIDENCE_DIR/evidence_index.md")
print(f"evidence_index={path}")
print(f"sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
PY
