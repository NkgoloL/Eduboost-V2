# TODO Implementation Plan

## Purpose

This plan converts the open items in `TODO.md` into an execution sequence for
moving EduBoost V2 from RED / No-Go to an evidence-backed controlled beta
decision.

It does not change the project state. EduBoost remains not public-beta-ready and
not production-launch-ready until every required evidence artifact, CI run,
staging run, external approval, and release-owner decision exists and can be
opened.

## Operating Rules

- `TODO.md` remains the canonical task list and status vocabulary.
- This plan is the execution map for every outstanding `NS-*` item in `TODO.md`.
- Do not mark any task `[x]` unless its evidence artifact exists and can be
  opened.
- Keep `[external]`, `[blocked]`, and `[post-beta]` work visible instead of
  converting it into repository-side completion.
- Refresh generated state through `make refresh-current-state`; do not hand-edit
  `docs/current_state.md`.

## Critical Path Summary

1. Lock the known local baseline and capture the missing local evidence.
2. Make CI authoritative on the target branch and protect `master`.
3. Replace Cluster H phantom governance entries with real release artifacts.
4. Prove database migrations, frontend browser behavior, and runtime safety in
   disposable or staging environments.
5. Complete operations, POPIA/legal/security, CAPS/product, billing, and
   communications decisions.
6. Deploy to staging, execute smoke and telemetry checks, then run the formal
   beta go/no-go.

## Wave 1: Baseline Freeze And Local Evidence

Goal: preserve the current local green baseline while making unresolved local
evidence explicit.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-03 | Commit integrated repairs | Confirm the migration graph, POPIA, and AuthService repair files are in a clean scoped commit or already represented by pushed history. | Git commit hash recorded in `docs/release/unit_test_evidence.md` or release state snapshot. | Repair commit can be identified from the release bundle. |
| NS-04 | Unit-test evidence | Rerun `pytest -c pytest.ini tests/unit -q --no-cov` in the intended environment and capture complete output. | `docs/release/unit_test_evidence.md`. | Evidence shows full pass/skip counts and command context. |
| NS-05 | Warning triage | Reproduce the four known warnings, decide fix versus accepted debt, and create follow-up issue IDs for anything not fixed immediately. | Warning section in `docs/release/unit_test_evidence.md` or `docs/release/known_issues.md`. | Every warning is fixed, accepted with rationale, or tracked. |
| NS-13 | Current-state refresh | Run `make refresh-current-state` only after the baseline evidence is current. | Generated `docs/current_state.md`. | Current-state timestamp and gates match the latest local run. |

Recommended commands:

```bash
pytest -c pytest.ini tests/unit -q --no-cov
make refresh-current-state
make project-assistance-status-check
make recommended-operating-model-check
```

## Wave 2: CI Authority And Branch Governance

Goal: make GitHub Actions and protected branch settings the authoritative
release signal instead of local-only proof.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-06, NS-07 | CI unit suite | Trigger CI on `master`, verify the full unit suite runs, and capture the run URL and pass/skip counts. | `docs/release/ci_evidence.md`. | CI output includes the same required unit gate as local. |
| NS-08 | OpenAPI drift in CI | Confirm `make openapi-check` runs in CI and fails on drift. | CI evidence section with workflow/job URL. | OpenAPI drift check is visible in required CI jobs. |
| NS-09 | Migration graph in CI | Add or verify CI coverage for migration graph resolution. | CI evidence section with workflow/job URL. | Migration graph check passes remotely. |
| NS-10 | POPIA gate in CI | Add or verify CI coverage for POPIA gate/sweep checks. | CI evidence section with workflow/job URL. | POPIA checks pass remotely. |
| NS-11 | Frontend CI | Ensure lint, type-check, and unit tests run for the frontend. | CI evidence section with frontend job output. | Frontend quality jobs pass remotely. |
| NS-12 | Branch protection | Configure required checks, review rules, and no direct pushes on `master`. | `docs/release/branch_protection_evidence.md`. | Screenshot or settings export proves protection. |

Recommended commands:

```bash
gh workflow run <workflow-name> --ref master
gh run list --branch master --limit 10
gh run view <run-id> --log
```

## Wave 3: Release Governance And Cluster H Cleanup

