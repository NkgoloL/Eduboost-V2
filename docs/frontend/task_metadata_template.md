# Frontend Task Metadata Template

Every Blocker or Critical task in TODO_V4.1 must capture the following metadata before work begins. Copy the table row below into PR descriptions, Jira tickets, or the evidence log.

| Field | Description | Example |
| --- | --- | --- |
| Task | Stable ID from TODO (`FE-P1-001`) | `FE-P1-005` |
| RC | RC gate that owns the work | `RC1` |
| Owner | Engineer / role accountable | `Frontend Tech Lead` |
| Blocks | IDs that cannot start until this task finishes | `FE-P1-038..044` |
| AC | Acceptance criteria as observable statements | `GET /api/health returns status/version` |
| Evidence | File path, CI link, or screenshot confirming AC | `docs/frontend/evidence/runtime/health-route.png` |
| Risk | Security · POPIA · Learner-safety · Performance · Product · Low | `Security` |
| Notes | Optional clarifications, defer reasons, or spike links | `Dependent on ADR-001` |

## Usage

1. Add a `Task Metadata` section to every PR touching RC1 blockers.
2. When deferring a task, set `RC = Deferred` and include the product decision link.
3. Mirror the same metadata into `docs/frontend/frontend_evidence_index.md` or the release evidence file when closing RC gates.
