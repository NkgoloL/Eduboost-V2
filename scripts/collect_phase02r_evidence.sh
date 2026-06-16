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

[[ "$GATE" == "2R.0" || "$GATE" == "2R.1" ]] || { echo "Only Gate 2R.0 and 2R.1 evidence collection are supported." >&2; exit 2; }

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.0" ]]; then
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r0"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md"
  WORK_REPORT_NAME="phase_02r_gate_2r0_closure_report.md"
else
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r1"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r1_closure_report.md"
  WORK_REPORT_NAME="phase_02r_gate_2r1_closure_report.md"
fi

WORKDIR="$(mktemp -d)"
WORK_EVIDENCE_ROOT="$WORKDIR/evidence"
RAW="$WORK_EVIDENCE_ROOT/raw"
WORK_REPORT="$WORKDIR/$WORK_REPORT_NAME"
INDEX="$WORK_EVIDENCE_ROOT/evidence_index.md"
AUDIT="$WORK_EVIDENCE_ROOT/audit_report.md"
mkdir -p "$RAW"

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
branch="$(git branch --show-current 2>/dev/null || printf unknown)"
head_sha="$(git rev-parse HEAD 2>/dev/null || printf unknown)"
base_sha="$(git merge-base HEAD origin/master 2>/dev/null || printf unknown)"
status_porcelain="$(git status --porcelain 2>/dev/null || true)"

capture() {
  local name="$1"
  shift
  local output="$RAW/$name"
  local tmp
  tmp="$(mktemp)"
  printf '+ %s\n' "$*" > "$tmp"
  set +e
  "$@" >> "$tmp" 2>&1
  local rc=$?
  set -e
  printf '\nexit_code=%s\n' "$rc" >> "$tmp"
  mv "$tmp" "$output"
  return "$rc"
}

capture_json() {
  local name="$1"
  shift
  local output="$RAW/$name"
  local meta="$RAW/$name.meta.txt"
  local tmp_output
  local tmp_meta
  tmp_output="$(mktemp)"
  tmp_meta="$(mktemp)"
  printf '+ %s\n' "$*" > "$tmp_meta"
  set +e
  "$@" > "$tmp_output" 2>> "$tmp_meta"
  local rc=$?
  set -e
  printf 'exit_code=%s\n' "$rc" >> "$tmp_meta"
  mv "$tmp_output" "$output"
  mv "$tmp_meta" "$meta"
  return "$rc"
}

overall_rc=0

if [[ "$GATE" == "2R.0" ]]; then
  capture_json baseline.json "$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py --json || overall_rc=1
  capture_json phase_identifier_compatibility.json "$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py --json 02R phase-02r phase_02r || overall_rc=1
  capture_json phase_identifier_compatibility_strict.json "$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py --strict --json 02R phase-02r phase_02r || overall_rc=1
  capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery || overall_rc=1
  capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.0 --mode discovery || overall_rc=1
  capture_json source_manifest.json "$PYTHON_BIN" scripts/curriculum/validate_source_manifest.py --json || overall_rc=1
  capture_json source_inventory.json "$PYTHON_BIN" scripts/curriculum/source_inventory.py --json || overall_rc=1
  capture_json extraction_sample.json "$PYTHON_BIN" scripts/curriculum/extract_caps_source_sample.py --json || overall_rc=1
  capture reconciliation_closure.txt env PHASE_RECONCILIATION_MODE=closure bash scripts/verify_phases_01_07_reconciliation.sh || overall_rc=1
  capture openapi_check.txt "$PYTHON_BIN" scripts/generate_openapi.py --check || overall_rc=1
  capture import_boundaries.txt bash -lc 'if command -v lint-imports >/dev/null 2>&1; then lint-imports; else python -m importlinter --config .importlinter; fi' || overall_rc=1
  capture migration_graph.txt "$PYTHON_BIN" scripts/verify_migration_graph.py || overall_rc=1
  capture schema_integrity.txt "$PYTHON_BIN" scripts/validate_schema_integrity.py || overall_rc=1
else
  # Gate 2R.1
  capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.1 || overall_rc=1
  capture apply_patch.txt bash scripts/apply_phase02r_patch.sh --gate 2R.1 || overall_rc=1
  capture_json phase_identifier_compatibility_strict.json "$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py --strict --json 02R phase-02r phase_02r || overall_rc=1
  capture phase_control_sets.txt "$PYTHON_BIN" scripts/validate_phase_control_sets.py || overall_rc=1
  capture migration_graph.txt "$PYTHON_BIN" scripts/verify_migration_graph.py || overall_rc=1
  capture schema_integrity.txt "$PYTHON_BIN" scripts/validate_schema_integrity.py || overall_rc=1
  capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.1 || overall_rc=1