Goal: replace inflated or placeholder Cluster H entries with named, readable
release governance artifacts.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-14 | Sign-off manifest shell | Create blank named sign-off fields for release owner, technical, POPIA/legal, security, product, rollback, and post-deploy verification. | `docs/release/sign_off_manifest.md`. | Manifest exists but unsigned fields remain pending/external. |
| NS-15 | Rollback runbook | Document API, frontend, database, config, and feature-flag rollback paths, including Alembic downgrade target or non-downgrade rationale. | `docs/release/rollback_runbook.md`. | Operator can follow rollback commands in staging/disposable environment. |
| NS-16 | Smoke checklist | Define post-deploy smoke coverage for `/health/deep`, login, lesson generation, consent grant, and POPIA export. | `docs/release/post_deploy_smoke_checklist.md`. | Checklist has commands, expected results, and owner fields. |
| NS-17 | Release bundle index | Create an index with only real links to existing evidence and pending placeholders clearly marked. | `docs/release/release_bundle_v1.0.0-rc2.md`. | Bundle has no fake or unreachable evidence claims. |
| NS-18 | PR template | Add a PR template covering scope, evidence, security/POPIA, deployment, rollback, and reviewer focus. | `.github/PULL_REQUEST_TEMPLATE.md`. | New PRs inherit the template. |
| NS-19 | Release hygiene checklist | Define hygiene checks for docs, generated artifacts, secrets, migrations, evidence links, and branch state. | `docs/release/release_hygiene_checklist.md`. | Checklist can be completed before release candidate tagging. |
| NS-20 | Release state snapshot | Capture SHA, test counts, TODO counts, known issues, and deferred scope. | `docs/release/release_state_snapshot.md`. | Snapshot matches the current commit and TODO state. |
| NS-21 | Audit trail index | Link release decisions, evidence files, CI runs, sign-offs, and external records. | `docs/release/audit_trail_index.md`. | Audit trail can answer what changed, who approved, and what evidence exists. |
| NS-22, NS-64 | Final closure certificate | Create the certificate template, but keep it unsigned until all evidence is complete. | `docs/release/final_closure_certificate.md`. | Certificate remains pending until final external approval. |
| NS-23 | Project status cleanup | Consolidate phantom Cluster H entries into one honest section linking real evidence. | `docs/project_status.md`. | Status page has one Cluster H governance section and no inflated closure claims. |

Recommended commands:

```bash
make release-owner-accountability-check
make beta-release-readiness-contract-check
make release-audit-trail-index-check
```

## Wave 4: Database Migration Runtime Proof

Goal: prove migrations and schema behavior against a real disposable PostgreSQL
target.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-24 | Upgrade proof | Run `alembic upgrade head` against disposable PostgreSQL with the intended app config. | `docs/release/migration_evidence.md`. | Upgrade completes and output is captured. |
| NS-25 | Schema integrity | Run schema integrity validation against the upgraded database. | `docs/release/migration_evidence.md`. | Schema check passes or exceptions are documented. |
| NS-26 | Downgrade/rollback | Run downgrade where supported or document a deliberate non-downgrade policy with backup/restore fallback. | `docs/release/migration_evidence.md` and rollback runbook update. | Rollback path is tested or explicitly scoped. |

Recommended commands:

```bash
alembic upgrade head
make schema-integrity
make migration-check
```

## Wave 5: Frontend And Browser Runtime Proof

Goal: prove the recovered learner experience against a live backend rather than
relying only on component or mocked tests.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-27 | Frontend coverage | Run frontend lint, type-check, unit tests, and coverage collection. | `docs/release/frontend_test_evidence.md`. | Output captures command, environment, and results. |
| NS-28 | Browser E2E | Run Playwright/browser E2E against live local stack or staging backend. | `docs/release/frontend_test_evidence.md`. | Browser evidence covers authenticated learner flow. |
| NS-29 | Critical UI flows | Verify login, dashboard, lesson generation, consent, and POPIA export. | `docs/release/frontend_test_evidence.md`. | Each critical flow has pass/fail evidence. |
| NS-30 | PWA/offline scope | Verify implementation or record explicit beta deferral. | `docs/release/known_issues.md` or beta scope document. | No ambiguous PWA/offline claim remains. |
| NS-31 | Parent dashboard scope | Verify implementation or record explicit beta deferral. | `docs/release/known_issues.md` or beta scope document. | No ambiguous parent dashboard claim remains. |

Recommended commands:

```bash
make frontend-verification-evidence-check
make frontend-e2e
make frontend-e2e-smoke
```

## Wave 6: Operations, Observability, Backup, Restore, And Rollback

