# EduBoost V2 — Comprehensive True-State Remediation Roadmap

**Roadmap date:** 13 July 2026  
**Source assessment:** `EduBoost_V2_True_State_Technical_Report_2026-07-13.md`  
**Reviewed snapshot:** `Eduboost-V2-master(31)(4).zip`  
**Snapshot digest:** `a059d4134b8dc99e10db4fb98a19cba933fc3baacaeb7471a86c4a8c1101e9e2`  
**Declared application version:** `1.0.0-rc1`  
**Roadmap status:** Proposed for controlled execution  
**Current release posture:** **NO-GO for production; controlled internal/staging validation only**  
**Primary objective:** Resolve every material concern identified in the true-state audit without weakening existing release controls, expanding product scope, or creating further documentation and workflow sprawl.

---

## 1. Executive direction

EduBoost has reached the point where convergence matters more than feature expansion. The platform already contains substantial product capability, but whole-repository quality, security, contract integrity, operational reproducibility, and maintainability have not converged enough to support a production claim.

This roadmap therefore imposes five operating decisions:

1. **Freeze net-new product scope until Release Gate RG-2 is closed.** Only remediation, safety, compliance, reliability, and evidence work may proceed.
2. **Close PRD-11 Runtime Restore Execution-7 first.** Do not bury its failures inside a larger refactor and do not lower thresholds to obtain green status.
3. **Reduce authority surfaces.** Maintain one roadmap, one machine-readable remediation register, one canonical verifier per implementation bundle, and one evidence record per merged bundle.
4. **Separate release-critical remediation from long-horizon maturity work.** A concern may be real without blocking a tightly controlled pilot; every concern must still have an owner, deadline, acceptance criterion, and disposition.
5. **Treat children’s data and learning decisions as high-risk.** Security, authorization, privacy, educational quality, and operational recovery require independent review before public production.

The intended end state is not merely “tests pass.” It is:

> One current truth source, one supported toolchain, one canonical API contract, one authorization model, a small CI graph, maintainable service boundaries, proven data operations, defensible learner-state modelling, reproducible infrastructure, and immutable evidence from the exact release candidate.

---

## 2. Program outcomes

The remediation program is complete only when all of the following outcomes are true:

| Outcome | Required end state |
|---|---|
| Release assurance | Coverage, Ruff, mypy, Bandit, Python dependency audit, frontend dependency audit, and secret review are green on the exact release candidate. |
| Canonical truth | The production-readiness register, `README.md`, `docs/current_state.md`, route inventory, generated contracts, and release authority agree automatically. |
| Toolchain coherence | Python, Node, pnpm, Next.js, React, database, pgvector, and build tooling are intentionally pinned and reproduced in local, CI, staging, and release environments. |
| CI authority | A small, explicit workflow graph defines required pull-request, merge, scheduled, release, and operational-drill checks. |
| Maintainability | Oversized routers/services, broad exception handling, legacy compatibility layers, and architectural exceptions are materially reduced and governed by enforceable limits. |
| Data assurance | The complete schema has classification, retention, export, erasure, backup, isolation, migration, recovery, and ownership proof. |
| Security/privacy | One authorization engine is authoritative; live POPIA operations, processor governance, incident response, access review, and external security review are proven. |
| KG/educational validity | Mastery states are semantically explicit, graph versions are migratable, CAPS mappings are reviewed, scale is measured, and adaptive claims are validated. |
| Operational readiness | Staging is reproducibly deployed from IaC; SLOs, alerts, runbooks, load, cost, backup, restore, rollback, and incident drills have measured evidence. |
| Production authority | Production release, deployment, tag, controlled live traffic, and payments are authorized only from immutable evidence tied to the exact release commit. |

---

## 3. Non-negotiable execution rules

### 3.1 Scope and release controls

- Production release, production deployment, release tagging, public beta, billing launch, and live payment processing remain disabled until their explicit gates close.
- Grade 4 Mathematics remains the only launch-active educational scope unless a separate reviewed scope-expansion decision is approved.
- No release gate may be made green by lowering coverage, excluding additional code, broadening ignores, adding blanket suppressions, changing audit severity, or moving failing commands out of the required path.
- A temporary exception must identify the exact finding, risk owner, compensating control, expiry date, and removal verifier. Critical or high-severity security findings cannot be self-waived for public production.
- Evidence from another branch, commit, environment, or dependency set is contextual only. It cannot close a release gate.

### 3.2 Evidence discipline

Every implementation bundle must include:

1. An approved scope entry in the remediation register.
2. The implementation and tests.
3. One canonical verifier that checks behavior and required artifact consistency.
4. Raw machine-readable command outputs.
5. Environment and toolchain identity.
6. Source commit and artifact digests.
7. Post-merge reproduction from clean `master`.
8. A concise evidence record that derives status rather than manually restating it.

### 3.3 Documentation minimization

Do not create a separate narrative plan, report, approval memo, handoff note, closeout note, and duplicate evidence index for every small task. The target control set is:

- `docs/roadmap/execution/true_state_remediation_roadmap_2026-07-13.md`
- `docs/roadmap/production_readiness/true_state_remediation_register.json`
- one implementation/evidence record per bundled slice;
- one verifier per bundle;
- generated current-state pages.

Historical detail may remain archived, but it must not remain in the default engineering navigation or act as current authority.

### 3.4 Work-in-progress limits

For a single-developer operating model:

- Maximum one active code-heavy remediation bundle.
- Maximum one concurrent evidence/documentation closure bundle.
- No new architecture migration while an earlier release blocker is unverified.
- Security, privacy, data migration, and release-authorization reviews require an independent reviewer or formally recorded external assessment before public production.

---

## 4. Priorities, status model, and effort model

### 4.1 Priority definitions

| Priority | Meaning |
|---|---|
| P0 | Current release blocker or material risk of incorrect release authority. |
| P1 | Must be resolved before public production; may not block internal staging while controlled. |
| P2 | Required hardening or maintainability work with an explicit pre-GA or post-pilot deadline. |
| P3 | Optimization or longer-term maturity item; must remain visible and measured. |

### 4.2 Status model

`identified → authorised → in_progress → implementation_complete → evidence_pending → verified → closed`

A task may also be `blocked`, `accepted_risk` with expiry, or `superseded` with a referenced replacement. “Done” or “green” without raw evidence is not a valid state.

### 4.3 Planning estimate

These are planning ranges, not delivery promises. Rebaseline after Wave 1 captures the real failure counts.

| Delivery model | Estimated elapsed effort |
|---|---:|
| Sole developer with occasional independent review | Approximately 9–14 months |
| Three-person engineering team plus part-time security/privacy/education review | Approximately 4–7 months |
| Five-person cross-functional team | Approximately 3–5 months |

The release-critical subset through RG-2 is materially smaller than the whole roadmap, but public production should not proceed until RG-4.

---

## 5. Roadmap waves and release gates

| Wave | Workstream | Primary purpose | Priority | Indicative effort | Depends on | Exit gate |
|---|---|---|---|---:|---|---|
| W0 | TSR-0 Authority and reproducible baseline | Establish one remediation authority and exact baseline | P0 | 3–5 engineering days | None | RG-0 |
| W1 | TSR-1 Execution-7 release-gate recovery | Make all current coverage/static/security gates genuinely green | P0 | 15–30 days | TSR-0 | RG-1 |
| W2 | TSR-2 Canonical truth and contract integrity | Eliminate stale status, scope ambiguity, and OpenAPI drift | P0/P1 | 7–12 days | TSR-0; may overlap late TSR-1 | RG-2A |
| W2 | TSR-3 Toolchain, frontend, and dependency convergence | Establish coherent, reproducible dependency surfaces | P0/P1 | 12–22 days | TSR-0 | RG-2B |
| W3 | TSR-4 CI and governance consolidation | Replace workflow sprawl with one explicit CI authority graph | P1 | 15–25 days | TSR-1, TSR-3 | RG-2 |
| W3 | TSR-5 Test-system maintainability | Separate product signal from governance and remove flaky/ambiguous execution | P1 | 12–22 days | TSR-1, TSR-4 design | RG-2 |
| W4 | TSR-6 Architecture and code-risk reduction | Reduce oversized modules, exceptions, duplication, and legacy debt | P1/P2 | 35–60 days | RG-1 | RG-3A |
| W4 | TSR-7 Data, migration, and transaction hardening | Prove schema lifecycle and live-data behavior | P1 | 18–30 days | TSR-3, staging DB | RG-3B |
| W5 | TSR-8 Security, authorization, and POPIA live proof | Establish defensible access and privacy operations | P0/P1 | 25–45 days | TSR-7; portions parallel TSR-6 | RG-3 |
| W5 | TSR-9 Runtime KG and educational-quality maturity | Validate graph semantics, mapping quality, versioning, and adaptive claims | P1/P2 | 25–50 days | TSR-7, reviewed data | RG-3C |
| W6 | TSR-10 API simplification and compatibility | Establish one canonical API and a measured deprecation path | P2 | 10–18 days | TSR-2, TSR-4 | RG-3D |
| W6 | TSR-11 Operations, SRE, DR, performance, and cost | Prove deployability, recovery, monitoring, and sustainable operation | P0/P1 | 25–45 days | TSR-3, TSR-7, TSR-8 | RG-4 |
| W7 | TSR-12 Controlled production authorization | Run release-candidate, pilot, and final go/no-go controls | P0 | 12–25 days | All pre-production gates | RG-5 |
| W8 | TSR-13 Post-release stabilization and resilience | Remove residual risk and reduce key-person dependence | P1/P2 | 20–35 days | RG-5 | RG-6 |

