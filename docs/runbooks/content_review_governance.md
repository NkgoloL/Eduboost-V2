# Content Review Governance Runbook

## Purpose

Operate and contain the Phase 3 educator-consensus workflow without weakening quorum, auditability, or learner-safety controls.

## Stale reviews

1. Check `eduboost_content_review_stale_assignments`.
2. Query `GET /content-review/assignments/stale` as a senior reviewer or curriculum lead.
3. Review reminder and escalation timestamps.
4. Reassign through `POST /content-review/assignments/{assignment_id}/reassign`.
5. Never change an artifact to approved because a review is overdue.

## Incorrect approval

1. Quarantine the artifact immediately.
2. Record a reason code and incident correlation ID.
3. Confirm learner delivery and Phase 2 retrieval no longer return the artifact.
4. Preserve all review decisions and transition events.
5. Create a corrected artifact version; do not edit the approved version in place.

## Emergency quarantine

1. Use the protected quarantine endpoint.
2. Verify artifact status and retrieval exclusion.
3. Invalidate any downstream cache or serving index.
4. Notify the Curriculum Lead, Security/Privacy reviewer, and Release Manager.
5. Open an incident record when learner exposure may have occurred.

## Stuck publication

1. Confirm quorum, rubric versions, source approval, and `publication_eligible`.
2. Confirm the artifact passed staging and production promotion gates.
3. Inspect blocking reject, quarantine, or revision-required decisions.
4. Do not bypass the service by updating database status directly.

## Audit investigation

- Read `content_review_decisions` and `content_state_transition_events`.
- Do not attempt UPDATE or DELETE; database triggers intentionally reject mutation.
- Preserve query output with commit, environment, and time metadata.

## Rollback

Disable Phase 3 mutation routes or roll back application code. Preserve review and audit tables. Prefer a forward fix for schema problems; destructive downgrade is not the default because historical review evidence must remain intact.
