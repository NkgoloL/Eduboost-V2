#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate) GATE="${2:-}"; shift 2 ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done
case "$GATE" in
  2R.0|2R.1|2R.2|2R.3|2R.4|2R.5|2R.6|2R.7|2R.8) ;;
  *) echo "Gate $GATE evidence collection is not supported." >&2; exit 2 ;;
esac

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.0" ]]; then
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r0"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md"
else
  GATE_FILE="${GATE/./}"
  GATE_DIR="${GATE,,}"
  GATE_DIR="${GATE_DIR/.}"
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-${GATE_DIR}"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_${GATE_FILE}_closure_report.md"
fi
mkdir -p "$EVIDENCE_ROOT"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

fail_collection_precondition() {
  local reason="$1"
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

record_skipped() {
  local name="$1"
  local reason="$2"
  printf "%s\n" "$reason" > "$RAW/$name"
  "$PYTHON_BIN" - "$RAW/$name.meta.json" "$reason" <<'PYMETA'
import json
import sys
from pathlib import Path
path, reason = sys.argv[1:]
Path(path).write_text(json.dumps({
    "command": [],
    "started_at": None,
    "finished_at": None,
    "duration_seconds": 0,
    "exit_code": None,
    "status": "not_run",
    "reason": reason,
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PYMETA
}

capture environment.txt bash -lc 'python3 --version; git --version; uname -a'
if [[ "$GATE" == "2R.0" ]]; then
  capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery
  capture verification.txt bash scripts/verify_phase02r.sh --gate 2R.0 --mode discovery
else
  if [[ "$GATE" == "2R.1" ]]; then
    capture gate-2r1-closure-verification.json \
      "$PYTHON_BIN" scripts/verify_phase02r_gate2r1.py --mode closure --json
  else
    raw_gate="${GATE,,}"
    raw_gate="${raw_gate/.}"
    if [[ "$GATE" == "2R.2" ]]; then
      capture gate-${raw_gate}-closure-verification.json \
        "$PYTHON_BIN" scripts/verify_phase02r_gate2r2.py --include-real-source --json
    elif [[ "$GATE" == "2R.3" ]]; then
      capture gate-${raw_gate}-closure-verification.json \
        "$PYTHON_BIN" scripts/verify_phase02r_gate2r3.py --include-real-source --json
    else
      capture gate-${raw_gate}-closure-verification.json \
        "$PYTHON_BIN" scripts/verify_phase02r_gate2r2_to_2r8.py --gate "$GATE" --mode closure --json
    fi
  fi
  closure_static_rc="$LAST_CAPTURE_RC"
  if [[ "$closure_static_rc" -eq 0 ]]; then
    capture postgres-verification.txt bash scripts/verify_phase02r_postgres.sh
  else
    record_skipped postgres-verification.txt \
      "PostgreSQL verification was not run because Gate $GATE closure prerequisites failed."
  fi
fi
(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' \
    | sort \
    | while read -r name; do sha256sum "$name"; done \
    > SHA256SUMS.txt
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

See \`$EVIDENCE_ROOT/\`. Every raw artifact is listed in
\`raw/SHA256SUMS.txt\`.

## Control boundary

This report is candidate evidence only. A separate evidence commit, human
review record, and approval commit are required before any gate transition.
EOF

cat > "$INDEX" <<EOF
# Phase 2R Gate $GATE Evidence Index

**Generated:** $timestamp
**Status:** $status
**Source commit:** \`$head_sha\`
**Environment:** see \`raw/environment.txt\`

| Evidence ID / claim | Artifact |
|---|---|
EOF
if [[ "$GATE" == "2R.0" ]]; then
  cat >> "$INDEX" <<'EOF'
| Gate 2R.0 preflight | `raw/preflight.txt` |
| Gate 2R.0 verification | `raw/verification.txt` |
EOF
else
  if [[ "$GATE" == "2R.1" ]]; then
    cat >> "$INDEX" <<'EOF'
| E-02R-020 — source-completeness inventory frozen | `raw/gate-2r1-closure-verification.json` |
| E-02R-021 — authority schema and append-only controls | `raw/gate-2r1-closure-verification.json`, `raw/postgres-verification.txt` |
| E-02R-022 — per-use rights policy tests | `raw/gate-2r1-closure-verification.json` |
| E-02R-023 — model-training use separately default-denied | `raw/gate-2r1-closure-verification.json` |
| Gate-state, migration, schema and control-set consistency | `raw/gate-2r1-closure-verification.json` |
| PostgreSQL migration/append-only proof | `raw/postgres-verification.txt` |
EOF
  else
    raw_gate="${GATE,,}"
    raw_gate="${raw_gate/.}"
    raw_name="gate-${raw_gate}-closure-verification.json"
    cat >> "$INDEX" <<EOF
| Gate $GATE implementation and closure controls | \`raw/$raw_name\` |
| PostgreSQL migration/append-only proof | \`raw/postgres-verification.txt\` |
EOF
  fi
fi
cat >> "$INDEX" <<'EOF'
| Raw evidence checksums | `raw/SHA256SUMS.txt` |
EOF

cat > "$AUDIT" <<EOF
# Phase 2R Gate $GATE Audit Record

**Generated:** $timestamp
**Status:** Pending independent review
**Candidate verification status:** $status

No audit verdict is emitted by the evidence collector. The assigned reviewer
must reproduce the required commands, inspect human decisions and source
records, and issue a separate signed decision.
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
