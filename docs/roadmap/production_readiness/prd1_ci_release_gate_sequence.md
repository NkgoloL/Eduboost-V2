# PRD-1 Required CI and Release Gate Convergence Sequence

| Slice | Name | Purpose |
|---|---|---|
| PRD-1.0 | CI/release-gate stream authority and register | Establish PRD-1 authority and sub-slice register. |
| PRD-1.1 | CI inventory authority | Inventory all CI, workflow, release, check, branch-protection, and OpenAPI command sources. |
| PRD-1.2 | Required check classification | Classify checks as required, advisory, stale, legacy, release-only, or blocked. |
| PRD-1.3 | Workflow canonicalisation | Standardise pytest invocation, master/main semantics, release workflow ambiguity, and OpenAPI artifact references. |
| PRD-1.4 | Release gate definition | Define authoritative release gate checks and release-blocking rules. |
| PRD-1.5 | CI convergence evidence | Capture evidence that required checks are stable/green or explicitly blocked. |
| PRD-1.6 | Release readiness register | Record release readiness state without authorising release. |
| PRD-1.7 | Authority reconciliation | Reconcile PRD-1 records, CI state, release-gate state, and PRD-0 handoff state. |
| PRD-1.8 | Final evidence capture | Capture final PRD-1 evidence bundle. |
| PRD-1.9 | Controlled handoff to PRD-2 | Close PRD-1 and authorise PRD-2 handoff without implementing runtime KG. |

PRD-1 ends only with a controlled handoff to PRD-2. It does not authorise production deployment, public beta, live learner traffic, billing, or payment processing.
