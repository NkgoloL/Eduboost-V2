#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
GATE="2R.8"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r8"
REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r8_closure_report.md"
mkdir -p "$EVIDENCE_ROOT"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

fail_collection_precondition() {
  local reason="$1"
  cat > "$EVIDENCE_ROOT/collection_failure.md" <<EOF
# Phase 2R Gate $GATE Evidence Collection Failure

**Generated:** $timestamp
**Status:** Failed

$reason

No Gate 2R.8 approval, final transition, or Phase 02R closure decision may be based on this failed collection.
EOF
  echo "$reason" >&2
  exit 3
}

command -v git >/dev/null 2>&1 || fail_collection_precondition "Git is required for attributable final evidence."
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail_collection_precondition "Evidence must be collected from a Git worktree."
status_porcelain="$(git status --porcelain)"
[[ -z "$status_porcelain" ]] || fail_collection_precondition "Evidence collection requires a clean worktree. Commit or discard all changes first."

branch="$(git branch --show-current)"
head_sha="$(git rev-parse HEAD)"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
WORK_EVIDENCE_ROOT="$WORKDIR/evidence"
RAW="$WORK_EVIDENCE_ROOT/raw"
WORK_REPORT="$WORKDIR/closure_report.md"
INDEX="$WORK_EVIDENCE_ROOT/evidence_index.md"
AUDIT="$WORK_EVIDENCE_ROOT/audit_report.md"
mkdir -p "$RAW"

