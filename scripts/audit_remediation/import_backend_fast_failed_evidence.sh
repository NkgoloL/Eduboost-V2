#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SOURCE_DIR=""
LABEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-dir)
      SOURCE_DIR="$2"
      shift 2
      ;;
    --label)
      LABEL="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$SOURCE_DIR" ]]; then
  SOURCE_DIR="$(find /tmp -maxdepth 2 -type d -path '/tmp/backend-fast-gate-failed-evidence-*/backend-fast-gate' 2>/dev/null | sort | tail -n 1 || true)"
fi

if [[ -z "$SOURCE_DIR" || ! -d "$SOURCE_DIR" ]]; then
  echo "Could not find failed backend-fast evidence directory. Pass --source-dir." >&2
  exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SAFE_LABEL="${LABEL:-$TIMESTAMP}"
SAFE_LABEL="${SAFE_LABEL//[^A-Za-z0-9_.-]/_}"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-gate-failure/$SAFE_LABEL"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

cp -a "$SOURCE_DIR" "$RAW_DIR/original_failed_evidence"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
GENERATED_AT="$(date -Iseconds)"

$PYTHON_BIN scripts/audit_remediation/verify_backend_fast_environment.py --json > "$RAW_DIR/backend_fast_environment.json" || true
$PYTHON_BIN scripts/audit_remediation/backend_fast_failure_report.py --input "$SOURCE_DIR" --json > "$RAW_DIR/backend_fast_failure_report.json"

cat > "$RAW_DIR/import_manifest.json" <<EOF_JSON
{
  "source_dir": "${SOURCE_DIR}",
  "imported_at": "${GENERATED_AT}",
  "source_commit": "${SOURCE_COMMIT}",
  "branch": "${BRANCH}",
  "status": "failed_authority_gate_captured_for_triage"
}
EOF_JSON

find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF_INDEX
# Technical Audit Remediation Evidence — Backend Fast Failed Gate Diagnostic

**Stream:** technical-audit-remediation  
**Slice:** 02a-backend-fast-failure-triage  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${GENERATED_AT}  
**Status:** Failed authority gate captured — remediation pending  
**Authority command:** make test-fast  
**Imported from:** ${SOURCE_DIR}

## Raw evidence

- raw/original_failed_evidence/
- raw/backend_fast_environment.json
- raw/backend_fast_failure_report.json
- raw/import_manifest.json
- raw/SHA256SUMS.txt

## Boundary

This is non-passing diagnostic evidence. It must not be used as backend-fast candidate evidence. Passing evidence remains blocked until \`make test-fast\` exits 0 from a clean implementation commit.
EOF_INDEX

sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Imported failed backend-fast diagnostic evidence into %s\n' "$EVIDENCE_DIR"
