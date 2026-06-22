#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

ALLOW_DIRTY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-dirty) ALLOW_DIRTY=1; shift ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "Git is required for evidence attribution." >&2; exit 3; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Evidence must be collected inside a Git worktree." >&2; exit 3; }
if [[ "$ALLOW_DIRTY" != "1" && -n "$(git status --porcelain)" ]]; then
  echo "Gate 2R.4 evidence collection requires a clean worktree. Commit implementation first or pass --allow-dirty for local rehearsal only." >&2
  exit 3
fi

EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r4"
RAW="$EVIDENCE_ROOT/raw"
REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r4_closure_report.md"
mkdir -p "$RAW" "$(dirname "$REPORT")"
rm -rf "$RAW"
mkdir -p "$RAW"

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
branch="$(git branch --show-current || true)"
head_sha="$(git rev-parse HEAD)"

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
  if [[ "$rc" -ne 0 && "$overall_rc" -eq 0 ]]; then overall_rc="$rc"; fi
  return 0
}

capture preflight.txt bash scripts/preflight_phase02r.sh --gate 2R.4
capture verify_phase02r.txt bash scripts/verify_phase02r.sh --gate 2R.4
capture verify_phase02r_postgres.txt bash scripts/verify_phase02r_gate2r4_postgres.sh
capture curriculum_graph_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r4_graph.py --section graph --json
capture mapping_review_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r4_graph.py --section mapping-review --json
capture tier1_support_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r4_graph.py --section tier1 --json
capture language_authority_validation.json "$PYTHON_BIN" scripts/curriculum/validate_phase02r_gate2r4_graph.py --section language --json
capture graph_export.json "$PYTHON_BIN" scripts/curriculum/export_phase02r_curriculum_graph.py --json

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%f\n' | sort | while read -r name; do sha256sum "$name"; done > SHA256SUMS.txt
)

status="Candidate verification failed"
recommendation="Gate 2R.4 remains blocked. Review failing raw evidence."
if [[ "$overall_rc" -eq 0 ]]; then
  status="Candidate verification passed — approval pending"
  recommendation="Candidate evidence may proceed to independent review. The collector has not approved or closed the gate. Gate 2R.5 remains blocked."
fi

cat > "$EVIDENCE_ROOT/evidence_index.md" <<EOF
# Phase 02R Gate 2R.4 Evidence Index

**Generated:** $timestamp  
**Status:** $status  
**Branch:** \\`$branch\\`  
**Source commit:** \\`$head_sha\\`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.4 preflight | \\`raw/preflight.txt\\` |
| Gate 2R.4 implementation verifier | \\`raw/verify_phase02r.txt\\` |
| Gate 2R.4 PostgreSQL/static migration proof | \\`raw/verify_phase02r_postgres.txt\\` |
| Curriculum graph validation | \\`raw/curriculum_graph_validation.json\\` |
| Mapping review / maker-checker validation | \\`raw/mapping_review_validation.json\\` |
| Tier 1 support readiness validation | \\`raw/tier1_support_validation.json\\` |
| Language authority validation | \\`raw/language_authority_validation.json\\` |
| Deterministic graph export | \\`raw/graph_export.json\\` |
| Raw evidence checksums | \\`raw/SHA256SUMS.txt\\` |

## Boundary

This evidence covers Gate 2R.4 only. It does not activate a corpus, rebuild a retrieval projection, create embeddings, or change generation/tutor/learner-facing behaviour.
EOF

cat > "$REPORT" <<EOF
# Phase 02R Gate 2R.4 Candidate Closure Report

**Generated:** $timestamp  
**Status:** $status  
**Branch:** \\`$branch\\`  
**Source commit:** \\`$head_sha\\`  
**Clean worktree at collection start:** $([[ "$ALLOW_DIRTY" == "1" ]] && echo "not required for rehearsal" || echo "yes")

## Result

$recommendation

## Evidence

See \\`$EVIDENCE_ROOT/\\`. Every raw artifact is listed in \\`raw/SHA256SUMS.txt\\`.

## Gate boundary

Gate 2R.4 remains a curriculum graph and reviewed mapping readiness gate. This report does not approve the gate and does not authorise Gate 2R.5.

## Approval discipline

Create \\`docs/roadmap/execution/atlas/phase_02r_gate_2r4_approvals.json\\` only after this evidence is committed and reviewed.
EOF

echo "PHASE 02R GATE 2R.4 CANDIDATE EVIDENCE COLLECTED"
echo "status=$status"
echo "source_commit=$head_sha"
exit "$overall_rc"