overall_rc=0
LAST_CAPTURE_RC=0
capture() {
  local name="$1"
  shift
  local output="$RAW/$name"
  local meta="$RAW/$name.meta.json"
  local started finished start_epoch finish_epoch rc
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_epoch="$(date +%s)"
  set +e
  "$@" >"$output" 2>&1
  rc=$?
  set -e
  finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  finish_epoch="$(date +%s)"
  "$PYTHON_BIN" - "$meta" "$started" "$finished" "$((finish_epoch-start_epoch))" "$rc" "$@" <<'PYMETA'
import json
import sys
from pathlib import Path
path, started, finished, duration, rc, *command = sys.argv[1:]
Path(path).write_text(json.dumps({
    "command": command,
    "started_at": started,
    "finished_at": finished,
    "duration_seconds": int(duration),
    "exit_code": int(rc),
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PYMETA
  LAST_CAPTURE_RC="$rc"
  if [[ "$rc" -ne 0 && "$overall_rc" -eq 0 ]]; then
    overall_rc="$rc"
  fi
  return 0
}

capture environment.txt bash -lc 'python3 --version; git --version; uname -a'
capture gate-control.json "$PYTHON_BIN" scripts/phase02r_gate_control.py --expected-approved-gate 2R.7 --expected-authorised-gate 2R.8 --require-approval-roles --require-evidence-index-sha --json
capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.8
capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.8 --mode implementation
capture verify_phase02r_gate2r8.json "$PYTHON_BIN" scripts/verify_phase02r_gate2r8.py --mode implementation --json
capture verify_phase02r_gate2r8_postgres.txt bash scripts/verify_phase02r_gate2r8_postgres.sh
capture legacy_migration_manifest.json "$PYTHON_BIN" scripts/curriculum/build_phase02r_gate2r8_legacy_migration.py --json
capture real_corpus_evaluation_report.json "$PYTHON_BIN" scripts/curriculum/export_phase02r_gate2r8_evaluation_report.py --json
capture audit_bundle.json "$PYTHON_BIN" scripts/curriculum/export_phase02r_gate2r8_audit_bundle.py --json
capture closure_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r8_closure.py --json
capture focused_tests.txt "$PYTHON_BIN" -m pytest -q tests/unit/phase02r/test_gate2r8_legacy_evaluation_closure.py --no-cov
capture compileall.txt "$PYTHON_BIN" -m compileall -q app/services/curriculum/legacy_migration.py app/services/curriculum/evaluation.py app/services/curriculum/phase02r_closure.py scripts/verify_phase02r_gate2r8.py scripts/curriculum/build_phase02r_gate2r8_legacy_migration.py scripts/curriculum/export_phase02r_gate2r8_evaluation_report.py scripts/curriculum/export_phase02r_gate2r8_audit_bundle.py scripts/curriculum/validate_phase02r_gate2r8_closure.py tests/unit/phase02r/test_gate2r8_legacy_evaluation_closure.py

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' \
    | sort \
    | while read -r name; do sha256sum "$name"; done \
    > SHA256SUMS.txt
)

status="Candidate verification passed — human approval pending"
if [[ "$overall_rc" -ne 0 ]]; then
  status="Candidate verification failed — do not approve"
fi

cat > "$WORK_REPORT" <<EOF
# Phase 2R Gate 2R.8 Candidate Closure Report

**Generated:** $timestamp
**Branch:** $branch
**Source commit:** $head_sha
**Status:** $status

## Scope

Gate 2R.8 covers legacy migration readiness, real-corpus evaluation,
audit-bundle aggregation, and Phase 02R closure-readiness evidence. This report
is candidate evidence only. It does not approve Gate 2R.8, does not declare
Phase 02R complete, does not execute legacy migration, and does not activate
production serving.

## Boundary

- Gate 2R.8 approval manifest: not created by evidence collection.
- Phase 02R final closure: not declared by evidence collection.
- Production activation: not performed.
- Legacy migration: not executed.
- Live database execution: static-only unless explicitly rerun with live DB settings.

## Evidence

See \\`docs/release-evidence/atlas/phase-02r/gate-2r8/evidence_index.md\\`.
EOF

cat > "$INDEX" <<EOF
# Phase 2R Gate 2R.8 Evidence Index

**Generated:** $timestamp
**Branch:** $branch
**Source commit:** $head_sha
**Status:** $status
**Gate 2R.8:** candidate evidence collected
**Phase 02R closure:** pending human approval and final closure decision

## Raw Evidence

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.8 control authorisation from Gate 2R.7 | \\`raw/gate-control.json\\`, \\`raw/preflight.txt\\` |
| Gate 2R.8 implementation verifier | \\`raw/verify_phase02r.txt\\`, \\`raw/verify_phase02r_gate2r8.json\\` |
| PostgreSQL/static-readiness disclosure | \\`raw/verify_phase02r_gate2r8_postgres.txt\\` |
| Legacy migration disposition manifest | \\`raw/legacy_migration_manifest.json\\` |
| Real-corpus retrieval evaluation report | \\`raw/real_corpus_evaluation_report.json\\` |
| Audit bundle and prior-gate reference aggregation | \\`raw/audit_bundle.json\\` |
| Closure-readiness validation | \\`raw/closure_validation.json\\` |
| Focused Gate 2R.8 tests | \\`raw/focused_tests.txt\\` |
| Compile checks | \\`raw/compileall.txt\\` |
| Raw evidence checksums | \\`raw/SHA256SUMS.txt\\` |
EOF

cat > "$AUDIT" <<EOF
# Phase 2R Gate 2R.8 Audit Record

**Generated:** $timestamp
**Status:** Pending human approval and final Phase 02R closure decision
**Candidate verification status:** $status

The evidence collector emits no final audit verdict. A separate approval
manifest and final closure record are required before Phase 02R can be declared
complete.
EOF

rm -rf "$EVIDENCE_ROOT/raw"
mkdir -p "$EVIDENCE_ROOT/raw" "$(dirname "$REPORT")"
cp "$WORK_REPORT" "$REPORT"
cp "$INDEX" "$EVIDENCE_ROOT/evidence_index.md"
cp "$AUDIT" "$EVIDENCE_ROOT/audit_report.md"
cp "$RAW"/* "$EVIDENCE_ROOT/raw/"
rm -f "$EVIDENCE_ROOT/collection_failure.md"

echo "PHASE 02R GATE $GATE CANDIDATE EVIDENCE COLLECTED"
echo "status=$status"
echo "source_commit=$head_sha"
exit "$overall_rc"
