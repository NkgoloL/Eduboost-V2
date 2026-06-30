#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }

EXEC_DIR="docs/roadmap/execution/atlas"
EVIDENCE_DIR="docs/release-evidence/atlas/phase-05"
RAW_DIR="$EVIDENCE_DIR/raw"
PLAN="$EXEC_DIR/phase_05_execution_plan.md"
REPORT="$EXEC_DIR/phase_05_implementation_report.md"
INDEX="$EVIDENCE_DIR/phase_05_evidence_index.md"
AUDIT="$EVIDENCE_DIR/phase_05_audit_report.md"
mkdir -p "$EXEC_DIR" "$RAW_DIR"

[[ -f "$PLAN" ]] || { echo "Missing $PLAN" >&2; exit 3; }
grep -q 'PHASE_05_START_APPROVED=true' "$PLAN" || { echo "Phase 5 plan is not approved" >&2; exit 4; }

SOURCE_BRANCH="$(git branch --show-current)"
SOURCE_COMMIT="$(git rev-parse HEAD)"
COLLECTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

run_capture() {
  local name="$1"; shift
  echo "+ $*" | tee "$RAW_DIR/$name.txt"
  "$@" 2>&1 | tee -a "$RAW_DIR/$name.txt"
  local status=${PIPESTATUS[0]}
  echo "exit_code=$status" | tee -a "$RAW_DIR/$name.txt"
  return "$status"
}

{
  echo "collected_at=$COLLECTED_AT"
  echo "branch=$SOURCE_BRANCH"
  echo "commit=$SOURCE_COMMIT"
  echo "python=$($PYTHON_BIN --version 2>&1)"
  echo "python_executable=$PYTHON_BIN"
  echo "platform=$(uname -a)"
  echo "docker=$(docker --version 2>/dev/null || echo unavailable)"
  echo "docker_compose=$(docker compose version 2>/dev/null || echo unavailable)"
  echo "node=$(node --version 2>/dev/null || echo unavailable)"
  echo "pnpm=$(pnpm --version 2>/dev/null || corepack pnpm --version 2>/dev/null || echo unavailable)"
  echo "worktree_before_collection:"
  git status --short
} > "$RAW_DIR/environment.txt"

run_capture verify_phase5 bash scripts/verify_phase5.sh
run_capture verify_phase5_postgres bash scripts/verify_phase5_postgres.sh
run_capture migration_graph "$PYTHON_BIN" scripts/verify_migration_graph.py
run_capture schema_integrity "$PYTHON_BIN" scripts/validate_schema_integrity.py

"$PYTHON_BIN" - <<'PY' > "$RAW_DIR/router_inventory.txt"
from app.api_v2 import app
for route in sorted(app.routes, key=lambda item: item.path):
    if '/tutor/' in route.path or route.path.endswith('/tutor/sessions'):
        methods=','.join(sorted(getattr(route,'methods',[]) or []))
        print(f"{methods:20s} {route.path}")
PY

cat > "$REPORT" <<EOF
# Phase 5 Implementation Report — Safe Learner AI Tutor