### 5.1 Gate definitions

| Gate | Meaning | Minimum decision |
|---|---|---|
| RG-0 | Baseline authority established | Remediation work may begin. Production remains NO-GO. |
| RG-1 | Execution-7 independently green | Release-blocking code assurance restored; no production authority yet. |
| RG-2A | Canonical truth and contracts agree | Stakeholders can trust current state and API artifacts. |
| RG-2B | Toolchain and dependency surfaces coherent | Clean installs are reproducible and frontend green evidence is credible. |
| RG-2 | CI/test authority consolidated | A release candidate may be formed for hardening; production remains NO-GO. |
| RG-3 | Architecture, data, authorization, privacy, and educational safeguards acceptable | Limited controlled pilot may be proposed, subject to operations gate. |
| RG-4 | Operations and recovery proven | Time-boxed controlled production pilot may be authorized. |
| RG-5 | Pilot and release-candidate evidence accepted | Production deployment and release tag may be authorized. |
| RG-6 | Stabilization complete | Normal product roadmap may resume under standard change controls. |

### 5.2 Critical dependency path

```text
TSR-0
  └── TSR-1 ── RG-1
        ├── TSR-2 ── RG-2A
        ├── TSR-3 ── RG-2B
        └── TSR-4 + TSR-5 ── RG-2
                         ├── TSR-6
                         ├── TSR-7 ── TSR-8
                         ├── TSR-9
                         └── TSR-10
                                  └── TSR-11 ── RG-4
                                               └── TSR-12 ── RG-5
                                                            └── TSR-13
```

---

# 6. Detailed workstreams

## TSR-0 — Authority, scope freeze, and reproducible baseline

### Objective

Create one reliable starting point and prevent the remediation program from reproducing the same authority fragmentation identified by the audit.

### Preconditions

- Clean canonical branch and exact base commit are available.
- Full pinned Python and frontend dependency environments can be installed.
- Production release and live-payment flags remain false.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-0.1 | P0 | Create `true_state_remediation_register.json` containing every finding in the audit | Machine-readable register | Every report concern has a unique ID, severity, owner role, dependency, target gate, verifier, status, and evidence pointer. |
| TSR-0.2 | P0 | Record exact canonical source state | Baseline record | Branch, commit, worktree status, submodules, source archive digest, lockfile digests, migration head, and OpenAPI digest are recorded. |
| TSR-0.3 | P0 | Capture canonical environment identity | Environment manifest | Python, pip, OS, Node, pnpm, Docker, Postgres/pgvector, Redis, browser, and relevant native-library versions are machine-readable. |
| TSR-0.4 | P0 | Reproduce clean dependency installs without using prior caches | Raw install evidence | Backend and frontend install from locked inputs; undeclared/manual dependencies are not required. |
| TSR-0.5 | P0 | Capture the complete starting failure profile | Baseline evidence bundle | Coverage, collection, Ruff, mypy, Bandit, pip-audit, pnpm audit, secrets, frontend quality, product/runtime, route, schema, and migration checks have raw outputs. |
| TSR-0.6 | P0 | Enforce temporary feature freeze | Register control and CI check | Pull requests outside remediation/safety/reliability require an explicit exception; no release flag changes are allowed. |
| TSR-0.7 | P1 | Define owners and independence controls | Responsibility matrix | Engineering, release, evidence, security, privacy, curriculum, and operations responsibilities are named; self-review conflicts are disclosed. |
| TSR-0.8 | P1 | Add roadmap/register schema validation | Canonical verifier | Missing finding IDs, duplicate authorities, impossible status transitions, stale evidence pointers, or unauthorised release flags fail closed. |

### RG-0 exit criteria

- The register covers 100% of the concern traceability matrix in Section 10.
- A clean environment can install and execute baseline commands.
- The current red/green state is captured without interpretation loss.
- No production authorization field has changed.

### Required evidence

- `baseline_manifest.json`
- `environment_manifest.json`
- `baseline_command_summary.json`
- raw command outputs and hashes
- register schema-verifier output

---

## TSR-1 — PRD-11 Execution-7 coverage, static, and security convergence

### Objective

Close the current release blocker exactly as defined: all seven release-gating command families green, independently captured, and reproduced from merged `master`.

### Scope guardrail

This wave permits only changes required to make the current gates truthful and green. Large architectural rewrites belong to TSR-6.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-1.1 | P0 | Repair MCP startup-test isolation | Test fixture and tests | Stub tests explicitly prevent real backend import, assert `FASTMCP_BACKEND == "test-stub"`, and pass whether or not the real MCP package is installed. |
| TSR-1.2 | P0 | Preserve real-backend startup coverage | Separate test path | With the stub flag unset and the real dependency installed, the real backend path is exercised and verified independently. |
| TSR-1.3 | P0 | Stabilize test collection in the canonical environment | Collection manifest | Zero unexpected collection errors; required dependencies are declared in the correct profile; skips and xfails are explicit. |
| TSR-1.4 | P0 | Complete bounded, sharded coverage execution | Coverage summary and shard outputs | All shards terminate, no unresolved timeout leaves remain, combined line coverage meets or exceeds 70%, and missing-line data is published. |
| TSR-1.5 | P0 | Add risk-based tests rather than superficial line padding | Focused tests | New coverage primarily targets authorization, consent, payments-disabled paths, learner state, data export/erasure, migration, and failure handling. |
| TSR-1.6 | P0 | Close Ruff findings in `app` and `tests` | Clean Ruff output | `python3 -m ruff check app tests` exits zero; no blanket ignores are introduced. |
| TSR-1.7 | P0 | Close mypy findings in `app` | Clean mypy output | `python3 -m mypy app` exits zero under the committed configuration; CI no longer uses `continue-on-error` for the release job. |
| TSR-1.8 | P0 | Close Bandit findings | Bandit report and dispositions | No unreviewed high findings; medium findings are fixed or narrowly accepted with owner and expiry; no blanket `# nosec`. |
| TSR-1.9 | P0 | Close Python dependency findings | Audit outputs and lock updates | Base and development requirements have no unaccepted known vulnerabilities; exceptions are time-boxed and approved. |
| TSR-1.10 | P0 | Close frontend production dependency findings | `pnpm audit` output | Production dependency audit is green under the approved policy after dependency alignment; high/critical issues are zero or independently accepted. |
| TSR-1.11 | P0 | Review the secret baseline | Reviewed baseline and disposition register | Every detected candidate is human-reviewed; real secrets are rotated and removed from history where necessary; baseline regeneration alone is insufficient. |
| TSR-1.12 | P0 | Capture independent Execution-7 evidence | Execution-7 evidence record | Every gate is run independently from the exact merged source; command, exit code, duration, environment, artifact hash, warnings, skips, and failures are retained. |
| TSR-1.13 | P0 | Re-run product/runtime regression gates | Regression evidence | Previously green critical product, runtime stack, frontend, schema, generated-contract, and database-lineage gates remain green. |
| TSR-1.14 | P1 | Publish a debt delta | Before/after report | Ruff, mypy, Bandit, vulnerabilities, secret candidates, coverage gaps, timeouts, and test collection deltas are quantified. |

### Canonical command families

```bash
python -m compileall -q app tests scripts alembic
PYTHONPATH=. python -m pytest -c pytest.ini tests/unit/test_etl_mcp_server_startup.py -q
make coverage-baseline-stabilisation
python3 -m ruff check app tests
python3 -m mypy app
python3 -m bandit -r app scripts -q
pip-audit -r requirements/base.txt -r requirements/dev.txt
cd app/frontend && pnpm audit --prod
# Scan and then perform interactive/human audit of the committed baseline.
detect-secrets scan --baseline .secrets.baseline app scripts .github
detect-secrets audit .secrets.baseline
```

The committed Execution-7 contract remains authoritative if its commands differ. This roadmap must not silently replace or weaken it.

