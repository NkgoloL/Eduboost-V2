#!/usr/bin/env bash
set -euo pipefail

# EduBoost V2 — Next Batch: All Outstanding Tasks validation scaffold
#
# This script does NOT implement every outstanding task. Several require human sign-off,
# staging systems, legal/privacy review, or product decisions.
#
# It runs the mechanical validation gates and creates evidence placeholders needed
# for the next large batch.

ROOT="${1:-.}"
cd "$ROOT"

mkdir -p audits/migration audits/privacy audits/observability audits/dr audits/security docs/adr docs/engineering docs/operations

PYTHON_BIN=".venv/bin/python"
ALEMBIC_BIN=".venv/bin/alembic"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

if [[ ! -x "$ALEMBIC_BIN" ]]; then
  ALEMBIC_BIN="alembic"
fi

echo "== EduBoost next batch validation scaffold =="
echo "Repo: $(pwd)"
echo

echo "== Gate 1: pytest collection =="
"$PYTHON_BIN" -m pytest --collect-only --no-cov | tee audits/privacy/next_batch_collect_evidence.txt

echo
echo "== Gate 2: POPIA tests =="
"$PYTHON_BIN" -m pytest tests/popia --no-cov -v | tee audits/privacy/next_batch_popia_tests_evidence.txt

echo
echo "== Gate 3: Alembic heads =="
"$ALEMBIC_BIN" heads | tee audits/migration/next_batch_alembic_heads.txt

echo
echo "== Gate 4: Observability config =="
if command -v promtool >/dev/null 2>&1 && [[ -f prometheus/alerting_rules.yml ]]; then
  promtool check rules prometheus/alerting_rules.yml | tee audits/observability/next_batch_promtool_alerting.txt
else
  echo "promtool or prometheus/alerting_rules.yml unavailable; skipping" | tee audits/observability/next_batch_promtool_alerting.txt
fi

if command -v amtool >/dev/null 2>&1 && [[ -f alertmanager/alertmanager.yml ]]; then
  amtool check-config alertmanager/alertmanager.yml | tee audits/observability/next_batch_amtool.txt
else
  echo "amtool or alertmanager/alertmanager.yml unavailable; skipping" | tee audits/observability/next_batch_amtool.txt
fi

echo
echo "== Optional Gate 5: Disposable Postgres Alembic upgrade =="
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    docker rm -f eduboost-migration-test >/dev/null 2>&1 || true
    docker run -d --name eduboost-migration-test \
      -e POSTGRES_USER=eduboost_user \
      -e POSTGRES_PASSWORD=devpassword \
      -e POSTGRES_DB=eduboost_test \
      -p 55433:5432 \
      postgres:16-alpine >/dev/null

    for i in $(seq 1 30); do
      if docker exec eduboost-migration-test pg_isready -U eduboost_user -d eduboost_test >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done

    export DATABASE_URL="postgresql+asyncpg://eduboost_user:devpassword@localhost:55433/eduboost_test"
    "$ALEMBIC_BIN" upgrade head | tee audits/migration/alembic_upgrade_postgres_20260528.txt
    "$ALEMBIC_BIN" current | tee audits/migration/alembic_current_postgres_20260528.txt

    docker rm -f eduboost-migration-test >/dev/null 2>&1 || true
  else
    echo "Docker installed but daemon unavailable; skipping disposable Postgres upgrade." | tee audits/migration/alembic_upgrade_postgres_20260528.txt
  fi
else
  echo "Docker unavailable; skipping disposable Postgres upgrade." | tee audits/migration/alembic_upgrade_postgres_20260528.txt
fi

echo
echo "== Create outstanding-task evidence placeholders =="

cat > audits/privacy/popia_remaining_review_20260528.md <<'EOF'
# POPIA Remaining Review — 2026-05-28

## Outstanding human-review items

- T050 content filter decision: pending unless signed elsewhere.
- T114 Information Officer contact: must be real before launch.
- T115 Privacy Notice: requires Privacy/Legal/Information Officer review.
- T116 Breach Response Procedure: requires Security/Operations/Privacy review.
- T111D legacy DataSubjectRightsService reconciliation: pending unless completed in this branch.

## Required launch posture

No public/live learner-data launch may proceed while required compliance placeholders remain.
EOF

cat > audits/migration/alembic_rollback_policy_gap_20260528.md <<'EOF'
# Alembic Rollback Policy Gap — 2026-05-28

Known issue: downgrade-to-base previously failed due to PostgreSQL enum dependency cycles.

Decision required:

1. Support Alembic downgrade as rollback path and fix downgrade order/CASCADE handling; or
2. Declare restore-from-backup / forward-fix as authoritative production rollback model.

Until decided, production rollback posture is incomplete.
EOF

cat > docs/adr/ADR-005-database-rollback-policy.md <<'EOF'
# ADR-005 — Database Rollback Policy

Status: Proposed

## Context

Alembic forward upgrade to head is required for deployment. A previous downgrade-to-base test
failed because PostgreSQL enum types were still referenced by tables during downgrade.

## Decision

TBD. Choose exactly one supported rollback model:

1. Alembic downgrade is supported and must pass for all migrations.
2. Restore-from-backup / forward-fix is the supported production rollback path.

## Consequences

If option 1 is selected, enum downgrade ordering must be repaired.
If option 2 is selected, DR restore evidence must be kept current and downgrade may remain
unsupported for production rollback.
EOF

echo
echo "Next batch scaffold complete."
echo
echo "Suggested git commands:"
echo "git add audits docs"
echo "git commit -m \"phase1: scaffold outstanding remediation evidence\""
