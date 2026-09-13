---
title: "EduBoost V2 - Independent Technical Audit"
status: active
owner: engineering
reviewers: [engineering, architecture, security]
audience: internal
source_of_truth: false
last_reviewed: 2026-09-10
review_interval_days: 90
---

# EduBoost V2 — Independent Technical Audit
**Codebase, CI/CD, Security & Compliance-Path Review**

**Source:** NkgoloL/Eduboost-V2 (master, GitHub archive snapshot)  
**Audit date:** 10 September 2026  
**Prepared for:** EduBoost SA Engineering Leadership  
**Method:** Static analysis, dependency auditing, and configuration verification performed directly against the extracted repository archive in an isolated analysis sandbox — independent of, and without reference to, any previously generated audit artifact.

---

## 1. Executive Summary

This report presents an independently executed technical audit of the EduBoost V2 codebase, performed by direct static analysis, dependency scanning, and configuration verification against the repository archive supplied for review (GitHub source: NkgoloL/Eduboost-V2, master branch, no .git history included). No finding in this report was taken on the authority of any prior audit document; every claim below was re-derived from the code, configuration, and committed artifacts themselves, using AST parsing, live linting/security tooling, and direct queries against public vulnerability databases.

The codebase is large and structurally sound at its core. The ORM layer (103 tables, 470 application files) contains zero duplicate model or table declarations. The Alembic migration graph resolves to a single, unambiguous root and head across its 47 active revisions. The FastAPI route surface (240 distinct route declarations, deliberately double-mounted under two URL prefixes) matches its own committed route-inventory contract exactly. Production runtime dependencies (121 packages in `requirements/base.txt`) and production frontend dependencies (311 packages) both carry zero known vulnerabilities as of this audit date.

Set against that, the audit surfaced four findings that merit direct engineering-leadership attention, summarised here and detailed in Section 4:

- **The automated PR test gate executes 70 of the repository's 6,661 test functions (≈1.1%) on every pull request.** The remaining ~99% — including the bulk of `tests/unit` and `tests/integration` — is not wired into any active GitHub Actions workflow. "CI green" is therefore a narrow, specific signal, not a general regression guarantee.
- **Type checking is fully disabled (`mypy ignore_errors = True`) for 95 of roughly 470 application modules** — and the disabled set is concentrated almost exactly on the highest-risk surface: every authentication, consent/POPIA, billing/Stripe, JWT-keyring, and repository-layer module in the codebase.
- **The container image that actually serves ML inference (`docker/requirements.inference.txt`) pins dependencies with 38 unique known CVEs across 7 packages**, most concentrated in `transformers` (26 CVEs) and `starlette` (7 CVEs, the framework fronting the inference HTTP server). Neither this file nor `requirements/ml.txt` is included in the CI pip-audit job's scope, so this exposure is not currently visible to any automated gate.
- **The repository carries three simultaneously-committed `coverage.json` snapshots dated within five days of one another**, reporting 60.0%, 73.9%, and 34.3% coverage respectively over different file/statement counts. No CI workflow currently runs the coverage-gated Makefile target, so none of the three numbers is reproducibly authoritative.

Three findings from earlier remediation cycles referenced in project history were specifically re-tested and found resolved: the dual-repository / name-colliding ORM class issue, the dual-Alembic-head issue, and the SQL-injection exposure in the ETL metadata-update path (10 of 11 flagged sites are now soundly parameterized; the eleventh is downgraded in this report from a live vulnerability to a defense-in-depth gap — see Finding 4.3). This is a genuine and verifiable sign of forward progress and is called out explicitly in Section 5.

**Overall assessment:** the platform's core data and API layers are in good order. The principal residual risk is not in the application logic itself but in the assurance pipeline around it — CI gates and static-typing coverage that do not yet extend to the areas (auth, consent, billing, inference) where a regression would be most costly.

---

## 2. Scope & Methodology

