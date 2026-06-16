#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate)
      GATE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

[[ "$GATE" == "2R.0" ]] || { echo "Only Gate 2R.0 evidence collection is available before approval." >&2; exit 2; }

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r0"
RAW="$EVIDENCE_ROOT/raw"
REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md"
INDEX="$EVIDENCE_ROOT/evidence_index.md"
AUDIT="$EVIDENCE_ROOT/audit_report.md"
mkdir -p "$RAW" "$(dirname "$REPORT")"

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
branch="$(git branch --show-current 2>/dev/null || printf unknown)"
head_sha="$(git rev-parse HEAD 2>/dev/null || printf unknown)"
base_sha="$(git merge-base HEAD origin/master 2>/dev/null || printf unknown)"
status_porcelain="$(git status --porcelain 2>/dev/null || true)"

capture() {
  local name="$1"
  shift
  local output="$RAW/$name"
  printf '+ %s\n' "$*" > "$output"
  set +e
  "$@" >> "$output" 2>&1
  local rc=$?
  set -e
  printf '\nexit_code=%s\n' "$rc" >> "$output"
  return "$rc"
}

capture_json() {
  local name="$1"
  shift
  local output="$RAW/$name"
  local meta="$RAW/$name.meta.txt"
  printf '+ %s\n' "$*" > "$meta"
  set +e
  "$@" > "$output" 2>> "$meta"
  local rc=$?
  set -e
  printf 'exit_code=%s\n' "$rc" >> "$meta"
  return "$rc"
}

overall_rc=0
capture_json baseline.json "$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py --json || overall_rc=1
capture_json phase_identifier_compatibility.json "$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py --json 02R phase-02r phase_02r || overall_rc=1
capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery || overall_rc=1
capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.0 --mode discovery || overall_rc=1
capture_json source_manifest.json "$PYTHON_BIN" scripts/curriculum/validate_source_manifest.py --json || overall_rc=1
capture_json source_inventory.json "$PYTHON_BIN" scripts/curriculum/source_inventory.py --json || overall_rc=1
capture_json extraction_sample.json "$PYTHON_BIN" scripts/curriculum/extract_caps_source_text.py --json || overall_rc=1
capture migration_graph.txt "$PYTHON_BIN" scripts/verify_migration_graph.py || overall_rc=1
capture schema_integrity.txt "$PYTHON_BIN" scripts/validate_schema_integrity.py || overall_rc=1

verdict="Fail"
status="Failed / remediation required"
if [[ "$overall_rc" -eq 0 ]]; then
  verdict="Pass"
  status="Closed"
fi

cat > "$REPORT" <<EOF
# Phase 2R Gate 2R.0 Closure Report

**Generated:** $timestamp
**Status:** $status
**Branch:** \`$branch\`
**baseline_capture_sha:** \`$head_sha\`
**base_against_origin_master:** \`$base_sha\`
**gate_report_commit_sha:** pending until this report is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.0 closure evidence was collected. The approval flag must remain
\`PHASE_02R_START_APPROVED=false\` unless every raw command exits zero and the
worktree is clean.

## Source State

\`\`\`text
$status_porcelain
\`\`\`

## Evidence

See \`docs/release-evidence/atlas/phase-02r/gate-2r0/\`.

## Recommendation

$([[ "$overall_rc" -eq 0 ]] && echo "Gate 2R.0 may proceed to approval review." || echo "Gate 2R.1 remains blocked. Remediate the failing raw commands before approval.")
EOF

cat > "$INDEX" <<EOF
# Phase 2R Gate 2R.0 Evidence Index

**Generated:** $timestamp
**Status:** $status
**Source commit:** \`$head_sha\`

| Evidence | Path |
|---|---|
| Phase 0 equivalent baseline | \`raw/baseline.json\` |
| 02R compatibility | \`raw/phase_identifier_compatibility.json\` |
| Preflight | \`raw/preflight.txt\` |
| Discovery verification | \`raw/verify_phase02r.txt\` |
| Source manifest | \`raw/source_manifest.json\` |
| Source inventory | \`raw/source_inventory.json\` |
| Extraction sample | \`raw/extraction_sample.json\` |
| Migration graph | \`raw/migration_graph.txt\` |
| Schema integrity | \`raw/schema_integrity.txt\` |
| Raw hashes | \`raw/SHA256SUMS.txt\` |
EOF

cat > "$AUDIT" <<EOF
# Phase 2R Gate 2R.0 Audit Report

**Generated:** $timestamp
**Verdict:** $verdict
**Auditor:** Nkgolo Lebelo
**Independence disclosure:** self-audit in a single-developer context

The audit verdict is limited to Gate 2R.0 discovery controls. It does not
authorise Gate 2R.1 unless the verdict is Pass and the dedicated approval
commit changes \`PHASE_02R_START_APPROVED\` to \`true\`.
EOF

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' \
    | sort \
    | while read -r name; do sha256sum "$name"; done \
    > SHA256SUMS.txt
)

echo "PHASE 02R GATE 2R.0 EVIDENCE COLLECTED"
echo "status=$status"
echo "report=$REPORT"
echo "evidence=$INDEX"
echo "audit=$AUDIT"
exit 0
