#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-phase02l/$(date -u +%Y%m%dT%H%M%SZ)"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

python3 scripts/audit_remediation/verify_backend_fast_phase02l.py --json > "$RAW_DIR/phase02l_verification.json"
python3 scripts/audit_remediation/verify_backend_fast_evidence.py --json --evidence-dir docs/release-evidence/technical-audit/backend-fast-gate > "$RAW_DIR/backend_fast_evidence_verification.json"
python3 -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02l.py --no-cov > "$RAW_DIR/focused_tests.txt"
python3 -m compileall -q scripts/audit_remediation > "$RAW_DIR/compileall.txt"

find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"
cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Technical Audit Remediation Evidence — Backend Fast Phase 02L

**Stream:** technical-audit-remediation  
**Slice:** 02l-backend-fast-xfailed-evidence-verifier  
**Generated at:** $(date -Iseconds)  
**Status:** Phase 02L verification passed — backend-fast evidence verifier accepts valid xfailed summaries without weakening failed-test detection

## Raw evidence

- raw/phase02l_verification.json
- raw/backend_fast_evidence_verification.json
- raw/focused_tests.txt
- raw/compileall.txt
- raw/SHA256SUMS.txt

## Boundary

This evidence repairs the backend-fast evidence verifier only. It does not change application behaviour, product release readiness, Phase 02R governance, live database state, or runtime knowledge-graph implementation.
EOF
sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Collected Phase 02L evidence in %s\n' "$EVIDENCE_DIR"