### RG-1 exit criteria

- `coverage_gate_green = true`
- `advisory_static_gate_green = true`
- `dependency_audit_gate_green = true`
- `secret_baseline_gate_green = true`
- `evidence_recorded = true`
- No prior green runtime/product gate regressed.
- Production release/deployment/tag/public-beta/payment flags remain false.

---

## TSR-2 — Canonical truth, product scope, documentation, and generated-contract integrity

### Objective

Make repository state understandable and mechanically consistent so operators, developers, clients, and reviewers cannot act on stale PRD-0-era information or stale API contracts.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-2.1 | P0 | Repair production-register summary derivation | Register schema and generator | Top-level status, current truth, active item, closed predecessors, and release flags are derived from one canonical state object and cannot disagree. |
| TSR-2.2 | P0 | Generate current-state documentation | Generator for `README.md` status and `docs/current_state.md` | Both pages identify PRD-11 Execution-7/its successor correctly, show the operational hold, and include generation source/time. |
| TSR-2.3 | P0 | Correct product-scope statements | Product-scope authority | Grade 4 Mathematics is marked launch-active; Grade R–7 and other subjects are clearly planned, review-only, or inactive. |
| TSR-2.4 | P0 | Clarify controlled-beta semantics | Current-state wording and status schema | Governance authorization, operational safety, activation hold, cohort limits, and kill-switch state are distinct fields. |
| TSR-2.5 | P0 | Establish one canonical OpenAPI artifact | Generation policy | `docs/openapi.json` or a newly designated single location is authoritative; stale root artifacts are removed or atomically regenerated. |
| TSR-2.6 | P0 | Generate JSON/YAML formats from one in-memory schema | Atomic generator | JSON and YAML contain the same paths, operations, schemas, metadata, and hash-equivalent normalized form. |
| TSR-2.7 | P1 | Add route/OpenAPI/client consistency verification | Contract verifier | Router registry, canonical prefix, OpenAPI paths, frontend client inventory, and SDK inputs agree; the 22-path drift cannot recur. |
| TSR-2.8 | P1 | Reorganize documentation navigation | Current-doc index and archive index | Default navigation exposes current state, architecture, setup, domains, operations, security/privacy, current roadmap, and archive entry only. |
| TSR-2.9 | P1 | Quarantine historical evidence from ordinary search/navigation | Immutable archive policy | Historical records remain available and hashed but are marked non-authoritative and excluded from normal current-state navigation. |
| TSR-2.10 | P1 | Add freshness and contradiction checks | Documentation verifier | A current-state page that disagrees with the register or exceeds the defined freshness threshold fails CI. |
| TSR-2.11 | P2 | Standardize project/version metadata | Version authority | Package version, release-candidate status, Python support, active API version, and product scope derive from one source. |

### RG-2A exit criteria

- README, current-state page, register, route inventory, and OpenAPI all agree.
- No duplicate generated artifact can drift silently.
- Historical records are clearly archived and non-authoritative.
- Stakeholders can distinguish controlled-beta authorization from operational activation.

---

## TSR-3 — Toolchain, frontend, package management, and dependency-profile convergence

### Objective

Make a clean install reproducible and reduce compatibility, supply-chain, image-size, and audit risk.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-3.1 | P0 | Decide and document the supported frontend compatibility matrix | ADR and pinned manifest | Next.js, React, React DOM, `eslint-config-next`, bundle analyzer, TypeScript, Node, and pnpm use an intentionally supported combination. |
| TSR-3.2 | P0 | Align frontend packages and regenerate lockfiles | Updated manifest/lock | Clean frozen install succeeds without incompatible peer assumptions; type-check, lint, unit, E2E, build, and production audit pass. |
| TSR-3.3 | P1 | Decide root-package architecture | Workspace ADR | Either a formal pnpm workspace is committed or root E2E tooling is isolated with explicit lockfile ownership. |
| TSR-3.4 | P1 | Enforce one Node/pnpm policy | Toolchain file and Corepack config | Local, CI, Docker, and release jobs use the same supported Node and pnpm versions. |
| TSR-3.5 | P0 | Resolve Python support inconsistency | Python runtime policy | Pin production/development to 3.12.3 or define a tested support matrix; `pyproject.toml`, docs, CI, images, and deployment agree. |
| TSR-3.6 | P1 | Split Python dependencies by deployable profile | Requirements/lock structure | API runtime, worker, ETL/content, ML research, docs, and dev/test profiles are separate and independently auditable. |
| TSR-3.7 | P1 | Remove or justify Celery/Flower | Dependency and architecture decision | Unused packages and stale Celery TODOs are removed, or an active worker architecture and tests are documented. |
| TSR-3.8 | P1 | Keep research/ML dependencies out of API images | Lean image build | Production API image excludes GPU/transformer research stacks unless required by measured runtime behavior. |
| TSR-3.9 | P1 | Standardize Postgres/pgvector and Redis versions | Runtime matrix | Compose, CI, staging, migration tests, and production IaC use one supported version line or an explicit compatibility matrix. |
| TSR-3.10 | P1 | Produce SBOMs for release images | CycloneDX/SPDX artifacts | Backend and frontend release artifacts have reproducible SBOMs linked to source and image digests. |
| TSR-3.11 | P1 | Add dependency-update policy | Renovation policy | Update cadence, compatibility tests, vulnerability SLAs, lockfile ownership, and emergency-patch process are defined. |
| TSR-3.12 | P2 | Measure image/install reductions | Before/after metrics | API image size, install duration, package count, and vulnerability surface are recorded and materially reduced. |

### RG-2B exit criteria

- Fresh backend/frontend installs are reproducible with no manual dependency additions.
- Frontend framework/tooling versions are coherent and freshly green.
- Production images install only required runtime profiles.
- Toolchain identity is common across CI, staging, and release.

---

## TSR-4 — CI authority and governance consolidation

### Objective

Replace 86 overlapping workflow files and inconsistent strictness with a small canonical workflow graph that engineers and branch protection can understand.

### Target workflow graph

1. `pr-core.yml` — compile, fast product unit tests, Ruff, mypy, architecture, route/OpenAPI checks.
2. `product-runtime.yml` — integration, disposable Postgres/pgvector/Redis, migrations, critical journeys.
3. `frontend-e2e.yml` — frozen install, type-check, lint, unit, build, Playwright/accessibility.
4. `security-supply-chain.yml` — Bandit, dependency audits, secret scan, SBOM, container scan; scheduled and required for release.
5. `release-evidence.yml` — manually dispatched, exact-commit, immutable release-candidate evidence.
6. `operations-drills.yml` — backup/restore, rollback, incident, resilience, and performance drills.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-4.1 | P1 | Inventory all 86 workflows | Workflow inventory | Each workflow has purpose, trigger, branches, commands, tool versions, required/advisory status, replacement, and retirement decision. |
| TSR-4.2 | P1 | Define required-check authority | CI authority document and JSON map | Every branch-protection check maps to one canonical job and command; duplicate names are prohibited. |
| TSR-4.3 | P1 | Implement the six-workflow target graph | Canonical workflows | Required PR and release signals are complete; redundant workflows are disabled and moved outside `.github/workflows`. |
| TSR-4.4 | P0 | Remove release-critical `continue-on-error` | Strict required jobs | mypy, security, dependency, secret, migration, and generated-contract gates fail closed where designated. |
| TSR-4.5 | P1 | Standardize tool/action/service versions | Shared environment/action policy | setup-python, Node, Postgres/pgvector, Redis, pnpm, and action major versions are consistent. |
| TSR-4.6 | P1 | Standardize branch triggers | Trigger policy | Canonical branch naming is used; historical `main`, `develop`, and obsolete release-branch triggers are removed or justified. |
| TSR-4.7 | P1 | Centralize commands in repository scripts/Make targets | Command authority | Local and CI execution invoke the same command implementations, not divergent inline shell logic. |
| TSR-4.8 | P1 | Separate ordinary product checks from governance/evidence checks | Job taxonomy | Product failures are visible in fast feedback; governance tests remain strict but separately reported. |
| TSR-4.9 | P1 | Add concurrency, cache, and artifact-retention policy | Workflow controls | Stale runs cancel safely; caches are keyed to lockfiles; raw evidence retention and sensitivity are defined. |
| TSR-4.10 | P1 | Reconcile branch protection | Hosted configuration evidence | Required check list exactly matches canonical jobs; direct pushes and stale approvals are governed. |
| TSR-4.11 | P1 | Archive superseded workflows | Archive index | Historical workflow source remains retrievable but cannot execute accidentally. |
| TSR-4.12 | P1 | Prove post-merge authority from exact source | Hosted CI evidence | A clean merge commit runs all required checks successfully; evidence includes run IDs, commit SHA, and artifact hashes. |
| TSR-4.13 | P2 | Track CI health and cost | CI metrics | Median duration, failure categories, flake rate, queue time, and monthly compute use are monitored. |