### 2.1 What was reviewed
The uploaded archive `Eduboost-V2-master.zip` (21 MB compressed, ~201 MB extracted, 7,860 files) was extracted and analysed in full. The archive is a GitHub source export, not a git checkout: no `.git` directory, commit history, or blame information was present, which bounds several of the checks below (noted inline where relevant).

Tooling used, run directly against the extracted source in this session:
- **Custom AST-based parsers** (Python's `ast` module) for ORM model/table collision detection and Alembic revision-graph resolution — chosen over regex/grep specifically because naive text matching produced false positives during this audit's own first pass (documented in Finding 4.2).
- **Bandit 1.9.4** — run both under the repository's own CI invocation and under a series of targeted re-runs with nosec suppression disabled, to independently verify each suppressed finding rather than accept the suppression at face value.
- **pip-audit** — run directly against `requirements/base.txt`, `requirements/dev.txt`, `requirements/ml.txt`, `requirements/docs.txt`, and `docker/requirements.inference.txt` against the live PyPI/OSV advisory database.
- **pnpm 9.14.4** (matching the CI-pinned version) — `pnpm audit --prod` against `app/frontend/pnpm-lock.yaml`.
- **Ruff 0.x** and the repository's own `mypy.ini` — configuration reviewed directly; ruff executed against the repository's own `pyproject.toml` rule selection.
- **Direct parsing of committed artifacts:** `docs/route_inventory.md`, `coverage.json` / `coverage_latest.json` / `coverage_expansion.json`, `.secrets.baseline`, `.bandit`, `.gitleaks.toml`, and all six active GitHub Actions workflow files.

### 2.2 What was not performed, and why
In the interest of an accurate, non-overstated report, the following were out of scope for this pass:
- **Full dependency installation and live application boot / pytest execution.** `requirements/base.txt` alone pins 121 packages (with transitive ML dependencies in adjacent files running to several GB); a full, reliable install inside this sandbox was not pursued given the time budget. All findings on test-suite composition and CI-gate scope were instead derived by direct inspection of the workflow YAML and Makefile — i.e., what actually runs, not what a full run would report.
- **Runtime/dynamic testing** (penetration testing, load testing, live database behaviour). This is a static and configuration-level audit.
- **Exhaustive manual review of all 1,949 documentation files or all 879 baselined secrets-scan candidates.** Both were sampled and structurally assessed rather than reviewed line-by-line; see Findings 4.7 and 4.6.
- **Git history, blame, or contributor-pattern analysis** — no `.git` directory was present in the supplied archive.

Every quantitative figure in this report (line counts, file counts, finding counts) was produced by a script or tool invocation executed during this session; none are estimates.

---

## 3. Repository Composition

Measured directly via a language-aware line-counter across the full extracted tree (build artefacts, `node_modules` and caches excluded):

| Area | Files | Lines |
| :--- | :--- | :--- |
| `app/` (application code) | 470 | 83,834 |
| `tests/` | 1,292 | 130,236 |
| `scripts/` (tooling & governance automation) | 1,148 | 150,684 |
| `app/frontend` (TypeScript / TSX) | 237 | 20,745 |
| `alembic/versions/` (active migrations) | 47 | 6,867 |
| `docs/` | 1,949 (.md) | — |
| `audits/` | 80 (.md) | — |

**Total repository footprint:** 7,860 files, ~201 MB. Python across `app/`, `tests/`, `scripts/`, and `alembic/` totals 379,562 lines in 3,036 files.

**Observation — tooling-to-product ratio:** `scripts/` (150,684 lines, 1,148 files) is 80% larger by line count and 144% larger by file count than `app/` itself (83,834 lines, 470 files). This is the internal governance, evidence-generation, and release-verification apparatus referenced throughout `docs/` and `audits/`. It is not inherently a defect — the project has clearly invested in reproducible release evidence — but a tooling surface materially larger than the product it governs is itself a maintenance liability worth tracking: every script is code that can drift, break, or silently stop doing what its name implies (see Finding 4.1, the dead `.bandit` config, for a concrete instance of exactly that failure mode).

---

## 4. Detailed Findings

Findings are numbered by domain and ordered by severity within each. Severity reflects operational/security impact as assessed independently in this audit, not inherited from any prior document.

### 4.0 Findings at a Glance

| # | Domain | Finding | Severity |
| :--- | :--- | :--- | :--- |
| 4.1 | CI / Process | Dead `.bandit` suppression config — zero effect on actual CI Bandit invocation | MEDIUM |
| 4.2 | Data layer | ORM model & Alembic migration graph — clean, single head, zero collisions | POSITIVE |
| 4.3 | Security | B608 SQLi-pattern review: 10/11 sound; 1 implicit-only allow-list (ETL `normalize()`) | LOW |
| 4.4 | Dependencies | Inference-service image: 38 unique CVEs / 7 pkgs, outside CI pip-audit scope | HIGH |
| 4.5 | Dependencies | `requirements/ml.txt`: 48 unique CVEs / 9 pkgs (offline pipeline, not in API image) | LOW |
| 4.5b | Dependencies | Production API (`base.txt`) & production frontend deps — zero known CVEs | POSITIVE |
| 4.6 | Type safety | `mypy ignore_errors=True` on 95 modules, concentrated on auth/consent/POPIA/billing | HIGH |
| 4.7 | Static analysis | Ruff rule selection limited to E/F/W minus several disabled checks | LOW |
| 4.8 | Testing / CI | PR/runtime CI gates execute 70 of 6,661 test functions (≈1.1%) | HIGH |
| 4.9 | Testing | Three divergent, uncommitted-to-CI `coverage.json` snapshots; no active coverage gate | MEDIUM |
| 4.10 | Secrets mgmt | Gitleaks + detect-secrets wired into CI; 879 baselined candidates, clean manual sweep | POSITIVE |
| 4.11 | Compliance | POPIA data-subject-rights service structurally complete (export/erasure/correction/restriction) | POSITIVE |
| 4.12 | Frontend | `eslint-config-next` / `@next/bundle-analyzer` pinned a full major version behind next itself | LOW |
| 4.13 | Documentation | 74 top-level `docs/` subfolders, 1,949 markdown files, 80 audit docs all <40 days old | INFO |

---

### 4.1 Dead Bandit Suppression Configuration (MEDIUM)

The repository root contains a `.bandit` file declaring a skip list: `skips = B101,B104,B105,B106,B107,B110,B112,B311,B608`. This is the kind of configuration a reviewer would reasonably assume governs the project's Bandit security-scan tolerance.

**Verification performed:** Ran the exact CI invocation from `.github/workflows/security-supply-chain.yml` (`python3 -m bandit -r app scripts -ll -q`) with and without the `.bandit` file present.

**Result:** Byte-identical output in both cases (same `skipped_tests: 278`, same zero medium/high findings). The CI command never passes `-c .bandit` or `--skip`, so the file is not read at all. Separately, invoking Bandit 1.9.4 explicitly with `-c .bandit` throws a YAML parse error against this legacy INI-style file — the file would not even work if CI did reference it.

Practical impact today is low: re-running Bandit with all nosec suppressions ignored found zero HIGH-severity issues in `app/` and `scripts/`, so the dead config is not currently masking anything catastrophic. The real risk is procedural — the team believes a category-level suppression policy is in force when it is not; the actual suppression mechanism is 309 scattered inline `# nosec` comments with no central review surface.

**Recommendation:** either wire `.bandit` into the CI command (`bandit -r app scripts -ll -q -c .bandit` after converting it to the modern YAML/TOML format Bandit 1.9.x expects), or delete it to stop signalling a policy that isn't active.

---

### 4.2 Data Model & Migration Graph Integrity (POSITIVE)

Two structural risks flagged in earlier project history were independently re-tested from scratch in this audit.

#### ORM collision check
An AST walk of all 470 files under `app/` found every class carrying a `__tablename__` attribute: 103 classes, 103 distinct table names, zero duplicate class names, zero duplicate table names. The previously reported "dual repository layer with name-colliding classes" issue is not present in this snapshot.

#### Alembic migration graph
A first-pass regex parse of `alembic/versions/` initially (and incorrectly) suggested up to 27 competing heads — a useful cautionary finding in its own right about tooling reliability (see note below). Re-parsing with Python's `ast` module against every revision/down_revision assignment resolved this cleanly:
- 51 revision files total; 4 live in an `alembic/versions/_deprecated/` subfolder.
- `recursive_version_locations` is not set in `alembic.ini`, so Alembic itself never scans the `_deprecated/` subfolder — those 4 files are inert.
- The remaining 47 active revisions form exactly one root (`0001_v2_consolidated`) and exactly one head (`20260711_1510_prd11_runtime_green_exec5`).

*Note on methodology:* the initial regex-based head-detection script produced 27 false "heads" because it restricted quoted-identifier matching to hex-like characters, silently dropping any revision ID containing letters outside a–f. This was caught and corrected before being reported here, and is included deliberately — it is a concrete illustration of why this audit treats grep/regex-derived findings as provisional until confirmed by a parser that understands the underlying grammar.

---

### 4.3 SQL-Injection Pattern Review (Bandit B608) (LOW)

With inline nosec suppressions disabled, Bandit flags 11 B608 ("hardcoded SQL expression") sites in `app/`. Rather than accept either the raw Bandit count or the existing nosec annotations at face value, each of the 11 was individually read in context.

| File | Pattern | Assessment |
| :--- | :--- | :--- |
| `etl_pipeline_v2.py:434` | Column names filtered through an explicit allowed set before interpolation; values bound via placeholders | Sound |
| `etl_pipeline.py:1285` | Clause text built only from fixed literal strings; values bound via placeholders | Sound |
| `etl_pipeline_v3_additions.py:300` | Column name gated by `col in old_doc` (must already exist as a real column) | Sound |
| `semantic_retrieval/{indexing,repository}.py` (5 sites) | f-string builds only generated bind-parameter names (`:chunk_id_0`, ...); values bound separately | Sound |
| `deep_readiness_runtime.py:51` | Table name comes from a hardcoded function-default tuple, no override callers found | Sound |
| `etl_pipeline.py` ≈ line 1140, `normalize()` | Column names come from `infer_metadata()`'s dict keys, interpolated with no allow-list check at the point of SQL construction | Gap — see below |

**The single flagged gap:** `infer_metadata()` currently only ever assigns a fixed, small set of literal string keys (grade, subject, publication_year, title, plus language added by the caller), so there is no exploitable path today. But that safety is an incidental property of the current implementation, not an enforced invariant at the SQL-construction site — unlike its sibling function in `etl_pipeline_v2.py`, which explicitly filters `updates.items()` through an allowed set immediately before building the query. A future change to `infer_metadata()` that adds a dynamically-named field would silently reopen this without touching the SQL layer at all.

**Recommendation:** add the same explicit allow-list filter used in `etl_pipeline_v2.py` to this call site. Low urgency, but cheap to fix and removes a latent trap for a future contributor.

---

### 4.4 Inference-Service Dependency Vulnerabilities (Outside CI Scope) (HIGH)

pip-audit was run directly against the live OSV/PyPI advisory database for every requirements file in the repository, including two that the current CI security workflow does not cover.

| File | Installed by | Audited by CI? | Result |
| :--- | :--- | :--- | :--- |
| `requirements/base.txt` | Dockerfile.api / Dockerfile.v2 (production API) | Yes — pip-audit-dependencies job | 0 CVEs / 121 pkgs |
| `requirements/dev.txt` | Dev/CI tooling only | Yes | 0 CVEs |
| `requirements/ml.txt` | Offline training pipeline only (confirmed via Dockerfile grep) | No | 48 unique CVEs / 9 pkgs |
| `docker/requirements.inference.txt` | Dockerfile.inference (live inference service) | No | 38 unique CVEs / 7 pkgs |
| `requirements/docs.txt` | Docs build tooling | No | 9 findings / 4 pkgs |

The inference-service finding is the one that matters operationally: `docker/requirements.inference.txt` builds the image that actually serves ML inference traffic — a live, presumably network-reachable service — and it is not in scope for the `security-supply-chain.yml` workflow's pip-audit job (which only ever passes `-r requirements/base.txt -r requirements/dev.txt`). Highlights:
- `transformers==4.40.0` — 26 unique CVEs; fixes available from 4.48.0 onward.
- `starlette==0.37.2` — 7 unique CVEs; fixes from 0.40.0 onward. This is the ASGI framework directly fronting the inference HTTP endpoint.
- `torch` — additional advisory present with a fix in a later point release.

**Recommendation:** add `docker/requirements.inference.txt` (and, at lower priority, `requirements/ml.txt`) to the `pip-audit-dependencies` job's scope, and schedule an upgrade pass for transformers and starlette in the inference image specifically. This is the highest-priority actionable item in this report.

---

### 4.5 Production Runtime & Frontend Dependencies — Clean (POSITIVE)

For balance: the dependency set that actually serves live API and web traffic is in good shape. `requirements/base.txt` (121 packages, what `Dockerfile.api` actually installs) returned zero known vulnerabilities. `pnpm audit --prod` against `app/frontend`'s lockfile (311 production packages, run at the CI-pinned pnpm 9.14.4) also returned zero vulnerabilities of any severity. The exposure identified in Finding 4.4 is real but narrowly scoped to the inference path, not the whole platform.

---

### 4.6 Type-Checking Disabled Across the Highest-Risk Module Set (HIGH)

`mypy.ini` sets `ignore_errors = True` for 95 individually named modules — roughly one in five of `app/`'s ~470 files carry zero type-checking in the `mypy-typecheck` CI job (which otherwise runs `mypy app` with `check_untyped_defs = True`, a reasonably strict baseline). The finding is not the raw count; it is what the 95 modules are. A representative sample from `mypy.ini`:

```text
app/api_v2_deps/consent_lifecycle.py
app/api_v2_routers/{auth, auth_extended, billing, consent, popia}.py
app/core/{authorization, stripe_client, database}.py
app/services/{auth_service, auth_application_service, auth_lifecycle_impl, auth_runtime_boundary, jwt_keyring, consent_service, popia_service, popia_consent_lifecycle_adapter, data_subject_rights_service, runtime_consent_facade}.py
app/repositories/{auth_repository, audit_repository, base}.py
app/modules/consent/service.py
```

In other words: authentication, session/JWT handling, authorization, consent lifecycle, POPIA services, the data-subject-rights implementation, Stripe billing, and the base repository class are, as a set, exactly the modules where type errors go unchecked. This is very unlikely to be coincidental — the more probable explanation is that these modules accumulated type errors during rapid iteration and were suppressed wholesale to keep the mypy-typecheck job green, rather than fixed incrementally. That is a reasonable short-term tactic, but as a steady state it means the CI type-safety net has a hole shaped exactly like the platform's compliance and payments surface.

**Recommendation:** this does not need to be fixed in one pass. A practical path is to triage the 95 modules by real risk (auth/consent/billing first), remove `ignore_errors` for one module at a time, and fix or explicitly `# type: ignore[code]` the specific errors that surface — which also produces a far more precise audit trail than a blanket per-module suppression.

---

### 4.7 Static Analysis Rule Selection Is Deliberately Narrow (LOW)

`pyproject.toml`'s `[tool.ruff.lint]` selects only `["E", "F", "W"]` (pycodestyle errors/warnings and Pyflakes) — no bugbear (`B`), security-oriented (`S`), complexity (`C90`), or modernization (`UP`) rule families. Within that already-narrow selection, the following are explicitly disabled: `E722` (bare except), `F401` (unused import), `F811` (redefinition), `F841` (unused local variable).

This is an internally consistent picture with Finding 4.1: exception-handling hygiene (bare except, try/except/pass) is relaxed at both the Bandit and Ruff layers, and dead-code signals (unused imports/variables) are structurally invisible to CI lint. None of this is a defect by itself — many mature codebases relax `F401`/`F841` deliberately — but combined with the narrow B-rule selection, Ruff is currently functioning as a syntax/style gate rather than a correctness or security gate. Enabling the `B` (flake8-bugbear) rule set in particular would be a low-cost, high-signal addition.

---

### 4.8 CI Test Gate Executes ~1% of the Test Suite by Function Count (HIGH)

This is the most consequential process finding in this audit, and it was derived entirely from reading the six active GitHub Actions workflow files line by line — not inferred or assumed.

- **Total test functions in the repository:** 6,661 (grep for `def test_` / `async def test_` across all of `tests/`, 1,292 files)
- **Executed by `pr-core.yml` → `fast-unit-tests` job:** 4 named files, 33 test functions (`test_etl_mcp_server_startup.py`, `test_subscription_service.py`, `test_password_policy.py`, `test_popia_consent_versioning.py`)
- **Executed by `product-runtime.yml` → `runtime-services-integration` job:** 7 named files, 37 test functions (`test_api_envelope.py`, `test_security_headers.py`, `test_v2_routers.py`, `test_deep_health.py`, `test_audit_immutability.py`, `test_diagnostic_session.py`, `test_rate_limits.py`)
- **Total automatically executed per PR:** 70 of 6,661 test functions ≈ 1.05%

Critically, the `fast-unit-tests` job is not running `make test-fast` (the Makefile target that would exercise the full `tests/unit` directory under markers excluding governance/slow/llm/e2e) — it invokes pytest directly against four hand-named files. The other four workflows (`frontend-e2e.yml`, `operations-drills.yml`, `release-evidence.yml`, `security-supply-chain.yml`) perform linting, SBOM/evidence generation, and drills, but none of them broadens functional test execution beyond these 11 files.

This does not mean the other 6,591 test functions are worthless — they clearly represent substantial engineering investment (130,236 lines across `tests/`) and may run in ad hoc or manually triggered contexts (the coverage-baseline-stabilisation Makefile targets, for instance, appear designed for exactly that). But as configured, a green checkmark on a pull request currently certifies: the code compiles, passes Ruff's narrow rule set, passes mypy outside the 95 excluded modules, and passes 70 specific test functions plus an OpenAPI/route-inventory drift check. It does not certify that the other ~1,220 test files still pass.

**Recommendation:** at minimum, restore `make test-fast` (the full `tests/unit` run under the existing marker exclusions) as the PR gate in place of the four-file list, and consider a scheduled (nightly/on-merge) workflow that runs `tests/integration` and `tests/unit` in full so regressions in the untested 99% surface within a day rather than only when someone runs the suite manually.

---

### 4.9 Coverage Reporting Is Not Reproducible or CI-Enforced (MEDIUM)

Three `coverage.json` artifacts are committed simultaneously at the repository root:

| File | Generated (UTC) | Coverage % | Files measured | Statements |
| :--- | :--- | :--- | :--- | :--- |
| `coverage.json` | 2026-08-28 20:32 | 73.88% | 471 | 35,809 |
| `coverage_expansion.json` | 2026-08-28 21:22 | 34.34% | 460 | 34,999 |
| `coverage_latest.json` | 2026-09-02 07:28 | 60.01% | 454 | 35,544 |

Two snapshots generated 50 minutes apart on the same day differ by nearly 40 percentage points, and the most recent ("latest") sits between the other two rather than superseding them. This is consistent with the three files being produced by different Makefile targets against different test-marker subsets (`test-coverage` vs. `test-coverage-full` vs. one of the coverage-baseline-stabilisation scripts), not a genuine trend.

More importantly: `COVERAGE_THRESHOLD` defaults to 70 in the root Makefile, and `make test-coverage` does enforce `coverage report --fail-under=$(COVERAGE_THRESHOLD)` — but grepping every line of every active workflow file for `test-coverage`, `pytest-coverage.ini`, or `COVERAGE_THRESHOLD` returns zero matches. No active CI workflow invokes this target. The 70% gate exists in the Makefile and is simply never run automatically.

**Recommendation:** pick one canonical coverage-generation command, wire it into a scheduled or PR-triggered workflow step, and remove (or clearly date/label as historical) the superseded snapshot files so the repository doesn't carry three simultaneously "current-looking" and contradictory coverage figures.

---

### 4.10 Secrets Management — Reasonably Mature (POSITIVE)

Both layers of the repository's secrets-hygiene tooling are active in CI, not merely present as config: `security-supply-chain.yml` runs a `detect-secrets-hook --baseline .secrets.baseline` check against `app`, `scripts`, and `.github` on every PR/push and nightly, and `.gitleaks.toml` extends gitleaks' default ruleset with a scoped allowlist for known-generated fixture paths.

`.secrets.baseline` currently carries 879 previously-flagged candidates across 67 files, all baselined (i.e., accepted as reviewed non-secrets or approved test fixtures) — a large number in absolute terms, but this is the expected shape of a mature detect-secrets adoption on a codebase this size (JWT-shaped test tokens, high-entropy IDs, and hex fixtures dominate this kind of baseline in practice). A targeted manual regex sweep of `app/` for common hardcoded-credential patterns performed independently during this audit returned no plausible matches outside of configuration/environment-variable references.

This audit did not — and could not feasibly, at this scope — individually re-verify all 879 baselined entries; that remains a standing manual-review item for whoever owns the baseline file, but nothing in this pass suggests it is currently masking a live exposure.

---

### 4.11 POPIA Data-Subject Rights — Structurally Complete (POSITIVE)

`app/services/data_subject_rights_service.py` (481 lines) was reviewed directly for structural completeness against POPIA's core data-subject rights. It implements distinct, separately-testable flows for:
- **Access / export** — `create_export_request`, `build_and_complete_export`, `get_export_status`, with CSV serialization.
- **Erasure** — `create_erasure_request`, `approve_erasure`, `execute_erasure`: notably a two-step approve-then-execute flow rather than direct deletion, which is the right shape for an auditable erasure process.
- **Correction / rectification** — `create_correction_request`, `complete_correction`.
- **Processing restriction** — `create_restriction_request`, `lift_restriction`.
- **SLA tracking** — `list_overdue_export_requests`, `list_overdue_erasure_requests`.

105 test files across the repository reference popia/consent/data_subject naming, indicating this is a genuinely tested area of the codebase in absolute terms — independent of whether any given one of those files is presently wired into the narrow CI gate described in Finding 4.8.

*Caveat:* this audit reviewed the service's structural shape and method surface, not its behavioural correctness (e.g., whether `execute_erasure` actually reaches every table holding personal data, or whether SLA deadlines are enforced correctly). That would require either a live test run or a full data-flow trace against the 103-table schema, both out of scope for this pass. Combined with Finding 4.6 (this exact module's mypy checking is disabled) and Finding 4.8 (its tests are not confirmed to run automatically), the structural completeness here is encouraging but not a substitute for confirming the CI gate and type-checking gaps are closed for this specific service.

