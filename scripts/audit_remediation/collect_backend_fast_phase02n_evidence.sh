#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-phase02n/$(date -u +%Y%m%dT%H%M%SZ)"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
GENERATED_AT="$(date -Iseconds)"

run_json() {
  local output="$1"
  shift
  "$@" >"$output" 2>&1
}

run_json "$RAW_DIR/phase02n_verifier.json" "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02n.py --json
run_json "$RAW_DIR/backend_fast_evidence_verifier.json" "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_evidence.py --json --evidence-dir docs/release-evidence/technical-audit/backend-fast-gate || true
"$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02n.py --no-cov > "$RAW_DIR/focused_tests.txt" 2>&1
"$PYTHON_BIN" -m compileall -q scripts/audit_remediation > "$RAW_DIR/compileall.txt" 2>&1

(
  cd "$EVIDENCE_DIR"
  find raw -type f -print0 | sort -z | xargs -0 sha256sum > raw/SHA256SUMS.txt
)

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Technical Audit Remediation Evidence — Backend Fast Phase 02N

**Stream:** technical-audit-remediation  
**Slice:** 02n-backend-fast-evidence-finalization  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${GENERATED_AT}  
**Status:** Phase 02N verification passed — backend-fast HEAD evidence refresh pending

## Raw evidence

- raw/phase02n_verifier.json
- raw/backend_fast_evidence_verifier.json
- raw/focused_tests.txt
- raw/compileall.txt
- raw/SHA256SUMS.txt

## Boundary

This evidence records the harness repair only. It does not itself close the backend-fast authority gate, claim full release readiness, change Phase 02R governance, run live database migrations, or implement runtime knowledge graphs.
EOF
sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Collected Phase 02N evidence in %s\n' "$EVIDENCE_DIR"