### RG-2 exit criteria

- Branch protection references only canonical required jobs.
- No release-critical command is advisory or duplicated with conflicting configuration.
- Local commands and hosted CI commands are equivalent.
- Superseded workflows cannot run.

---

## TSR-5 — Test-system taxonomy, isolation, and maintainability

### Objective

Preserve the strength of the large test suite while making failures actionable, execution bounded, and product behavior more visible than governance text checks.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-5.1 | P1 | Enforce test taxonomy | Marker and path policy | Tests are classified as product-unit, product-integration, runtime-stack, architecture-static, governance-contract, or release-evidence. |
| TSR-5.2 | P1 | Make fast PR test selection deterministic | Fast-suite manifest | The same test set runs locally and in PR CI; no hidden environment-based inclusion. |
| TSR-5.3 | P1 | Separate governance tests from product unit counts | CI reporting | Product pass/failure counts and governance pass/failure counts are independently visible. |
| TSR-5.4 | P1 | Eliminate environment-sensitive backend selection | Isolation fixtures | Optional integrations are forced explicitly in unit tests; real backends have dedicated integration tests. |
| TSR-5.5 | P1 | Establish flake policy | Flake register and detector | Retries cannot conceal first-attempt failures; quarantines have owners, expiry, and reproduction evidence. |
| TSR-5.6 | P1 | Standardize factories and fixtures | Shared test support | Database, auth, learner, guardian, consent, curriculum, and provider fixtures are reusable and deterministic. |
| TSR-5.7 | P1 | Add risk-based coverage thresholds | Coverage policy | Global threshold is supplemented by stricter targets for authorization, privacy, payments, migration, and learner-state calculations. |
| TSR-5.8 | P2 | Introduce mutation testing on high-risk modules | Mutation reports | Critical authorization/consent/mastery branches demonstrate that tests fail when behavior is altered. |
| TSR-5.9 | P1 | Bound slow and hanging tests | Timeout/budget policy | Every shard has a budget; terminal timeout leaves are classified and cannot be ignored. |
| TSR-5.10 | P1 | Validate tests from a disposable dependency-complete environment | Reproduction workflow | Full collection and selected suites pass from an empty cache/container, eliminating audit-host ambiguity. |
| TSR-5.11 | P2 | Reduce duplicated governance test logic | Shared schema/verifier library | Repeated text-presence tests are replaced by generated schemas and a small number of semantic verifiers. |
| TSR-5.12 | P2 | Publish test-suite health metrics | Dashboard/report | Collection time, run duration, flake rate, skip/xfail age, coverage by domain, and failure recurrence are tracked. |

### Exit criteria

- Zero unexplained collection errors in canonical environments.
- Test categories and owners are clear.
- Real and stub integration paths cannot be selected accidentally.
- Fast PR feedback remains bounded while full release evidence remains comprehensive.

---

## TSR-6 — Architecture, service boundaries, code quality, and legacy retirement

### Objective

Reduce the maintenance and security risk created by oversized modules, direct repository access, broad exceptions, duplicated implementations, and compatibility layers.

### Sequencing rule

Refactor one bounded domain at a time with characterization tests and unchanged public behavior. Do not run a repository-wide “cleanup” rewrite.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-6.1 | P1 | Create an architectural-debt register | Debt register | Every import-linter exception, oversized module, legacy alias, duplicate implementation, broad exception hotspot, TODO, `pass`, and coverage exclusion has an owner and retirement target. |
| TSR-6.2 | P1 | Split `content_factory.py` by capability | Thin route modules | Generation, review, staging, promotion, and production-read paths delegate to typed services; route modules no longer import repositories directly. |
| TSR-6.3 | P1 | Consolidate ETL implementations | One versioned ETL interface | `etl_pipeline.py`, `_v2.py`, and `_v3_additions.py` are merged, wrapped, or retired under one supported interface with migration tests. |
| TSR-6.4 | P1 | Decompose POPIA orchestration | Typed command/query services | Export, erasure, consent, retention, and audit flows have explicit boundaries and transaction ownership. |
| TSR-6.5 | P1 | Decompose curriculum graph and content-review orchestration | Smaller domain services | Graph load, mapping, review, versioning, and publication logic are independently testable. |
| TSR-6.6 | P1 | Decompose batch/content generation | Typed jobs and command objects | Provider calls, budget reservations, persistence, review, and retries use explicit state transitions. |
| TSR-6.7 | P1 | Remove direct router-to-repository exceptions | Import-linter enforcement | The exception list trends to zero; any remaining exception has a documented expiry. |
| TSR-6.8 | P1 | Replace broad exception hotspots | Typed exception taxonomy | Integration boundaries classify retryable, client, provider, persistence, policy, and internal failures; unexpected exceptions propagate to observability. |
| TSR-6.9 | P1 | Prevent degraded failures from returning success | Error-contract tests | Health, provider, job, and persistence failures return the intended status and metric, not silent 200 responses. |
| TSR-6.10 | P1 | Consolidate authorization modules | One object-authorization service | `app/core/authorization.py`, `app/security/authorization.py`, and `app/security/object_authorization.py` have one authoritative implementation. |
| TSR-6.11 | P1 | Resolve fail-closed placeholders | Implemented or removed helpers | Guardian/teacher relationship helpers no longer remain ambiguous placeholders; tests cover every policy path. |
| TSR-6.12 | P1 | Inventory and quarantine `app/legacy` | Legacy boundary | Production imports from legacy code are zero or explicitly permitted by a temporary compatibility adapter. |
| TSR-6.13 | P2 | Remove obsolete aliases and compatibility shims | Retirement changes | Usage inventory proves no supported caller depends on the removed alias; deprecation is tested where external. |
| TSR-6.14 | P1 | Set gradual complexity budgets | Lint/architecture policy | New modules/functions cannot exceed approved limits; existing hotspots have ratcheting ceilings rather than blanket exemptions. |
| TSR-6.15 | P1 | Resolve `pass`, TODO/HACK, and `pragma: no cover` debt | Disposition register | Each item is implemented, removed, or narrowly justified with an expiry and test rationale. |
| TSR-6.16 | P2 | Establish domain ownership and public interfaces | Architecture index | Each domain exposes supported services/events/contracts and prohibits cross-domain internal imports. |
| TSR-6.17 | P2 | Re-measure complexity after each domain slice | Before/after metrics | Module size, function length, exception count, type errors, import exceptions, and coverage improve without behavior regression. |

### RG-3A exit criteria

Before public production:

- No direct repository access remains in public API routers without an approved exception.
- One authorization engine is authoritative.
- The highest-risk oversized modules are decomposed.
- Broad exceptions at critical boundaries are typed and observable.
- Legacy production dependencies are removed or isolated.

Longer-tail decomposition may continue after a controlled pilot under ratcheting limits.

---

## TSR-7 — Data inventory, schema lifecycle, migrations, transactions, and recovery integrity

### Objective

Prove that the 103-table schema can be operated, migrated, exported, erased, backed up, restored, and supported safely.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-7.1 | P1 | Build a table/field data inventory | Data inventory | Every table has business purpose, owner, personal-data class, lawful basis, retention, export, erasure, encryption, backup, and isolation treatment. |
| TSR-7.2 | P1 | Map data lineage across derived stores | Lineage map | Primary DB, Redis, object storage, analytics, audit, KG events, generated content, logs, and backups are linked. |
| TSR-7.3 | P1 | Prove empty-database bootstrap | Migration evidence | Alembic upgrades a clean supported database to the single head and schema/model drift is zero. |
| TSR-7.4 | P1 | Prove upgrade from the last supported release state | Upgrade fixture and evidence | Realistic prior schema/data upgrades without loss; duration and locks are measured. |
| TSR-7.5 | P1 | Prove production-like migration performance | Migration benchmark | Large representative datasets migrate inside the approved maintenance/zero-downtime strategy. |
| TSR-7.6 | P1 | Define rollback versus forward-fix policy | Migration runbook | Each migration class identifies rollback feasibility, backup requirement, forward-fix path, and stop condition. |
| TSR-7.7 | P1 | Add schema/model/generated-contract drift checks | CI verifier | ORM metadata, Alembic head, live schema, and generated schema artifacts agree. |
| TSR-7.8 | P1 | Replace implicit request-wide transaction ownership | Transaction policy and refactor | Read queries do not commit; commands explicitly own commit/rollback; audit writes and domain writes have documented atomicity. |
| TSR-7.9 | P1 | Test tenant/object isolation at persistence boundaries | Isolation suite | Cross-learner, cross-guardian, and unauthorized object access fail at service/query boundaries. |
| TSR-7.10 | P1 | Validate audit immutability controls | DB-level tests | Mutation prevention is effective under the deployed database role model and survives migrations/restores. |
| TSR-7.11 | P1 | Identify obsolete/redundant tables | Schema disposition | Unused tables are retired through safe migrations or assigned active owners. |
| TSR-7.12 | P1 | Align backup handling with retention and erasure | Backup policy | Retention, encryption, access, restore, and legally defensible erasure treatment are explicit. |
| TSR-7.13 | P2 | Measure query/index health | Query report | Critical learner, parent, KG, consent, lesson, and reporting queries have plans and latency budgets on representative data. |