Goal: give operators enough evidence and runbooks to detect, recover, and
communicate incidents during beta.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-32 | Operator runbook | Document start/stop, health checks, queue/cache checks, log locations, escalation, and common remediation steps. | `docs/release/operator_runbook.md`. | Operator can handle first-line beta support. |
| NS-33 | Uptime monitor | Configure monitor for `GET /api/v2/health/deep`. | `docs/release/monitoring_evidence.md`. | Monitor evidence includes URL, interval, alert target, and screenshot/export. |
| NS-34 | Alertmanager | Wire Alertmanager to the selected channel and fire a test alert. | `docs/release/alertmanager_evidence.md`. | Test alert is received and recorded. |
| NS-35 | Backup dry-run | Run backup job and capture timestamp/checksum. | Backup log and `docs/release/monitoring_evidence.md` or backup evidence file. | Backup artifact can be located and verified. |
| NS-36 | Restore drill | Restore into disposable/staging environment and run smoke checks. | Restore log plus smoke evidence. | Restore process is proven end to end. |
| NS-37 | Rollback drill | Execute rollback against staging/disposable environment and correct runbook gaps. | Rollback evidence and updated rollback runbook. | Rollback has tested commands and outcomes. |
| NS-38 | Change-control policy | Define who can approve beta changes, emergency changes, and rollback decisions. | `docs/release/change_control_policy.md`. | Policy has named owner/role fields. |
| NS-39 | Incident tabletop | Run incident scenario and capture decisions/action items. | `docs/release/incident_tabletop_evidence.md`. | Action register exists and blockers feed back into TODO. |

Recommended commands:

```bash
make observability-ops-check
make database-backup-dry-run
make database-restore-dry-run
make beta-monitoring-incident-trigger-check
```

## Wave 7: POPIA, Legal, Security, And Governance Approvals

Goal: separate repository checks from real external approvals and make every
missing approval visible.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-40 | POPIA sweep | Run POPIA sweep and resolve or document exceptions. | `docs/release/popia_sweep_evidence.md`. | Sweep has zero issues or tracked exceptions. |
| NS-41 | Legal review | Submit POPIA/privacy docs and capture reviewer decision. | Legal review record linked from sign-off manifest. | Legal reviewer decision exists. |
| NS-42 | Security review | Obtain pen-test decision, scoped assessment, or sign-off. | Security sign-off or finding report. | Security reviewer decision exists. |
| NS-43 | Sign manifest | Fill real names, dates, roles, and decisions after reviews complete. | `docs/release/sign_off_manifest.md`. | Manifest is signed by required owners. |
| NS-44, NS-62 | Release decision log | Record beta go/no-go participants, evidence reviewed, decision, and conditions. | `docs/release/release_decision_log.md`. | Decision log is signed and references current evidence. |

Recommended commands:

```bash
make popia-consent-gate-check
make privacy-legal-evidence-check
make release-approval-workflow-contract-check
```

## Wave 8: CAPS Content And Product Readiness

Goal: ensure the beta scope is honest about curriculum content, answer quality,
supported cohorts, and known limitations.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-45 | CAPS approved count | Generate or manually compile approved versus candidate item counts. | Item-bank report linked from beta scope. | Counts are current and auditable. |
| NS-46 | Educator review | Route AI-generated items through educator review and capture decisions. | Review/sign-off records. | Required item sample has reviewer decisions. |
| NS-47 | Launch threshold | Reach threshold or explicitly constrain beta scope. | Approved item evidence or beta-scope limitation document. | Beta scope matches real content readiness. |
| NS-48 | Answer-key validation | Implement independent validation or define external review workflow. | Validation plan or implementation evidence. | Answer-key risk has owner and process. |
| NS-49 | Beta scope | Define supported grades, subjects, languages, and exclusions. | Beta product scope document. | Scope is understandable to support, legal, and beta users. |
| NS-50 | Known issues | Create non-empty known issues and limitations file. | `docs/release/known_issues.md`. | Known limitations are not hidden. |
| NS-51, NS-61 | Acceptance criteria | Define beta metrics, thresholds, exit criteria, and no-go conditions. | `docs/release/beta_acceptance_criteria.md`. | Release owner can judge beta success or failure. |

Recommended commands:

```bash
make caps-ai-safety-evidence-check
make beta-acceptance-exit-criteria-check
make beta-known-issues-register-check
```

## Wave 9: Monetization And Communications Decisions

Goal: prevent silent product gaps around billing and user communications.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-52 | Billing mode decision | Decide free beta or paid beta before staging go/no-go. | Release bundle/product scope decision. | One billing mode is explicitly selected. |
| NS-53 | Paid beta path | If paid, implement provider checkout, webhooks, subscription lifecycle, and quota tests. | Billing integration evidence and tests. | Paid flow is tested before beta. |
| NS-54 | Free beta path | If free, disable billing and document deferred monetization. | Feature flag/config and release note. | Users cannot accidentally enter paid flow. |
| NS-55 | Notifications | Implement transactional notification provider or document deferral. | Communication evidence or deferred scope. | Password reset, consent renewal, and progress report risks are addressed. |
| NS-56 | Communication paths | Verify password reset, consent renewal, and progress report delivery path. | Tests or manual evidence. | Required communications work or are explicitly out of beta scope. |

Recommended commands:

```bash
make beta-release-communications-plan-check
make environment-security-check
```

## Wave 10: Staging, Beta Go/No-Go, And Release Closure

Goal: make the final beta decision only after runtime, external, and product
evidence exists.

