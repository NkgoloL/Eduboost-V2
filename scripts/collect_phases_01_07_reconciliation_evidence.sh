#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

IMPL="scripts/collect_phases_01_07_reconciliation_evidence_impl.sh"
REPORT="docs/roadmap/execution/atlas/phases_01_07_reconciliation_report.md"
EVIDENCE_DIR="docs/release-evidence/atlas/programme-reconciliation-01-07"
RAW_DIR="$EVIDENCE_DIR/raw"
INDEX="$EVIDENCE_DIR/evidence_index.md"
AUDIT="$EVIDENCE_DIR/audit_report.md"

mkdir -p "$RAW_DIR" "$(dirname "$REPORT")"

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
branch="$(git branch --show-current 2>/dev/null || printf 'unknown')"
commit="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
status_before="$(git status --short 2>/dev/null || true)"

set +e
bash "$IMPL" "$@" 2>&1 | tee "$RAW_DIR/collector_run.txt"
collector_rc=${PIPESTATUS[0]}
set -e

# If the underlying collector succeeded, keep its richer generated artifacts.
if [[ "$collector_rc" -eq 0 ]]; then
  printf '\nEvidence collection completed successfully.\n'
  exit 0
fi

# The previous collector used `set -e`, so it could terminate before creating
# the report/index/audit. Always create truthful failure artifacts.
if [[ ! -f "$REPORT" ]]; then
  cat > "$REPORT" <<EOF
# Phases 1–7 Reconciliation Report

**Generated:** $timestamp  
**Branch:** \`$branch\`  
**Source commit:** \`$commit\`  
**Status:** Verification Failed — evidence collection incomplete  
**Collector exit code:** \`$collector_rc\`

## Summary

The evidence collector executed the reconciliation verifier, but at least one
mandatory gate failed. This report is intentionally not a completion claim.

Review the raw collector output:

\`$RAW_DIR/collector_run.txt\`

## Source-state note

The worktree state captured before evidence generation was:

\`\`\`text
$status_before
\`\`\`

Final closure evidence must be regenerated from a committed implementation
candidate and then confirmed against the canonical merge commit.

## Required next actions

1. Resolve the first failing verification gate.
2. Commit the reconciliation implementation candidate.
3. Rerun the fast and PostgreSQL verification scripts.
4. Rerun this evidence collector.
5. Complete an independent audit.
EOF
fi

cat > "$INDEX" <<EOF
# Phases 1–7 Reconciliation Evidence Index

**Generated:** $timestamp  
**Branch:** \`$branch\`  
**Source commit:** \`$commit\`  
**Status:** Incomplete — verification failed  
**Collector exit code:** \`$collector_rc\`

| Evidence | Path | Status |
|---|---|---|
| Collector output | \`raw/collector_run.txt\` | Captured |
| Reconciliation report | \`$REPORT\` | Failure report generated |
| Fast verification | See collector output | Failed or incomplete |
| PostgreSQL verification | See collector output | Not authoritative until all gates pass |
| Independent audit | \`audit_report.md\` | Pending |

This index must not be used to mark any phase Verified Complete.
EOF

cat > "$AUDIT" <<EOF
# Phases 1–7 Reconciliation Audit

**Generated:** $timestamp  
**Source commit:** \`$commit\`  
**Verdict:** Fail — mandatory verification did not complete  
**Collector exit code:** \`$collector_rc\`

The evidence collector terminated because a mandatory verification gate failed.
No phase status may be advanced on the basis of this evidence set.

An independent re-audit is required after all gates pass on the canonical
source state.
EOF

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS.txt
)

printf '\nEvidence collection failed, but failure artifacts were generated.\n'
printf 'Report: %s\n' "$REPORT"
printf 'Index:  %s\n' "$INDEX"
printf 'Audit:  %s\n' "$AUDIT"
printf 'Raw:    %s\n' "$RAW_DIR/collector_run.txt"
exit "$collector_rc"
