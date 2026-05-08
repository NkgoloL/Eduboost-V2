# First PR-sized Batch: Repository Governance and Backlog Hygiene

## Objective
Make the repository easier to operate before touching high-risk auth/POPIA/AI code. This PR is intentionally low-runtime-risk and creates guardrails for later PRs.

## Included TODO items

| ID | Priority | Status | Task | Current evidence |
|---|---|---|---|---|
| TODO-026 | high | Partial | Add issue templates: bug, feature, security redirect, compliance concern, accessibility issue, curriculum issue, incorrect content, production incident. | .github/ISSUE_TEMPLATE/bug_report.yml; .github/ISSUE_TEMPLATE/feature_request.yml |
| TODO-025 | high | Partial | Add `CODEOWNERS` for backend, frontend, infrastructure, security, compliance, curriculum, and docs. | .github/CODEOWNERS |
| TODO-027 | high | Partial | Add PR template with checkboxes for tests, docs, migrations, POPIA impact, security impact, accessibility impact, analytics impact, deployment impact, and rollback plan. | .github/PULL_REQUEST_TEMPLATE.md |
| TODO-029 | high | Partial | Remove duplicate or stale root dependency files, or clearly mark them as compatibility aliases. | requirements.txt; requirements-dev.txt; requirements-docs.txt; requirements-ml.txt |
| TODO-032 | medium | Partial | Add `docs/adr/` and write ADRs for modular monolith, FastAPI V2, Next.js frontend, PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment. | docs/adr |
| TODO-028 | high | Human-decision | Audit dependency files and decide canonical dependency paths for runtime, dev, docs, and ML extras. | wsl_copilot.sh; requirements.txt; pytest.ini; Makefile; requirements-docs.txt; prometheus.yml; .agent.md; CONTRIBUTING.md |
| TODO-024 | high | Blocked | Protect `master`/`main`: require PR review, required checks, no force-push, no branch deletion, and signed commits if feasible. | .github/workflows/ci-cd.yml |
| TODO-033 | medium | Partial | Add markdown linting and docs link checking to CI. | .github/workflows/ci-cd.yml |

## Concrete patch plan

1. Expand `.github/CODEOWNERS` to cover backend, frontend, infrastructure, security, compliance, curriculum, docs, and tests.
2. Add missing issue templates: security redirect, compliance concern, accessibility issue, curriculum/content issue, incorrect content, and production incident.
3. Expand `.github/PULL_REQUEST_TEMPLATE.md` with migration, POPIA, security, accessibility, analytics, deployment, rollback, and evidence-bundle checkboxes.
4. Update `docs/repository_governance.md` to cover mirrors, branch policy, release authority, secret rotation authority, security patch process, and archive policy.
5. Normalize dependency-file intent: `requirements/base.txt`, `dev.txt`, `docs.txt`, `ml.txt` as canonical; root files as compatibility aliases unless deleted by owner decision.
6. Add missing `Makefile` targets: `e2e`, `security`, `release-check`, and `smoke`.
7. Add ADR stubs for PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment.
8. Add docs-link checking to CI or document it as a follow-up if dependency install is too heavy.

## Acceptance criteria

- Governance docs and templates exist in deterministic paths.
- Makefile help lists all required commands.
- Dependency hierarchy is unambiguous.
- PR template forces future security/privacy/accessibility/migration/deployment/rollback disclosure.
- No application runtime behavior changes.