**Generated:** $COLLECTED_AT  
**Source branch:** \`$SOURCE_BRANCH\`  
**Source commit:** \`$SOURCE_COMMIT\`  
**Status:** Verification complete — independent audit and canonical merge closure pending

## Objective

Deliver a lesson-scoped, privacy-preserving, age-appropriate tutor with ownership, consent, PII, prompt-injection, output-safety, budget, rate, cancellation, fallback, accessibility and escalation controls.

## Delivered implementation

- Tutor session, message and escalation persistence.
- Migration \`20260615_1200_p5_tutor\` from the Phase 4 head.
- Learner/lesson ownership and active-consent route gates.
- Strict request schemas that reject actor spoofing and unknown fields.
- PII redaction before provider calls and persistence; original learner text represented only by SHA-256 digest.
- Prompt-injection and high-risk input blocking before provider calls.
- Full provider-response validation before controlled SSE emission.
- Local non-deceptive fallback for policy, provider, network and budget failures.
- Per-user/tenant token budgets and endpoint rate limiting.
- Context-hash invalidation when the bound lesson changes.
- Idempotent client message IDs and immutable-after-insert messages.
- Educator/safeguarding escalation records.
- Accessible learner chat component with stop control, live region, privacy notice and offline messaging.
- Tutor metrics, runbook and safety ADR.

## Verification summary

- Fast verification: passed — see \`raw/verify_phase5.txt\`.
- Disposable PostgreSQL verification: passed — see \`raw/verify_phase5_postgres.txt\`.
- Migration graph and schema integrity: passed.
- Phase 1–4 regression gates: included by the verification scripts.
- Frontend type-check and focused component tests: included by the fast verifier.

## Deviations and residual work

- Provider output is buffered and validated before controlled SSE chunks are sent. This is intentional so unsafe partial provider output is never displayed.
- Phase 6 remains responsible for broader production alert routing and cross-service dashboards.
- Independent sampled tutor-quality and safeguarding review must be completed before closure.
- This report does not mark the phase complete; the audit, merge commit and post-merge evidence must be finalised first.

## Source-state declaration

All evidence in \`docs/release-evidence/atlas/phase-05/raw/\` was collected from commit \`$SOURCE_COMMIT\` on branch \`$SOURCE_BRANCH\` at \`$COLLECTED_AT\`.
EOF

cat > "$INDEX" <<EOF
# Phase 5 Evidence Index — Safe Learner AI Tutor

**Collected:** $COLLECTED_AT  
**Branch:** \`$SOURCE_BRANCH\`  
**Commit:** \`$SOURCE_COMMIT\`  
**Status:** Complete for audit review; canonical post-merge confirmation pending

| Criterion | Status | Evidence |
|---|---|---|
| Approved pre-execution plan | Verified | \`$PLAN\` and Git history |
| Python/toolchain attributable | Verified | \`raw/environment.txt\` |
| Tutor safety and schema tests | Verified | \`raw/verify_phase5.txt\` |
| Ownership/consent/routing contracts | Verified | \`raw/verify_phase5.txt\`, \`raw/router_inventory.txt\` |
| PII and prompt-injection fail closed | Verified | \`raw/verify_phase5.txt\` |
| Provider/budget fallback is non-deceptive | Verified | focused and PostgreSQL tests |
| PostgreSQL migration and constraints | Verified | \`raw/verify_phase5_postgres.txt\` |
| Message immutability and idempotency | Verified | \`raw/verify_phase5_postgres.txt\` |
| Safe persisted tutor exchange | Verified | \`raw/verify_phase5_postgres.txt\` |
| Escalation without provider call | Verified | \`raw/verify_phase5_postgres.txt\` |
| SSE cancellation/disconnect contract | Verified | \`raw/verify_phase5.txt\` and route inventory |
| Frontend accessibility/type contract | Verified | \`raw/verify_phase5.txt\` |
| Phase 1–4 regressions | Verified | \`raw/verify_phase5.txt\`, \`raw/verify_phase5_postgres.txt\` |
| Migration graph / schema integrity | Verified | \`raw/migration_graph.txt\`, \`raw/schema_integrity.txt\` |
| Independent sampled-quality review | Pending | Final audit |
| Canonical merge and post-merge CI | Pending | Merge commit and CI URL |

## Evidence integrity

See \`raw/SHA256SUMS.txt\`. Any evidence change requires regeneration of the manifest and re-audit.
EOF

cat > "$AUDIT" <<EOF
# Phase 5 Independent Audit Report — Safe Learner AI Tutor

**Prepared:** $COLLECTED_AT  
**Candidate branch:** \`$SOURCE_BRANCH\`  
**Candidate commit:** \`$SOURCE_COMMIT\`  
**Verdict:** **Pending independent audit**

This file is an audit workpaper, not a self-issued Pass.

## Mandatory independent procedures

- [ ] Confirm the execution plan was approved and committed before production-code work.
- [ ] Reproduce cross-learner, unrelated-lesson and missing-consent negative tests.
- [ ] Verify recognised PII is absent from provider-bound context, stored messages and general logs.
- [ ] Reproduce prompt-injection and high-risk input blocking and confirm the provider is not called.
- [ ] Reproduce unsafe/low-quality provider-output containment.
- [ ] Reproduce provider, budget and connectivity fallback and verify non-deceptive wording.
- [ ] Inspect SSE behaviour and confirm no unvalidated partial output reaches the learner.
- [ ] Review the accessible chat interaction, live region, keyboard operation, stop control and privacy notice.
- [ ] Sample at least 20 representative tutor questions across supported Grade 4 Mathematics journeys and record quality/safety results.
- [ ] Review all open tutor escalations created during evaluation.
- [ ] Confirm Phase 1–4 regressions, migration recovery and post-merge CI on the canonical merge commit.
- [ ] Confirm no unresolved Critical or High finding remains.

## Findings

| ID | Severity | Finding | Status / remediation |
|---|---|---|---|
| P5-A01 | TBD | Independent procedures not yet signed | Open |

## Final decision

- [ ] Pass
- [ ] Pass with non-blocking observations
- [ ] Fail

**Auditor:** TBD  
**Independence declaration:** TBD  
**Date:** TBD  
**Canonical merge commit reviewed:** TBD
EOF

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

echo "Phase 5 evidence collected under $EVIDENCE_DIR"
echo "Independent audit and post-merge closure are still required."
