#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="docs/release-evidence/technical-audit/backend-fast-phase02m/${STAMP}"
RAW="${OUT}/raw"
mkdir -p "$RAW"

python3 scripts/audit_remediation/verify_backend_fast_phase02m.py --json > "$RAW/phase02m_verification.json"
python3 -m compileall -q scripts/audit_remediation > "$RAW/compileall.txt" 2>&1
python3 -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02m.py --no-cov > "$RAW/focused_tests.txt" 2>&1

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
cat > "$OUT/evidence_index.md" <<EOF
# Technical Audit Remediation Evidence — Backend Fast Phase 02M

**Stream:** technical-audit-remediation  
**Slice:** 02M backend-fast HEAD-aligned finalization  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${STAMP}  
**Status:** Phase 02M verification passed — backend-fast retry pending

## Raw evidence

- raw/phase02m_verification.json
- raw/compileall.txt
- raw/focused_tests.txt

## Boundary

This evidence records audit-harness finalization only. It does not replace the backend-fast authority gate, claim full product release readiness, execute a live database migration, change Phase 02R governance, or implement runtime KG.
EOF

( cd "$OUT" && find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt )

echo "$OUT"