### RG-3B exit criteria

- One migration head and zero schema drift are proven from empty and prior-release databases.
- Every live-data table has a privacy and operational treatment.
- Explicit transaction ownership exists for high-risk commands.
- Backup and restore behavior is compatible with retention and erasure obligations.

---

## TSR-8 — Security, object authorization, POPIA live-data operations, and external assurance

### Objective

Move from thoughtful security/privacy design to release-grade proof over the exact deployed system and live-data topology.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-8.1 | P0 | Make one authorization engine authoritative | Policy engine and route migration | Every protected route/service calls the same object-policy layer; duplicates are removed or adapters only. |
| TSR-8.2 | P0 | Complete learner/guardian/teacher/admin policy matrix | Machine-readable matrix and tests | Every role/object/action combination has allow/deny expectations, including negative and revoked-consent paths. |
| TSR-8.3 | P1 | Validate authentication lifecycle | Security test evidence | Password, MFA where applicable, refresh rotation, revocation, session expiry, account recovery, rate limits, and device/logout paths are tested. |
| TSR-8.4 | P1 | Prove secret management and rotation | Key Vault/secret evidence | Production starts only with approved secret sources; rotation and rollback are rehearsed; no secret appears in logs/artifacts. |
| TSR-8.5 | P1 | Perform live-schema export completeness test | Export evidence | A subject export includes all legally required primary and derived data with provenance and readable format. |
| TSR-8.6 | P1 | Perform full erasure cascade test | Erasure evidence | Primary, derived, cache, object, analytics, search, KG, and generated-data paths are erased or legally retained with explicit reason. |
| TSR-8.7 | P1 | Define backup-erasure treatment | Legal/technical policy | Backup retention, restore-time re-erasure, encryption-key retirement, and audit evidence are defined and tested. |
| TSR-8.8 | P1 | Enforce retention automatically | Retention jobs and tests | Expired data is removed/anonymized on schedule; dry-run and production-safe modes are auditable. |
| TSR-8.9 | P1 | Strengthen guardian verification and minor-data handling | Verification flow and tests | Guardian authority, consent version, withdrawal, age/learner linkage, and disputed-access paths are enforced. |
| TSR-8.10 | P1 | Complete processor/subprocessor governance | Register and agreements | Every external provider has purpose, data categories, location, contract/DPA status, retention, and exit process. |
| TSR-8.11 | P1 | Run threat modelling for high-risk surfaces | Threat models | Auth, parent portal, tutor/LLM, content generation, content promotion, billing/webhooks, exports, erasure, KG, and admin operations are covered. |
| TSR-8.12 | P1 | Prove incident response and notification | Tabletop evidence | Security/privacy incident classification, containment, evidence preservation, notification decision, and communication are rehearsed. |
| TSR-8.13 | P1 | Establish access review and separation of duties | Access review record | Production admin, database, cloud, evidence, and release permissions are least-privilege and periodically reviewed. |
| TSR-8.14 | P0 | Commission independent security review | External report and remediation | Penetration testing/code review covers public attack surface and high-risk workflows; critical/high findings are closed before public production. |
| TSR-8.15 | P1 | Add supply-chain and artifact integrity controls | Signed artifacts/provenance | Release images are vulnerability-scanned, signed, linked to SBOMs, and traceable to source. |
| TSR-8.16 | P1 | Validate LLM/content safety boundaries | Safety evidence | Prompt injection, data leakage, unsafe content, hallucinated curriculum claims, provider failure, and cost-abuse controls are tested. |
| TSR-8.17 | P2 | Establish vulnerability-management SLA | Operating policy | Severity-based remediation targets, emergency patching, exception expiry, and disclosure channels are operational. |

### RG-3 security/privacy exit criteria

- One authorization model is enforced and independently tested.
- Export, erasure, retention, backup treatment, and guardian verification work against the actual release schema and stores.
- No unresolved critical/high external-security finding remains.
- Production access and incident procedures are operational, not only documented.

---

## TSR-9 — Runtime KG, mastery semantics, CAPS mapping quality, and educational validation

### Objective

Turn the credible KG foundation into a defensible learner-state and intervention system without overstating scientific maturity.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-9.1 | P1 | Define learner-state semantics | API/domain model | `authoritative`, `inferred`, `tentative`, `stale`, and `superseded` mastery/evidence states are explicit. |
| TSR-9.2 | P1 | Version the mastery algorithm | Model/version registry | Every learner-state result records algorithm version, graph version, evidence window, confidence, and provenance. |
| TSR-9.3 | P1 | Define graph-revision migration policy | Migration service and tests | Learner states can be mapped, recomputed, invalidated, or preserved across curriculum graph revisions with audit history. |
| TSR-9.4 | P1 | Validate CAPS node/edge/source mapping quality | Reviewed sample and metrics | Coverage, correctness, reviewer agreement, unresolved ambiguity, and source provenance meet approved thresholds. |
| TSR-9.5 | P1 | Introduce double review for high-impact mappings | Review workflow | Prerequisite edges and assessment/grade-critical nodes require independent curriculum review. |
| TSR-9.6 | P1 | Calibrate mastery against diagnostics/IRT and teacher judgment | Validation study | Correlation, bias, calibration, false-gap, and false-mastery rates are measured on consented data. |
| TSR-9.7 | P1 | Replace or bound the simple correctness×confidence model | Model decision | The current formula is validated for limited use, improved, or explicitly treated as tentative; unsupported precision claims are prohibited. |
| TSR-9.8 | P1 | Validate longitudinal learning impact | Controlled study | Mastery movement, retention, intervention effectiveness, and subgroup fairness are measured over time. |
| TSR-9.9 | P1 | Load-test graph traversal and projection refresh | Performance evidence | Representative graph/data volumes meet latency, throughput, event-growth, and cost budgets. |
| TSR-9.10 | P1 | Add graph update rollback and shadow mode | Operational controls | New graph/model versions can run in shadow, compare outputs, and roll back without corrupting learner state. |
| TSR-9.11 | P1 | Expose uncertainty safely to product surfaces | UX/API contract | Tutor, parent, and learner experiences distinguish estimates from verified outcomes and avoid deterministic labeling. |
| TSR-9.12 | P1 | Validate bias and fairness | Fairness report | Performance and intervention recommendations are reviewed across available learner groups without using inappropriate sensitive inference. |
| TSR-9.13 | P2 | Establish educational-claim governance | Claim register | Marketing/product claims identify evidence level and cannot describe the KG as mature adaptive intelligence without validation. |
| TSR-9.14 | P2 | Create ongoing mapping/model quality monitoring | Metrics and alerts | Drift, orphan nodes, version mismatches, low-confidence states, and intervention anomalies are detectable. |

### RG-3C exit criteria

- Learner-state semantics and version provenance are explicit.
- Graph revisions cannot silently invalidate learner history.
- CAPS mappings and mastery behavior have human and quantitative validation.
- Scale and rollback behavior are proven.
- Product claims match the evidence level.

---

## TSR-10 — API prefix rationalization, compatibility, and client migration

### Objective

Reduce duplicated attack, testing, observability, and documentation surfaces caused by mounting nearly all routes under both `/api/v2` and `/v2`.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-10.1 | P2 | Designate `/api/v2` as canonical | API version policy | Documentation, OpenAPI, frontend, SDKs, monitoring, and examples use one prefix. |
| TSR-10.2 | P2 | Inventory `/v2` consumers | Telemetry/client inventory | Every known internal/external consumer is identified; unknown usage is measured through logs/metrics. |
| TSR-10.3 | P2 | Add compatibility/deprecation middleware | Deprecation behavior | Alias responses include approved deprecation metadata without leaking data or changing authorization. |
| TSR-10.4 | P2 | Preserve policy equivalence during transition | Equivalence tests | Auth, consent, rate limits, error envelopes, schemas, and observability are identical across prefixes while both exist. |
| TSR-10.5 | P2 | Migrate frontend and internal callers | Client updates | No first-party code depends on `/v2`. |
| TSR-10.6 | P2 | Publish sunset criteria | Sunset plan | Removal depends on telemetry showing zero approved consumers for the defined window and successful client migration. |
| TSR-10.7 | P2 | Remove alias and regenerate contracts | API cleanup | `/v2` is removed only after criteria close; route count and OpenAPI surface reduce predictably. |
| TSR-10.8 | P2 | Establish future API-versioning rules | API governance | Version introduction, compatibility, deprecation, sunset, and schema-change policies are executable. |