| TODO IDs | Workstream | Implementation approach | Evidence output | Exit gate |
| --- | --- | --- | --- | --- |
| NS-57 | Staging deploy | Deploy the exact candidate to staging. | Staging deployment log. | Deployment artifact and commit SHA match release bundle. |
| NS-58 | Staging smoke | Run API, frontend, CORS, security-header, and core learner flow smokes. | Smoke output. | Staging smoke passes or no-go is recorded. |
| NS-59 | Telemetry and alerts | Verify dashboards, logs, traces, uptime, and alert routing in staging. | Dashboard/alert evidence. | Operators can detect staging failures. |
| NS-60 | Issue templates | Add bug, feature, incorrect content, and POPIA concern templates. | `.github/ISSUE_TEMPLATE/*.md`. | Beta feedback routes to actionable templates. |
| NS-63 | Beta outcome | After beta ends, write outcome report with metrics, incidents, feedback, and follow-ups. | `docs/release/beta_outcome_report.md`. | Report exists after beta completion. |
| NS-65 | Tag release | Tag release candidate or beta only after all required gates pass. | GitHub tag/release with evidence bundle. | Tag points to reviewed commit and current evidence bundle. |

Recommended commands:

```bash
make staging-release-gate-check
make staging-smoke-evidence-manifest-check
make beta-release-final-checklist-check
make final-release-verification-check
```

## Dependency Order

| Gate | Must be true before moving on |
| --- | --- |
| Local baseline | NS-03 through NS-05 and NS-13 have current evidence. |
| CI authority | NS-06 through NS-12 prove remote checks and branch protection. |
| Governance bundle | NS-14 through NS-23 produce readable release governance artifacts. |
| Runtime proof | NS-24 through NS-31 prove DB and frontend behavior. |
| Operational readiness | NS-32 through NS-39 prove monitoring, backup, restore, rollback, and incident handling. |
| Approval readiness | NS-40 through NS-51 collect POPIA/legal/security/product/content evidence. |
| Product decisions | NS-52 through NS-56 close billing and communication ambiguity. |
| Beta decision | NS-57 through NS-65 complete staging, templates, decision log, closure, and tagging. |

## External Work Register

These tasks need real people, systems, or post-beta events and should not be
closed by repository-only edits:

| TODO IDs | External dependency |
| --- | --- |
| NS-12 | Repository administrator configures and exports branch protection evidence. |
| NS-22, NS-43, NS-44, NS-62, NS-64, NS-65 | Release owner and named approvers sign final decisions, certificates, tags, and releases. |
| NS-33, NS-34 | Monitoring and alerting systems must be configured and tested. |
| NS-38, NS-39 | Change-control approval and incident tabletop require accountable participants. |
| NS-41, NS-42 | Legal and security reviewers must provide approval or findings. |
| NS-46, NS-51, NS-61 | Educator/product reviewers must approve content and beta success criteria. |
| NS-63 | Beta outcome report can only be completed after beta has run. |

## Working Cadence

- Daily during active remediation: update the active wave, evidence file, or
  blocker note.
- Twice weekly: run the relevant Make checks and update `TODO.md` statuses only
  when evidence exists.
- Before every PR: link the TODO IDs addressed and include exact validation
  commands.
- Before beta go/no-go: review this plan, `TODO.md`, `docs/current_state.md`,
  and the release bundle together.

## Plan Coverage

This plan intentionally covers all outstanding `NS-*` items from `TODO.md` as
of 2026-05-22:

`NS-03`, `NS-04`, `NS-05`, `NS-06`, `NS-07`, `NS-08`, `NS-09`, `NS-10`,
`NS-11`, `NS-12`, `NS-13`, `NS-14`, `NS-15`, `NS-16`, `NS-17`, `NS-18`,
`NS-19`, `NS-20`, `NS-21`, `NS-22`, `NS-23`, `NS-24`, `NS-25`, `NS-26`,
`NS-27`, `NS-28`, `NS-29`, `NS-30`, `NS-31`, `NS-32`, `NS-33`, `NS-34`,
`NS-35`, `NS-36`, `NS-37`, `NS-38`, `NS-39`, `NS-40`, `NS-41`, `NS-42`,
`NS-43`, `NS-44`, `NS-45`, `NS-46`, `NS-47`, `NS-48`, `NS-49`, `NS-50`,
`NS-51`, `NS-52`, `NS-53`, `NS-54`, `NS-55`, `NS-56`, `NS-57`, `NS-58`,
`NS-59`, `NS-60`, `NS-61`, `NS-62`, `NS-63`, `NS-64`, `NS-65`.

Run:

```bash
make todo-implementation-plan-check
```

The check verifies that every outstanding `NS-*` item from `TODO.md` appears in
this plan. It does not verify that the tasks are complete.