---

### 4.12 Frontend Tooling Version Drift (LOW)

`app/frontend/package.json` and its resolved `pnpm-lock.yaml` were checked directly for version consistency:

| Package | Declared / resolved version |
| :--- | :--- |
| `next` | 16.3.3 (resolved in lockfile) |
| `eslint-config-next` | 15.5.18 |
| `@next/bundle-analyzer` | 15.5.18 |
| `react` / `react-dom` | 18.3.1 |
| `typescript` | 5.4.5 |

`eslint-config-next` and `@next/bundle-analyzer` are pinned a full major version behind the next package they're meant to accompany. In practice this means ESLint's Next-specific rule set may not reflect Next 16's current conventions (App Router changes, etc.), reducing lint signal quality without necessarily breaking the build outright. Low severity, cheap fix (bump both to a 16.x-compatible release).

---

### 4.13 Documentation & Governance Volume (INFO)

`docs/` contains 74 top-level subfolders and 1,949 markdown files; `audits/` contains 80 markdown files, all with modification times inside the 40 days preceding this audit. This reflects an unusually high, sustained rate of process/audit documentation churn — consistent with the multi-week gate-remediation and canonical-truth-toolchain efforts referenced in project history. `TODO.md`'s own canonical task list (`NS-03` through `NS-13` at minimum) shows several items still explicitly unchecked, including "Warning triage" and "Current-state refresh" — i.e., the project's own tracking already acknowledges an incomplete-and-in-progress state consistent with this report's other findings, rather than presenting a false picture of completion.