### RG-3D exit criteria

- One canonical prefix is used by all first-party clients.
- Alias usage is measured and safely deprecated.
- Duplicate route surface is removed or has a time-bound external compatibility exception.

---

## TSR-11 — Infrastructure parity, observability, SRE, disaster recovery, performance, and cost

### Objective

Prove that the exact release candidate can be deployed, observed, recovered, rolled back, and supported under representative conditions.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-11.1 | P0 | Establish IaC-to-staging parity | Deployment manifest | Staging is created from the same Kubernetes/Bicep/container definitions intended for production, with environment-specific values only. |
| TSR-11.2 | P1 | Eliminate configuration drift | Drift detector | Running environment, IaC, image digests, migrations, secrets, and feature flags are compared automatically. |
| TSR-11.3 | P1 | Define service-level objectives | SLO document and metrics | Availability, latency, error, queue, tutor/provider, data freshness, and recovery objectives have owners and measurement sources. |
| TSR-11.4 | P1 | Validate dashboards and alerts under fault | Alert evidence | Database, Redis, provider, queue, migration, auth abuse, budget, storage, and learner-journey failures trigger actionable alerts. |
| TSR-11.5 | P1 | Validate logs/traces for privacy and diagnosis | Observability review | Correlation is possible without exposing learner/guardian secrets or excessive personal data. |
| TSR-11.6 | P0 | Run full backup/restore drill | DR evidence | Restore produces a consistent application, validates critical records, and records actual RTO/RPO. |
| TSR-11.7 | P0 | Run deployment rollback/forward-fix drill | Rollback evidence | Application, config, and migration rollback/forward-fix decisions are rehearsed with explicit stop conditions. |
| TSR-11.8 | P1 | Run regional/provider/Redis/database failure drills | Resilience evidence | Degradation is safe, user-visible behavior is appropriate, data remains consistent, and recovery is observable. |
| TSR-11.9 | P0 | Run representative load and endurance tests | Performance report | Learner, parent, tutor, diagnostic, lesson, KG, content, and admin workloads meet latency/error/resource budgets. |
| TSR-11.10 | P1 | Measure event/table/log growth | Capacity model | Storage, KG events, audit events, tutor messages, generated content, backups, and log retention have forecasts and alerts. |
| TSR-11.11 | P1 | Establish cost budgets and kill switches | Cost model | Per-learner, LLM, database, storage, egress, and observability costs are bounded; provider and generation budgets fail safely. |
| TSR-11.12 | P1 | Complete operator runbooks | Runbook index | Release, rollback, auth incident, privacy request, provider outage, DB saturation, queue backlog, bad content, and payment-disable procedures are executable. |
| TSR-11.13 | P0 | Establish on-call and escalation ownership | Support roster | A production incident does not depend on one unavailable person; escalation and external contacts are current. |
| TSR-11.14 | P1 | Run incident tabletop and live game day | Drill evidence | Detection, triage, communications, recovery, evidence preservation, and post-incident actions are demonstrated. |
| TSR-11.15 | P1 | Prove release artifact provenance | Release manifest | Source commit, image digest, SBOM, migrations, OpenAPI, frontend assets, configuration, and evidence are cryptographically linked. |
| TSR-11.16 | P1 | Verify payment controls remain disabled | Runtime control | Stripe/live billing cannot activate before separate commercial and release authorization; tests fail closed. |

### RG-4 exit criteria

- Staging and candidate infrastructure are reproducible from source-controlled definitions.
- Measured RTO/RPO, rollback, load, endurance, capacity, and cost are acceptable.
- Alerts and runbooks have been exercised, not merely reviewed.
- At least two accountable people or an external support arrangement can respond to critical incidents.

---

## TSR-12 — Release-candidate formation, controlled pilot, and production authorization

### Objective

Make the final decision from immutable evidence tied to the exact release candidate, then validate a limited live cohort before broader production.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-12.1 | P0 | Freeze the release candidate | Candidate manifest | Exact source commit, lockfiles, images, migrations, OpenAPI, frontend build, SBOMs, and configuration digests are fixed. |
| TSR-12.2 | P0 | Run all required gates from the candidate | Final command evidence | No evidence is inherited from an earlier commit; all required jobs pass from clean environments. |
| TSR-12.3 | P0 | Obtain independent security/privacy/curriculum/operations sign-off | Review decisions | Conflicts are disclosed; unresolved blockers are explicit; no self-approval substitutes for mandatory external review. |
| TSR-12.4 | P0 | Authorize a time-boxed controlled production pilot | Pilot decision | Cohort, consent, data, support, monitoring, kill switch, rollback, payment-disabled state, and stop thresholds are approved. |
| TSR-12.5 | P0 | Run pilot with continuous monitoring | Pilot evidence | Real journey success, errors, incidents, performance, support, educational quality, privacy requests, and costs are captured. |
| TSR-12.6 | P0 | Apply stop/rollback criteria when triggered | Incident/rollback record | The pilot cannot continue through a critical authorization, privacy, safety, data-loss, or uncontrolled-cost event. |
| TSR-12.7 | P0 | Review pilot outcomes and residual risk | Go/no-go packet | Findings are classified; required remediation is closed or production remains blocked. |
| TSR-12.8 | P0 | Authorize production deployment and tag separately | Release decisions | Release tag, deployment, traffic expansion, and payment activation are distinct decisions; payment remains separately gated. |
| TSR-12.9 | P0 | Verify post-deployment state | Post-deploy evidence | Smoke, migrations, monitoring, rollback readiness, API contracts, and critical journeys are green on deployed artifacts. |
| TSR-12.10 | P1 | Publish an accurate release statement | Current-state update | Claims match active scope and evidence; known limitations and support channels are visible. |

### RG-5 exit criteria

- All release-critical findings in the remediation register are closed.
- Pilot stop thresholds were not breached or were resolved and revalidated.
- Exact release artifacts are signed, tagged, reproducible, and deployed through the approved path.
- Production release, deployment, tag, public traffic, and payments have explicit, separate authority states.

---

## TSR-13 — Post-release stabilization, ownership resilience, and return to normal roadmap

### Objective

Prevent early production from recreating hidden operational debt and reduce the single-developer/key-person risk highlighted by the audit.

### Work items

| ID | Pri. | Work item | Deliverable | Acceptance criteria |
|---|---:|---|---|---|
| TSR-13.1 | P1 | Run a defined stabilization window | Stabilization dashboard | Release changes are limited; incidents, performance, support, privacy, cost, and educational-quality metrics are reviewed daily/weekly. |
| TSR-13.2 | P1 | Close pilot/launch defects by severity | Defect register | Critical/high defects meet response targets and have regression tests. |
| TSR-13.3 | P1 | Rotate operational responsibilities | Handover evidence | A second operator/reviewer can deploy, roll back, restore, investigate, and handle privacy requests. |
| TSR-13.4 | P1 | Test evidence and access custody | Custody drill | Release evidence, keys, accounts, backups, and runbooks remain available if the primary developer is unavailable. |
| TSR-13.5 | P2 | Continue architecture ratchets | Debt metrics | Module size, exception, legacy, workflow, dependency, and coverage trends continue improving. |
| TSR-13.6 | P2 | Reassess KG and learning outcomes | Post-launch education review | Production evidence informs mastery/model changes without silently altering historical learner states. |
| TSR-13.7 | P2 | Reassess cost and capacity | Updated model | Forecasts use actual utilization and trigger scale/cost actions. |
| TSR-13.8 | P1 | Conduct formal post-release review | Review report | Release controls, incidents, near misses, false alarms, support burden, and residual risks produce actionable changes. |
| TSR-13.9 | P1 | Lift feature freeze only after RG-6 | Authority update | Normal roadmap resumes only when stabilization criteria and residual P0/P1 tasks are closed or explicitly deferred. |

---

# 7. Recommended implementation bundles

To reduce governance and PR overhead, execute the roadmap in a maximum of eight principal bundles. Small fixes may be commits inside a bundle; they should not become new roadmap programs.

