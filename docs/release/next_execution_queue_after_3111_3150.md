# Next Execution Queue After DB-OWNERSHIP-001R / code_3111_3150

## Recommended next backend/database batches

1. `DIAG-ITEMS-001R / code_3151_3190` — decide whether `diagnostic_items` should be populated or formally document `irt_items` as canonical.
2. `AUDIT-WRITE-001R / code_3151_3190` — exercise a staging flow that writes `audit_events`, then verify and attach evidence.
3. `DB-ROLLBACK-001R / code_3151_3190` — add backup/restore/rollback evidence.
4. `JWT-001R / code_3151_3190` — attach production/staging secret provisioning, fallback-disabled proof, and rotation metadata.
5. `ARQ-001R / code_3151_3190` — prove live Redis worker enqueue/dequeue.

## Discipline

This batch documents ownership only. It does not change persistence semantics or close legal/security approvals.
