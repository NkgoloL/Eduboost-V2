#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE="2R.5"
EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r5"
REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r5_closure_report.md"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fail_collection_precondition() {
  local reason="$1"
  mkdir -p "$EVIDENCE_ROOT"
  cat > "$EVIDENCE_ROOT/collection_failure.md" <<EOF
# Phase 2R Gate $GATE Evidence Collection Failure

**Generated:** $timestamp
**Status:** Failed

$reason

No gate approval or completion decision may be based on this failed collection.
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
base_sha="$(git merge-base HEAD origin/master 2>/dev/null || git rev-parse HEAD^)"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
WORK_EVIDENCE_ROOT="$WORKDIR/evidence"
RAW="$WORK_EVIDENCE_ROOT/raw"
INDEX="$WORK_EVIDENCE_ROOT/evidence_index.md"
AUDIT="$WORK_EVIDENCE_ROOT/audit_report.md"
WORK_REPORT="$WORKDIR/closure_report.md"
mkdir -p "$RAW"

overall_rc=0
capture() {
  local name="$1"; shift
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
import json, sys
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
  if [[ "$rc" -ne 0 && "$overall_rc" -eq 0 ]]; then overall_rc="$rc"; fi
  return 0
}

capture environment.txt bash -lc 'python3 --version; git --version; uname -a; git log -1 --oneline --decorate'
capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.5
capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.5 --mode implementation
capture verify_phase02r_gate2r5.json "$PYTHON_BIN" scripts/verify_phase02r_gate2r5.py --mode implementation --json
capture verify_phase02r_gate2r5_postgres.txt bash scripts/verify_phase02r_gate2r5_postgres.sh
capture semantic_corpus_manifest.json "$PYTHON_BIN" scripts/curriculum/build_phase02r_gate2r5_semantic_corpus.py --json
capture retrieval_projection.json "$PYTHON_BIN" scripts/curriculum/export_phase02r_gate2r5_retrieval_projection.py --json
capture retrieval_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r5_retrieval.py --json
capture focused_tests.txt "$PYTHON_BIN" -m pytest -q tests/unit/phase02r/test_gate2r5_semantic_corpus.py --no-cov

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' | sort | while read -r name; do sha256sum "$name"; done > SHA256SUMS.txt
)

status="Candidate verification failed"
recommendation="Gate $GATE remains blocked. Review failing raw evidence."
if [[ "$overall_rc" -eq 0 ]]; then
  status="Candidate verification passed — human approval pending"
  recommendation="Candidate evidence may proceed to independent review. The collector has not approved or closed the gate."
fi

cat > "$WORK_REPORT" <<EOF
# Phase 2R Gate $GATE Candidate Evidence Report

**Generated:** $timestamp
**Status:** $status
**Branch:** \`$branch\`
**Source commit:** \`$head_sha\`
**Base against origin/master:** \`$base_sha\`
**Clean worktree at collection start:** yes

## Result

$recommendation

## Evidence

See \`$EVIDENCE_ROOT/\`. Every raw artifact is listed in \`raw/SHA256SUMS.txt\`.

## Gate boundary

This report covers Gate 2R.5 implementation evidence for approved semantic corpus build/freeze controls, staging activation/rollback planning, and retrieval projection validation only.

It does not approve Gate 2R.5, does not authorise Gate 2R.6, does not wire production generation or tutor behaviour, and does not execute a live database migration. The PostgreSQL evidence is static unless a separate controlled live DB run is captured.
EOF

cat > "$INDEX" <<EOF
# Phase 2R Gate $GATE Evidence Index

**Generated:** $timestamp
**Status:** $status
**Source commit:** \`$head_sha\`
**Environment:** see \`raw/environment.txt\`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.5 preflight authorised from Gate 2R.4 | \`raw/preflight.txt\` |
| Gate 2R.5 integrated verifier | \`raw/verify_phase02r.txt\`, \`raw/verify_phase02r_gate2r5.json\` |
| Approved semantic corpus manifest is deterministic and hashable | \`raw/semantic_corpus_manifest.json\` |
| Retrieval projection contains only active approved corpus membership | \`raw/retrieval_projection.json\` |
| Active binding/corpus/binding-epoch retrieval controls reject stale or mixed reads | \`raw/retrieval_validation.json\` |
| PostgreSQL/Alembic corpus-table readiness disclosed | \`raw/verify_phase02r_gate2r5_postgres.txt\` |
| Focused Gate 2R.5 tests | \`raw/focused_tests.txt\` |
| Raw evidence checksums | \`raw/SHA256SUMS.txt\` |
EOF

cat > "$AUDIT" <<EOF
# Phase 2R Gate $GATE Audit Record

**Generated:** $timestamp
**Status:** Pending independent review
**Candidate verification status:** $status

No audit verdict is emitted by the evidence collector. The assigned reviewer must reproduce the required commands, inspect human decisions and source records, and issue a separate signed decision.
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