| Bundle | Included work | Required evidence boundary |
|---|---|---|
| B1 — Release Gate Recovery | TSR-0 + TSR-1 | Baseline plus green Execution-7 evidence from merged `master`. |
| B2 — Truth and Toolchain | TSR-2 + TSR-3 | Generated truth/contracts and reproducible clean installs/frontend verification. |
| B3 — CI and Test Authority | TSR-4 + TSR-5 | Canonical workflow graph, branch-protection evidence, deterministic suite taxonomy. |
| B4 — Architecture and Data | TSR-6 first tranche + TSR-7 | High-risk module boundaries, single authorization direction, migration/data inventory proof. |
| B5 — Security, Privacy, and Education | TSR-8 + TSR-9 | Independent security/privacy proof and KG/content validity evidence. |
| B6 — API and Operations | TSR-10 + TSR-11 | API migration telemetry plus staging/DR/load/SLO evidence. |
| B7 — Candidate and Pilot | TSR-12 | Exact-candidate gates, pilot evidence, go/no-go decisions. |
| B8 — Stabilization | TSR-13 | Post-release metrics, resilience, and feature-freeze release. |

A bundle may be split only when it becomes too large to review safely. Splitting must not create duplicate authority or evidence records for the same claim.

---

# 8. Release decision matrix

| Condition | Internal development | Shared staging | Controlled live pilot | Public production | Live payments |
|---|---:|---:|---:|---:|---:|
| Before RG-1 | Allowed | Allowed with caution | No | No | No |
| RG-1 closed, RG-2 open | Allowed | Allowed | No | No | No |
| RG-2 closed, RG-3 open | Allowed | Allowed | No | No | No |
| RG-3 closed, RG-4 open | Allowed | Allowed | No, unless an explicit non-production research cohort authority exists | No | No |
| RG-4 closed | Allowed | Allowed | May be authorized with kill switch | No | No |
| RG-5 closed | Allowed | Allowed | Allowed within release decision | May be authorized | Separately authorized only after commercial/payment gate |

---

# 9. Program-level verification and evidence contract

## 9.1 Minimum evidence fields

Every command artifact must include:

- finding/task IDs addressed;
- source commit and clean-worktree status;
- environment manifest digest;
- command and working directory;
- start/end time and duration;
- exit code;
- stdout/stderr or structured report;
- test count, pass/fail/error/skip/xfail counts;
- warnings, retries, timeouts, collection errors;
- artifact digest and retention classification;
- operator and reviewer;
- whether the result is pre-merge, post-merge, staging, pilot, or production.

## 9.2 Global definition of done

A work item is closed only when:

- implementation and negative-path tests exist;
- affected documentation/contracts are generated or updated;
- security/privacy/data/education/operations impact is reviewed where applicable;
- the canonical verifier passes;
- evidence is captured from the intended environment and exact source;
- no higher-priority gate regressed;
- the remediation register derives `closed` from evidence rather than manual prose;
- temporary exceptions have not increased without approval.

## 9.3 Global stop conditions

Stop the affected wave and return to the last known green state when any of these occur:

- a critical product journey regresses;
- unauthorized cross-learner/guardian data access is observed;
- export/erasure loses data or removes legally retained evidence incorrectly;
- a migration causes unbounded lock time, corruption, or irrecoverable drift;
- secrets or learner data appear in logs, build artifacts, or public evidence;
- coverage is made green through new exclusions or threshold reduction;
- a critical/high security finding is discovered;
- cost controls fail open;
- release authority fields change before their gate;
- evidence cannot be tied to the exact source/environment claimed.

---

# 10. Complete concern-to-roadmap traceability

This matrix demonstrates coverage of every material concern raised in the true-state report.

| Audit concern | Severity | Roadmap treatment | Closure proof |
|---|---:|---|---|
| Execution-7 coverage gate false | Critical | TSR-1.3–1.5, 1.12 | Complete sharded coverage ≥70%, zero unresolved timeout leaves, exact-commit evidence. |
| Ruff gate not green | Critical release | TSR-1.6 | Zero-exit Ruff report without blanket ignores. |
| mypy gate not green / CI advisory | Critical release | TSR-1.7, TSR-4.4 | Clean mypy output and required CI job. |
| Bandit gate not green | Critical release | TSR-1.8 | No unreviewed high findings; reviewed dispositions. |
| Python dependency audit not green | Critical release | TSR-1.9, TSR-3.6, TSR-8.15 | Green audits, split profiles, SBOM/provenance. |
| Frontend dependency audit not green | Critical release | TSR-1.10, TSR-3.1–3.4 | Coherent compatibility set and green production audit. |
| Secret baseline not reviewed | Critical release | TSR-1.11, TSR-8.4 | Human-reviewed baseline, rotation/removal evidence. |
| MCP tests depend on installed backend | Medium-high | TSR-1.1–1.2, TSR-5.4 | Forced stub tests plus separate real-backend proof. |
| Audit environment lacked dependencies | Medium | TSR-0.3–0.5, TSR-3, TSR-5.10 | Reproducible dependency-complete clean environment. |
| ZIP lacked `.git`; provenance unverified | High evidence limitation | TSR-0.2, TSR-4.12, TSR-11.15, TSR-12.1–12.2 | Hosted exact-commit evidence and signed artifact provenance. |
| README/current-state stale at PRD-0 | High | TSR-2.1–2.2, 2.10 | Generated pages agree with register and fail on mismatch. |
| Register top-level status inconsistent | Medium | TSR-2.1 | Schema derives summary from canonical current truth. |
| Controlled beta authorized but operationally held | High clarity | TSR-2.4, TSR-12.4 | Separate authorization/safety/activation fields and pilot decision. |
| Product scope says Grade 4 vs Grade R–7 | Medium | TSR-2.3, TSR-9.13 | One launch-scope authority and evidence-level claims. |
| `docs/openapi.json` differs from root artifacts by 22 routes | High | TSR-2.5–2.7 | One atomic generator and zero route/schema drift. |
| Root `openapi.yaml` is JSON content | High contract integrity | TSR-2.5–2.6 | Correct format generation and normalized equivalence check. |
| More than 3,000 docs obscure current guidance | Medium-high | TSR-2.8–2.10 | Minimal current navigation and immutable archive index. |
| Governance documents outnumber current product truth | Medium-high | TSR-0.8, TSR-2, TSR-4.8, TSR-5.11 | One register/generator, separate governance jobs, reduced duplication. |
| 86 workflow files | High | TSR-4.1–4.3, 4.11 | Six canonical workflows; superseded files cannot execute. |
| Overlapping/inconsistent CI commands | High | TSR-4.2, 4.5–4.7 | Single command authority and environment policy. |
| Branch triggers include master/main/develop/historical branches | Medium-high | TSR-4.6 | Canonical trigger policy verified. |
| Different setup-python and service versions | Medium | TSR-3.9, TSR-4.5 | One supported runtime matrix. |
| `continue-on-error` on mypy | High | TSR-1.7, TSR-4.4 | Required fail-closed job. |
| Frontend Next/React/tooling versions incoherent | High | TSR-3.1–3.2 | Supported matrix, frozen install, full fresh quality proof. |
| Root and frontend package/lock surfaces ambiguous | Medium-high | TSR-3.3–3.4 | Formal workspace or explicit isolation and lock ownership. |
| Python metadata says ≥3.11 while CI targets 3.12.3 | Medium | TSR-3.5, TSR-2.11 | One runtime policy across metadata, CI, images, docs. |
| Celery/Flower present despite “no Celery” architecture | Medium-high | TSR-3.7 | Remove or formally activate/document/test. |
| ML/research dependencies bloat API runtime | Medium-high | TSR-3.6, 3.8, 3.12 | Split profiles and lean image metrics. |
| Oversized content factory router | High | TSR-6.2 | Thin routers and no direct repositories. |
| Multiple ETL pipelines | High | TSR-6.3 | One supported versioned interface. |
| Oversized curriculum/content/POPIA/batch services | High | TSR-6.4–6.6, 6.14 | Decomposed services and ratcheting complexity limits. |
| Direct router-to-repository import exceptions | High | TSR-6.1, 6.7 | Exception list reaches zero or time-bound approved minimum. |
| About 122 broad exception handlers | High maintainability | TSR-6.8–6.9 | Typed failures, observable unexpected exceptions, correct statuses. |
| Silent degraded-but-200 response risk | High operational | TSR-6.9, TSR-11.4 | Error-contract tests and alert fault injection. |
| Overlapping authorization modules | Medium-high | TSR-6.10, TSR-8.1–8.2 | One authoritative policy engine and complete matrix. |
| Guardian/teacher helpers return false placeholders | Medium-high | TSR-6.11 | Implemented/removed behavior with allow/deny tests. |
| `app/legacy` and compatibility aliases | Medium-high | TSR-6.12–6.13 | No production dependency or explicit temporary adapter. |
| `pass`, TODO/HACK, and no-cover debt | Medium | TSR-6.15 | Complete disposition and ratcheting policy. |
| 103-table schema operational burden | High | TSR-7.1–7.2, 7.11–7.13 | Table inventory, ownership, lineage, retirement, query evidence. |
| Migration branches/history complexity | High | TSR-7.3–7.7 | Empty/prior/realistic upgrades, one head, zero drift, measured duration. |
| Rollback behavior unproven | High | TSR-7.6, TSR-11.7 | Tested rollback/forward-fix runbook. |
| Request-wide implicit commit policy | Medium-high | TSR-7.8 | Explicit command/query transaction ownership. |
| Tenant/object isolation obligations | High | TSR-7.9, TSR-8.2 | Negative persistence and API authorization tests. |
| Audit immutability relies on intended DB rules | High | TSR-7.10 | Tests under deployed DB roles and after restore. |
| Runtime KG mastery formula comparatively simple | Medium-high | TSR-9.2, 9.6–9.8 | Versioned/validated model or explicitly tentative use. |
| KG mapping quality determines correctness | High education | TSR-9.4–9.5 | Reviewed CAPS mapping metrics and independent review. |
| KG traversal/event scale unproven | High operations | TSR-9.9, 9.14, TSR-11.10 | Load, growth, drift, and alert evidence. |
| Learner states across graph revisions unproven | High data/education | TSR-9.3, 9.10 | Migration/shadow/rollback tests. |
| Authoritative vs inferred mastery unclear | High product semantics | TSR-9.1, 9.11 | Explicit API/UX states and uncertainty. |
| Longitudinal educational effectiveness unproven | High product claim | TSR-9.6–9.8, 9.12–9.13 | Calibration, longitudinal, fairness, and claim evidence. |
| API mounted under `/api/v2` and `/v2` | Medium | TSR-10.1–10.7 | Canonical prefix, telemetry, migration, safe sunset. |
| Double API surface increases tests/attack/metrics | Medium | TSR-10.4, 10.7 | Equivalence during transition and final route reduction. |
| POPIA implementation lacks live-data proof | High | TSR-7.1–7.2, TSR-8.5–8.10 | Live export/erasure/retention/backup/processor evidence. |
| Guardian verification/minor data handling needs proof | High | TSR-8.9 | Verified relationship/consent/dispute flows. |
| Incident notification and access review unproven | High | TSR-8.12–8.13 | Tabletop and access-review evidence. |
| External security review absent for release candidate | Critical pre-production | TSR-8.14, TSR-12.3 | Independent review with critical/high closure. |
| Infrastructure may not match deployed environment | High | TSR-11.1–11.2 | IaC-created staging and drift detector. |
| DR exists mostly as scripts/workflows | High | TSR-11.6–11.8 | Measured restore, rollback, and failure drills. |
| SLOs/alerts/on-call need live validation | High | TSR-11.3–11.5, 11.12–11.14 | Fault-tested alerts, runbooks, roster, game day. |
| Performance/scale/cost evidence incomplete | High | TSR-11.9–11.11 | Representative load/endurance/capacity/cost evidence. |
| Single-developer key-person risk | High operational | TSR-0.7, TSR-11.13, TSR-13.3–13.4 | Second operator/external arrangement and custody drill. |
| Production release/tag/deployment unauthorised | Critical control | TSR-12.1–12.9 | Separate exact-candidate decisions after RG-4. |
| Live payments unauthorised | Critical control | TSR-11.16, TSR-12.8 | Runtime-disabled state and separate commercial authorization. |