fi

verdict="Fail"
status="Failed / remediation required"
if [[ "$overall_rc" -eq 0 ]]; then
  verdict="Pass"
  status="Closed"
fi

if [[ "$GATE" == "2R.0" ]]; then
  cat > "$WORK_REPORT" <<EOF
# Phase 2R Gate 2R.0 Closure Report

**Generated:** $timestamp
**Status:** $status
**Branch:** \`$branch\`
**evidence_run_source_sha:** \`$head_sha\`
**base_against_origin_master:** \`$base_sha\`
**initial_gate_report_commit_sha:** \`8d972b5f\`
**remediation_code_commit_sha:** pending until this remediation is committed
**evidence_commit_sha:** pending until this evidence pack is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.0 closure evidence was collected into a temporary directory before it
was copied into the repository. The approval flag must remain
\`PHASE_02R_START_APPROVED=false\` and
\`phase_02r_start_gate_control.json.start_approved=false\` unless every raw
command exits zero and the worktree is clean before evidence copy.

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
| Strict 02R compatibility | \`raw/phase_identifier_compatibility_strict.json\` |
| Preflight | \`raw/preflight.txt\` |
| Discovery verification | \`raw/verify_phase02r.txt\` |
| Source manifest | \`raw/source_manifest.json\` |
| Source inventory | \`raw/source_inventory.json\` |
| Extraction sample | \`raw/extraction_sample.json\` |
| Phase 1-7 closure reconciliation | \`raw/reconciliation_closure.txt\` |
| OpenAPI drift check | \`raw/openapi_check.txt\` |
| Import boundaries | \`raw/import_boundaries.txt\` |
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

else
  # Gate 2R.1 Outputs
  cat > "$WORK_REPORT" <<EOF
# Phase 2R Gate 2R.1 Closure Report

**Generated:** $timestamp
**Status:** $status
**Branch:** \`$branch\`
**evidence_run_source_sha:** \`$head_sha\`
**base_against_origin_master:** \`$base_sha\`
**initial_gate_report_commit_sha:** \`8d972b5f\`
**remediation_code_commit_sha:** pending until this remediation is committed
**evidence_commit_sha:** pending until this evidence pack is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.1 closure evidence was collected into a temporary directory before it
was copied into the repository.

## Source State

\`\`\`text
$status_porcelain
\`\`\`

## Evidence

See \`docs/release-evidence/atlas/phase-02r/gate-2r1/\`.

## Recommendation

$([[ "$overall_rc" -eq 0 ]] && echo "Gate 2R.1 implementation preflight and patch-application verification passed." || echo "Gate 2R.1 remains blocked. Remediate the failing raw commands before proceeding.")
EOF

  cat > "$INDEX" <<EOF
# Phase 2R Gate 2R.1 Evidence Index

**Generated:** $timestamp
**Status:** $status
**Source commit:** \`$head_sha\`

| Evidence | Path |
|---|---|
| Preflight | \`raw/preflight.txt\` |
| Patch application | \`raw/apply_patch.txt\` |
| Strict 02R compatibility | \`raw/phase_identifier_compatibility_strict.json\` |
| Phase control sets | \`raw/phase_control_sets.txt\` |
| Migration graph | \`raw/migration_graph.txt\` |
| Schema integrity | \`raw/schema_integrity.txt\` |
| Verification | \`raw/verify_phase02r.txt\` |
| Raw hashes | \`raw/SHA256SUMS.txt\` |
EOF

  cat > "$AUDIT" <<EOF
# Phase 2R Gate 2R.1 Audit Report

**Generated:** $timestamp
**Verdict:** $verdict
**Auditor:** Nkgolo Lebelo
**Independence disclosure:** self-audit in a single-developer context

The audit verdict is limited to Gate 2R.1 implementation controls.
EOF
fi

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' \
    | sort \
    | while read -r name; do sha256sum "$name"; done \
    > SHA256SUMS.txt
)

mkdir -p "$EVIDENCE_ROOT/raw" "$(dirname "$REPORT")"
cp "$WORK_REPORT" "$REPORT"
cp "$INDEX" "$EVIDENCE_ROOT/evidence_index.md"
cp "$AUDIT" "$EVIDENCE_ROOT/audit_report.md"
cp "$RAW"/* "$EVIDENCE_ROOT/raw/"

echo "PHASE 02R GATE ${GATE} EVIDENCE COLLECTED"
echo "status=$status"
echo "report=$REPORT"
echo "evidence=$INDEX"
echo "audit=$AUDIT"
exit "$overall_rc"
