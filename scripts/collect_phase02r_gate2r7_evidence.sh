#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE="2R.7"
EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r7"
REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r7_closure_report.md"
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
capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.7
capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.7 --mode implementation
capture verify_phase02r_gate2r7.json "$PYTHON_BIN" scripts/verify_phase02r_gate2r7.py --mode implementation --json
capture verify_phase02r_gate2r7_postgres.txt bash scripts/verify_phase02r_gate2r7_postgres.sh
capture grounded_tutor_response.json "$PYTHON_BIN" scripts/curriculum/build_phase02r_gate2r7_grounded_tutor.py --json
capture tutor_packet.json "$PYTHON_BIN" scripts/curriculum/export_phase02r_gate2r7_tutor_packet.py --json
capture tutor_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r7_tutor.py --json
capture focused_tests.txt timeout 120 "$PYTHON_BIN" -m pytest -q tests/unit/phase02r/test_gate2r7_grounded_tutor.py --no-cov

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

This report covers Gate 2R.7 implementation evidence for grounded learner tutor service-layer controls, active corpus retrieval hierarchy, safe non-authoritative fallback, append-only provenance persistence, audience-specific provenance views, and operational readiness checks only.

It does not approve Gate 2R.7, does not authorise Gate 2R.8, does not wire legacy migration/evaluation closure, does not add learner-facing API routes, and does not execute a live database migration. PostgreSQL evidence is static because this package adds service-layer tutor controls only.
EOF

cat > "$INDEX" <<EOF
# Phase 2R Gate $GATE Evidence Index

**Generated:** $timestamp
**Status:** $status
**Source commit:** \`$head_sha\`
**Environment:** see \`raw/environment.txt\`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.7 preflight authorised from Gate 2R.6 | \`raw/preflight.txt\` |
| Gate 2R.7 integrated verifier | \`raw/verify_phase02r.txt\`, \`raw/verify_phase02r_gate2r7.json\` |
| Grounded learner tutor response is deterministic and hashable | \`raw/grounded_tutor_response.json\`, \`raw/tutor_packet.json\` |
| Tutor retrieves from active approved corpus hierarchy | \`raw/grounded_tutor_response.json\`, \`raw/tutor_validation.json\` |
| Safe fallback emits no authoritative CAPS claim | \`raw/tutor_validation.json\` |
| Tutor provenance is persisted append-only | \`raw/tutor_packet.json\`, \`raw/tutor_validation.json\` |
| Audience-specific provenance views are access-shaped | \`raw/tutor_packet.json\`, \`raw/tutor_validation.json\` |
| Ownership, consent, safety, rate, budget controls are enforced at service contract level | \`raw/tutor_validation.json\` |
| Gate boundary excludes Gate 2R.8 migration/evaluation closure | \`raw/tutor_packet.json\` |
| PostgreSQL/Alembic static-readiness disclosed | \`raw/verify_phase02r_gate2r7_postgres.txt\` |
| Focused Gate 2R.7 tests | \`raw/focused_tests.txt\` |
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