---

# 11. Program risk register

| Risk | Probability | Impact | Mitigation | Stop/escalation trigger |
|---|---:|---:|---|---|
| Release-gate repair expands into uncontrolled refactor | High | High | Strict TSR-1 scope; move deep changes to TSR-6 | Critical-flow regression or bundle becomes unreviewable |
| Green status achieved through suppressions | Medium | Critical | Suppression delta verifier and human security review | Threshold/ignore/exclusion increases without approval |
| Workflow consolidation drops a required control | Medium | Critical | Command-to-workflow traceability and parallel shadow runs | Any prior required command has no canonical replacement |
| Dependency alignment causes frontend regressions | Medium | High | Compatibility ADR, frozen clean install, full E2E/build | Peer/runtime mismatch or journey regression |
| Architecture changes alter behavior | High | High | Characterization tests and one-domain slices | Contract or product-flow drift |
| Migration testing is unrepresentative | Medium | Critical | Sanitized production-scale fixtures and timing | Lock/data-loss threshold exceeded |
| Erasure removes required audit/legal records | Medium | Critical | Data classification and legal review | Irreversible deletion uncertainty |
| KG revision corrupts learner state | Medium | Critical | Shadow, versioned state, rollback, recomputation | Divergence beyond approved threshold |
| External provider outage or price spike | High | High | Fallback, budgets, kill switches, cached/degraded paths | Unbounded cost or unsafe content path |
| Single reviewer approves own high-risk work | High | High | Independent security/privacy/curriculum/ops review | Public-production decision lacks independent sign-off |
| Documentation archive hides needed operating knowledge | Low | High | Curated current index and searchable immutable archive | Runbook/evidence cannot be found during drill |
| Pilot scope expands informally | Medium | Critical | Cohort limits, feature flags, traffic/identity monitoring | Unapproved learner or payment traffic observed |
| Evidence contains personal or secret data | Medium | Critical | Redaction, restricted storage, automated scan | Sensitive content in public artifact |
| CI duration becomes prohibitive | Medium | Medium | Taxonomy, sharding, cache, scheduled deep checks | Required PR feedback exceeds approved budget repeatedly |
| Feature freeze lasts too long and creates pressure to bypass gates | High | High | Publish gate progress and prioritize critical path | Unauthorized feature/release work begins |

---

# 12. Success metrics

The program should publish a compact dashboard rather than more narrative status documents.

| Area | Metric | Target at RG-5 |
|---|---|---:|
| Release gates | Required green gates | 100% |
| Coverage | Combined line coverage | ≥70%, with higher domain-specific critical targets |
| Test health | Unexpected collection errors | 0 |
| Test health | Unowned flakes/quarantines | 0 |
| Static quality | Ruff/mypy required-job failures | 0 |
| Security | Unresolved critical/high release findings | 0 |
| Supply chain | Unaccepted high/critical runtime vulnerabilities | 0 |
| Secrets | Unreviewed secret candidates | 0 |
| CI | Active canonical workflows | ≤6 principal workflows |
| CI | Required-check command ambiguity | 0 |
| Contracts | OpenAPI/route/client drift | 0 |
| Documentation | Current-state/register contradictions | 0 |
| Architecture | Direct router-to-repository exceptions | 0 or explicitly time-bound minimum |
| Architecture | Broad exception count in critical modules | Materially reduced; no silent-success hotspots |
| Data | Classified live tables | 100% |
| Migrations | Empty/prior/representative upgrade success | 100% |
| Privacy | Export/erasure store coverage | 100% of classified stores |
| Authorization | Policy matrix negative-path coverage | 100% of protected actions |
| KG | Learner states with model/graph/evidence version | 100% |
| Operations | Measured restore and rollback drills | Passing |
| Operations | SLO-backed critical journeys | 100% |
| Resilience | Critical operations with second trained responder | 100% |
| Release | Artifacts linked to exact source/SBOM/signature | 100% |

---

# 13. Immediate next execution order

The first implementation bundle should perform only the following, in order:

1. Create the machine-readable remediation register and baseline manifest.
2. Capture fresh failure counts from the canonical dependency-complete environment.
3. Fix MCP startup-test isolation.
4. Run and stabilize bounded coverage to expose the true missing-line profile.
5. Close Ruff and mypy by defect category, not file order.
6. Close Bandit and secret findings with human disposition.
7. Align frontend dependencies and close Python/frontend dependency audits.
8. Re-run all seven Execution-7 gate families independently.
9. Re-run product/runtime/front-end/schema/generated-contract regression gates.
10. Merge, re-run from clean `master`, record immutable evidence, and close RG-1.

Do **not** begin CI consolidation, ETL rewrites, API-prefix removal, KG model replacement, or large documentation moves before RG-1 unless a change is strictly required to close an Execution-7 blocker.

---

# 14. Final completion statement

This roadmap is complete when EduBoost can demonstrate—not merely claim—that the exact production release is internally consistent, securely built, privacy-operable, educationally defensible, reproducibly deployed, recoverable, observable, and supportable.

The program should be judged by convergence:

- fewer authority files;
- fewer workflows;
- fewer duplicate contracts;
- fewer compatibility layers;
- fewer broad failure paths;
- smaller and clearer modules;
- one current state;
- one supported release candidate;
- stronger independent evidence.

Until RG-5 is closed, the correct production decision remains **NO-GO**.