No specific defect is asserted here; this is included as context for engineering leadership on where sustained effort is currently going (documentation and release-evidence generation, per Section 3's scripts/ observation) relative to product code and automated test coverage.

---

## 5. Status of Previously Reported Issues

Project history referenced three specific issues from earlier work that this audit deliberately re-tested from first principles rather than assuming still applied:

| Previously reported issue | Independent re-test result |
| :--- | :--- |
| Dual repository layer with name-colliding ORM classes causing runtime failures in billing/assessments | **RESOLVED** — AST scan of all 470 `app/` files: zero duplicate class or table names (Finding 4.2) |
| Dual Alembic migration heads | **RESOLVED** — AST-parsed revision graph: single root, single head across 47 active revisions (Finding 4.2) |
| SQL injection risk associated with the B608-suppressed sites / stale CVEs in pinned dependencies | **PARTIALLY RESOLVED** — 10 of 11 B608 sites are soundly parameterized; 1 downgraded to a defense-in-depth gap (Finding 4.3). Production API dependencies are CVE-clean, but this audit found a new, more specific dependency exposure in the inference-service image not previously scoped (Finding 4.4) |

This pattern — real, verifiable remediation on the issues that were directly targeted, alongside new findings in areas (CI gate scope, mypy suppression distribution, inference-image dependencies) that don't appear to have been previously scoped — is a reasonable and common shape for a codebase under active, iterative audit. It supports treating the engineering team's remediation track record as credible while still surfacing what hasn't yet been looked at.

---

## 6. Prioritized Recommendations

### Do first (high impact, addresses the largest assurance gaps)
- **Add `docker/requirements.inference.txt` to the CI pip-audit job's scope** and schedule a `transformers` / `starlette` upgrade for the inference image (Finding 4.4).
- **Replace the `fast-unit-tests` job's four-file pytest invocation with `make test-fast`** (the full `tests/unit` run under existing marker exclusions) as the PR gate; add a scheduled full-suite run for `tests/integration` (Finding 4.8).
- **Begin triaging the 95 `mypy ignore_errors` modules in risk order** — auth, consent/POPIA, billing first — replacing blanket module suppression with targeted, code-specific suppressions (Finding 4.6).

### Do next (real gaps, lower urgency)
- **Either fix `.bandit` to a format Bandit 1.9.x can load and wire it into the CI invocation**, or remove it to stop implying an inactive policy is active (Finding 4.1).
- **Consolidate coverage reporting to a single, CI-wired, reproducible source**; retire or clearly date the superseded `coverage.json` snapshots (Finding 4.9).
- **Add an explicit column allow-list to `etl_pipeline.py`'s `normalize()`** to match the pattern already used in its v2 sibling (Finding 4.3).

### Low-cost cleanup
- Bump `eslint-config-next` and `@next/bundle-analyzer` to a Next-16-compatible release (Finding 4.12).
- Consider enabling Ruff's flake8-bugbear (`B`) rule family for deeper-than-syntax signal at low integration cost (Finding 4.7).

---

## 7. Closing Note

This report reflects a single, time-boxed, static-analysis pass against one archive snapshot. It is a complement to — not a replacement for — the team's own live-environment testing, and several findings here (particularly around test-gate scope and coverage) would benefit from being re-verified inside an environment where the full dependency stack and CI runners can actually be exercised end to end. Where this audit's scope allowed a finding to be checked with certainty (ORM collisions, migration graph, dead config files, dependency CVEs, workflow YAML content), it was checked directly rather than inferred; where it could not (behavioural correctness of erasure/export logic, the 879 baselined secrets, full runtime test execution), that limitation is stated explicitly above rather than implied away.

