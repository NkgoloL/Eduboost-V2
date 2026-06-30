# Recommended Operating Model

## Purpose

This operating model turns the repository governance rules into the day-to-day
workflow for EduBoost V2. It applies until the repository owner replaces it with
a signed release-management decision.

This is an execution contract. It does not make the project release-ready by
itself, and it does not replace the current state, North Star TODO, CI evidence,
staging evidence, or release-owner go/no-go decision.

## 1. Single Source Of Truth

Use these sources in order when planning or reporting project state:

| Source | Role |
| --- | --- |
| `docs/current_state.md` | Generated technical baseline from local checks |
| `docs/project_status.md` | Human-readable status index and release posture |
| `TODO.md` | North Star execution backlog and evidence requirements |
| `docs/repository_governance.md` | Repository authority, branch, PR, and release rules |
| `docs/release/EVIDENCE_INDEX.md` | Release evidence inventory |

Operating rules:

- Do not claim release-ready, public-beta-ready, or production-ready status
  unless `docs/current_state.md` is green and the release evidence bundle is
  current.
- Do not mark backlog items done unless the referenced evidence artifact can be
  opened and read.
- Treat generated docs as generated. Refresh them through their scripts or Make
  targets instead of editing them manually.

## 2. Evidence-First Delivery

Every implementation change must produce evidence that matches the risk of the
change.

Minimum PR evidence:

- problem statement and scoped files
- linked issue, TODO item, ADR, incident, or release gate
- exact validation commands and outputs
- security, POPIA, accessibility, deployment, and rollback impact assessment
- reviewer focus areas

High-risk evidence:

| Change class | Required evidence |
| --- | --- |
| Auth, session, RBAC | Object-level authorization tests or inspection record |
| Learner, guardian, consent, erasure, export | POPIA sweep or targeted privacy evidence |
| AI generation, CAPS, content safety | Prompt/output safety and curriculum evidence |
| Database migrations | Migration, rollback, and schema integrity evidence |
| Deployment, secrets, infrastructure | Staging smoke, rollback, and secret handling evidence |
| Billing, notifications | Provider callback, reconciliation, and delivery evidence |

Operating rules:

- Repository-side implementation is not the same as CI, staging, legal,
  security, product, or production verification.
- Evidence files must describe what was actually run. Placeholders are allowed
  only when they are clearly marked as pending.
- Use the status vocabulary from `TODO.md`: `[x]`, `[verify]`, `[ ]`,
  `[external]`, `[post-beta]`, and `[blocked]`.

## 3. Protected Change Flow

All work moves through a predictable intake and review path.

1. Open or link an issue, TODO item, ADR, incident, or release gate.
2. Create a short-lived branch for the change.
3. Keep the change scoped to one risk area when practical.
4. Open a PR with the repository PR template completed.
5. Pass required local checks before requesting review.
6. Resolve review comments and update evidence before merge.
7. Delete merged feature branches after merge.

Required local checks by change type:

| Change type | Checks |
| --- | --- |
| Runtime/API | `make runtime-check`, `make openapi-check`, `make route-inventory-check` |
| Architecture | `make architecture-gates` or the relevant import-linter target |
| Backend unit behavior | targeted `pytest -c pytest.ini ... -q --no-cov` |
| Frontend behavior | lint, type-check, unit tests, and browser evidence where applicable |
| Release governance | relevant `make ...-check` release evidence target |
| Repository governance | `make verify-repo-state`, `make recommended-operating-model-check` |

## 4. Release Control

Release work is gated by evidence, not by intent.

Release sequence:

1. Refresh `docs/current_state.md`.
2. Confirm CI is authoritative for the target branch.
3. Confirm migration, schema integrity, backup, restore, rollback, and staging
   smoke evidence are current.
4. Confirm POPIA, legal, security, product, and CAPS/content sign-offs are
   captured where required.
5. Complete the release-owner go/no-go decision before tagging.

Operating rules:

- Only the repository owner or delegated release manager may tag releases from
  the canonical production branch.
- A release candidate tag must point back to the canonical repository and a
  current release evidence bundle.
- A no-go decision is a valid release outcome and must be recorded honestly.
- Public beta and production launch remain blocked until external approvals and
  runtime evidence are complete.

## 5. Operating Cadence And Accountability

Use a lightweight cadence so blockers do not disappear into the evidence pile.

| Cadence | Activity | Output |
| --- | --- | --- |
| Daily during active release work | Review failed checks and open blockers | Updated TODO status or issue comments |
| Twice weekly | Evidence review | Updated evidence index or release bundle |
| Weekly | Risk review across security, POPIA, AI safety, CAPS, billing, and deployment | Decision log entry or explicit no-change note |
| Before every release candidate | Release readiness review | Go/no-go memo and release-owner decision |
| After beta | Retrospective and outcome review | Beta outcome report and follow-up action register |

Accountability rules:

- Technical approval, privacy/POPIA approval, rollback ownership, and
  post-deploy verification must be assigned before a release candidate tag.
- External approvals stay `[external]` until a real person or system provides
  the evidence.
- The release owner is accountable for the decision record, not for bypassing
  missing evidence.

## Command

```bash
make recommended-operating-model-check
```

This command validates the operating-model contract wording and its connection
to the repository evidence workflow. It is not a release go/no-go decision.
