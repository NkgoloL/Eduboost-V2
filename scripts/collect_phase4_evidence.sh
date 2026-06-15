#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
RAW="docs/release-evidence/phase-04/raw"
mkdir -p "$RAW"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="python3"; fi

{
  date -u +'%Y-%m-%dT%H:%M:%SZ'
  git status --short
  echo "branch=$(git branch --show-current)"
  echo "commit=$(git rev-parse HEAD)"
  "$PYTHON_BIN" --version
  docker --version || true
  docker compose version || true
} > "$RAW/environment.txt"

set -o pipefail
bash scripts/verify_phase4.sh 2>&1 | tee "$RAW/phase4_fast_verification.txt"
bash scripts/verify_phase4_postgres.sh 2>&1 | tee "$RAW/phase4_postgres_verification.txt"
"$PYTHON_BIN" scripts/verify_migration_graph.py 2>&1 | tee "$RAW/migration_graph.txt"
if [[ -f scripts/validate_schema_integrity.py ]]; then
  "$PYTHON_BIN" scripts/validate_schema_integrity.py 2>&1 | tee "$RAW/schema_integrity.txt"
fi

git grep -n -E 'approve_artifact|test_admin_can_approve_artifact_route|/artifacts/\{artifact_id\}/approve' -- app docs tests audits \
  > "$RAW/legacy_approval_search.txt" || true
if [[ -s "$RAW/legacy_approval_search.txt" ]]; then
  echo 'Legacy approval references found; evidence collection failed' >&2
  exit 1
fi

find "$RAW" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW/SHA256SUMS"
COMMIT="$(git rev-parse HEAD)"
BRANCH="$(git branch --show-current)"
cat > docs/release-evidence/phase-04/phase_04_evidence_index.md <<EVIDENCE
# Phase 4 Evidence Index — IRT Quality and Self-Healing Controls

**Status:** Evidence Complete — independent audit pending  
**Source branch:** \`$BRANCH\`  
**Source commit:** \`$COMMIT\`  
**Collected:** $(date -u +'%Y-%m-%dT%H:%M:%SZ')

| Criterion | Status | Evidence |
|---|---|---|
| Approved minimum sample/data-quality policy | Verified | \`raw/phase4_fast_verification.txt\` |
| Healthy/monitor/review/quarantine/retire decisions | Verified | \`raw/phase4_fast_verification.txt\` |
| No automatic answer-position mutation | Verified | \`raw/phase4_fast_verification.txt\` |
| Quarantined/retired items excluded from serving | Verified | \`raw/phase4_fast_verification.txt\` and PostgreSQL run |
| Rewrites return to Phase 3 pending review | Verified | \`raw/phase4_fast_verification.txt\` |
| Durable nightly job and admin controls registered | Verified | \`raw/phase4_fast_verification.txt\` |
| Migration from Phase 3 and recovery | Verified | \`raw/phase4_postgres_verification.txt\` |
| Append-only calibration events | Verified | \`raw/phase4_postgres_verification.txt\` |
| Phase 1-3 regression | Verified | fast and PostgreSQL verification logs |
| Migration graph and schema integrity | Verified | \`raw/migration_graph.txt\`, \`raw/schema_integrity.txt\` |
| Raw evidence hashes | Verified | \`raw/SHA256SUMS\` |

No audit verdict is implied by this index. The phase remains open until an independent audit is completed against the canonical merge commit.
EVIDENCE

cat > docs/roadmap/execution/phase_04_implementation_report.md <<REPORT
# Phase 4 Implementation Report — IRT Quality and Self-Healing Controls

**Status:** Evidence Complete — audit and closure review pending  
**Source branch:** \`$BRANCH\`  
**Source commit:** \`$COMMIT\`

## Delivered

- Versioned conservative 2PL session-rest-score calibration policy.
- Minimum response, unique learner, session, answered-ratio, fit and accuracy gates.
- States: uncalibrated, healthy, monitor, review required, quarantined, retired/rewrite review.
- Deterministic intervention decisions with no automatic answer-option mutation.
- Quarantine/retirement exclusion from learner item selection.
- Governed rewrite artifacts created as Phase 3 \`pending_review\` and never publication eligible.
- Durable nightly ARQ job, idempotency, run status, append-only event history, admin manual override.
- Prometheus metrics and evidence collection workflow.
- Phase 1-3 regression verification.

## Verification

See \`docs/release-evidence/phase-04/phase_04_evidence_index.md\` and its raw logs. All commands completed successfully during evidence collection.

## Residual closure work

- Independent statistical/assessment review of thresholds and session-rest-score ability proxy.
- Independent reproduction of critical state transitions and serving exclusions.
- Merge to canonical branch and post-merge repeat of evidence collection.
- Final audit verdict and phase-status register update.
REPORT

cat > docs/release-evidence/phase-04/phase_04_audit_report.md <<AUDIT
# Phase 4 Independent Audit Report — IRT Quality and Self-Healing Controls

**Status:** Audit Not Yet Started  
**Candidate source commit:** \`$COMMIT\`

## Required independent procedures

- [ ] Confirm the execution plan was approved before substantive implementation.
- [ ] Review the statistical assumptions and approve or amend the thresholds.
- [ ] Reproduce healthy, monitor, review-required, quarantine and retirement transitions.
- [ ] Confirm healthy item content is not automatically mutated.
- [ ] Confirm quarantined/retired items cannot be served.
- [ ] Confirm rewritten items enter Phase 3 pending review and cannot auto-publish.
- [ ] Reproduce scheduled execution, idempotency, failure recovery and manual override.
- [ ] Inspect append-only calibration event enforcement.
- [ ] Confirm Phase 1-3 regressions and migration recovery.
- [ ] Reconcile evidence hashes and canonical merge commit.

**Verdict:** Pending
AUDIT

printf 'Evidence collected under %s\n' "$RAW"
echo 'Do not mark Phase 4 complete until the independent audit and post-merge closure review pass.'
