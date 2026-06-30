---
title: "ADR-005 — Database Rollback Policy"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-005 — Database Rollback Policy

**Status:** Proposed (awaiting sign-off)
**Date:** 2026-05-28
**Context:** T022B — Decide rollback policy for Alembic downgrade limitation

## Context

Alembic forward upgrade to head is required for deployment. A previous downgrade-to-base test failed because PostgreSQL enum types were still referenced by tables during downgrade. This creates a decision point for production rollback strategy.

## Decision Options

### Option A — Alembic downgrade is supported rollback

**Description:** Fix the enum dependency cycle and require all migrations to support `alembic downgrade base`.

**Requirements:**
- Repair enum downgrade ordering to handle dependency cycles
- Add CASCADE handling for enum drops
- Ensure all future migrations pass downgrade tests
- Add CI gate requiring downgrade to pass before merge

**Pros:**
- Standard Alembic workflow
- No external dependency on backup infrastructure
- Faster rollback time for simple schema changes

**Cons:**
- Complex to fix enum dependency cycles
- Downgrade may not preserve data integrity for complex migrations
- Requires ongoing maintenance of downgrade paths
- Risk of downgrade failing in production when needed most

### Option B — Restore-from-backup / forward-fix is production rollback (RECOMMENDED)

**Description:** Use database restore from backups as the primary rollback mechanism, with forward-fix for data correction if needed.

**Requirements:**
- Maintain tested backup/restore procedures
- Conduct regular DR restore drills (see Phase 2 T220-T221)
- Document RTO/RPO metrics
- Keep backup integrity verified
- Downgrade may remain unsupported for production rollback

**Pros:**
- Proven, reliable rollback method for production databases
- Restores exact state, including data
- No complex enum dependency management
- Industry standard for production systems
- Aligns with disaster recovery procedures

**Cons:**
- Slower rollback time than downgrade
- Requires backup infrastructure
- Data loss between backup and rollback point
- Requires DR procedures to be current

## Recommended Decision

**Option B — Restore-from-backup / forward-fix**

**Rationale:**
1. For production databases, restore-from-backup is the industry standard and more reliable than schema downgrade
2. EduBoost will have DR procedures in Phase 2 (T220-T221) that include restore drills
3. Enum dependency cycles are complex to fix and may introduce new bugs
4. Downgrade does not guarantee data integrity for complex migrations
5. Restore provides exact state recovery, including data that downgrade might not handle

## Consequences

If Option B is selected:
- Alembic downgrade may remain unsupported for production rollback
- DR restore evidence must be kept current before production launch
- Phase 2 DR drills (T220-T221) become critical path
- Documentation must clearly state that restore-from-backup is the authoritative rollback method
- CI should not require downgrade to pass for merge

## Sign-off Required

- **Database Owner:** [REQUIRED]
- **DevOps Lead:** [REQUIRED]
- **CTO/Engineering Lead:** [REQUIRED]

## References

- T022B: Decide rollback policy for Alembic downgrade limitation
- Phase 2 T220-T221: Disaster Recovery procedures
- `audits/migration/alembic_rollback_policy_gap_20260528.md`
