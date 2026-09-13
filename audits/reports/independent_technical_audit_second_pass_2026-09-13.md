---
title: "EduBoost V2 - Independent Technical Audit - Second Pass"
status: active
owner: engineering
reviewers: [engineering, architecture, security]
audience: internal
source_of_truth: false
last_reviewed: 2026-09-13
review_interval_days: 90
---

# EduBoost V2 — Independent Technical Audit — Second Pass
**Codebase, CI/CD, Security & Compliance-Path Review**

**Source:** NkgoloL/Eduboost-V2 (master, GitHub archive snapshot supplied 13 September 2026)  
**Audit date:** 13 September 2026 (prior independent pass: 10 September 2026)  
**Prepared for:** EduBoost SA Engineering Leadership  
**Method:** Static analysis, dependency auditing, and configuration verification performed directly against the extracted repository archive. An internally authored "Comprehensive True State Technical Audit Report" (13 Sep 2026) was supplied alongside the archive and is treated in this report strictly as a second data point to cross-check — every finding below was independently re-derived from the code and configuration, not adopted from that document.

---

## 1. Executive Summary

This is the second independent, tool-driven audit of the EduBoost V2 codebase performed in this engagement, run three days after the first (10 September 2026) against a fresh archive snapshot (13 September 2026). As with the first pass, every figure and finding below was re-derived directly from the code, CI configuration, and dependency manifests in this session — none were taken on the authority of the internally authored "True State Technical Audit" document supplied alongside this snapshot, which is referenced only where this audit's own results agree, refine, or diverge from it.

The three days between snapshots saw one clear, large, genuine engineering effort: 63 new files (mostly tests) were added, headlined by a stated push from ~66% to ~95.7% statement coverage across `app/` via 17 test-writing "batches." Direct sampling of that new test code found it substantively real — proper service-layer unit tests with meaningful mocking and assertions, not placeholder stubs. That work is genuine and should be credited as such.

Set against that, this audit's central finding is that the assurance pipeline around that new work did not change in the way its surrounding documentation implies:

- **The two GitHub Actions jobs that actually execute tests (`pr-core.yml`'s `fast-unit-tests`, `product-runtime.yml`'s `runtime-services-integration`) are byte-for-byte unchanged from three days ago.** They still run the same 4 and 7 hand-named files respectively — 70 of the codebase's (now) 7,363 test functions, ≈ 0.95%. None of the 700+ new test functions added in the last three days is wired into automatic execution.
- **`pr-core.yml` did gain three new steps in this window** — a `COVERAGE_THRESHOLD: "90"` environment variable, a "Test Import Integrity Audit," a "Pytest Blanket Test Collection Gate," and a "Verify Coverage Threshold Alignment" step. Each was read in full during this audit: the import audit is a static AST check that symbols exist; the collection gate runs `pytest --collect-only` (confirms tests can be gathered, not that they pass); and the threshold-alignment check is a pure text/regex comparison across Makefile, CI YAML, and `.coveragerc` confirming they all quote the number 90 — it does not run `coverage.py` or execute a single test. None of the three measures, executes, or gates on real test outcomes or real coverage.
- **The three contradictory `coverage.json` snapshots flagged in the 10 September pass have been deleted from the repository rather than reconciled** — removing the visible symptom without adding a CI step that actually regenerates and enforces a real number.

Two further findings, independently confirmed in this pass and not covered in the 10 September report:
- `app/api_v2_routers/diagnostics.py` imports a wrapper module that uses `importlib.import_module()` at runtime to reach the repository layer directly, which is invisible to the `.importlinter` static contract forbidding exactly that import — a genuine, working circumvention of an architectural guardrail, confirmed by reading both files.
- Consent/POPIA logic is now spread across at least 14 identically-themed files under `app/services/` alone (`consent_service`, `consent_compat`, `consent_runtime_compatibility`, `consent_runtime_orchestrator`, `popia_service`, `popia_dsr_service`, `popia_transactional_lifecycle`, `runtime_consent_facade`, and others) — naming that, on its own, reads as a history of successive adapters layered over earlier implementations rather than a single owned path.

Everything independently reconfirmed as sound in the first pass remains sound: zero ORM/table collisions across 103 models, a single unambiguous Alembic head across 47 active revisions, zero known CVEs in the production API dependency set (`requirements/base.txt`, 121 packages) and in production frontend dependencies (311 packages). The inference-service image (`docker/requirements.inference.txt`) still carries the same 38 unique CVEs identified three days ago, unchanged — no remediation occurred in the interim.

**Overall assessment:** real engineering effort went into test volume this week, but the mechanisms that would make that effort visible and durable to CI — actual test execution and actual coverage measurement — were not the mechanisms that changed. What changed instead were three new checks that verify the paperwork is consistent. That distinction is the throughline of this report.

---

## 2. Scope & Methodology

### 2.1 What was reviewed
`Eduboost-V2-master_1_.zip` (21 MB compressed, ~7,927 files after extraction) was extracted and analysed in full, independently of the accompanying `true_state_technical_audit_report_2026-09-13.md`. As before, this is a GitHub source export with no `.git` directory — no commit history, blame, or diff metadata was available from the archive itself; the commit hash cited in the supplied document (`cb2e62c6d`) could not be independently corroborated from the archive contents and is not relied upon anywhere in this report.

Where useful, this report also compares directly against the fully extracted 10 September 2026 snapshot retained from this engagement's first pass, giving an exact, tool-verified diff rather than a description of change.

Tooling used, run directly against the extracted source in this session:
- **Path-level diff (`comm`)** between the 10 and 13 September archives to establish exactly what was added, removed, or left untouched, before spending analysis effort — changed areas were re-verified from scratch; unchanged areas were confirmed identical rather than re-derived from prose.
- **AST-based Python parsing** for ORM/table-collision detection and the Alembic revision graph (same methodology as the first pass, applied fresh to the new snapshot).
- **Bandit 1.9.4**, run under the repository's exact CI invocation and under nosec-disabled re-runs to independently verify every suppressed B608 finding by reading the surrounding code, not by trusting either the suppression or the raw severity label.
- **pip-audit** against `requirements/base.txt` and `docker/requirements.inference.txt`, re-run against the live OSV/PyPI advisory database.
- **`mypy.ini`** reviewed directly and diffed byte-for-byte against the 10 September copy; a bounded, sandboxed mypy re-run was attempted against one suppressed module to test the externally supplied report's "56+ real type errors" claim (result: inconclusive in this sandbox — see §2.2).
- **Direct reading** of `scripts/coverage_suites/coverage_contract.py`, `scripts/audit_test_imports.py`, and both `.github/workflows/pr-core.yml` and `product-runtime.yml`, diffed against their 10 September versions.
- **Direct reading** of `.importlinter` and the two files implicated in the dynamic-import-circumvention claim.

### 2.2 What was not performed, and why
- **Full dependency installation and a live pytest run of the full suite.** A bounded, sandboxed attempt to re-run mypy against `app/core/stripe_client.py` with its `ignore_errors` override removed completed but returned no findings — with `ignore_missing_imports = True` and the `stripe` package itself not installed in this sandbox, mypy silently treats the unresolved import as `Any`, which suppresses exactly the class of error most likely to be real. This audit therefore cannot independently confirm or refute the externally supplied report's specific "56+ real type errors" figure, and says so plainly rather than repeating the number.
- **Live reproduction of the frontend build failure attributed to `next/font/google`.** The code pattern that would cause it was confirmed directly (`app/frontend/src/app/layout.tsx` imports `Geist`, `Geist_Mono` from `next/font/google`, which fetches font files from Google's CDN at build time), but this sandbox has no network path to `fonts.googleapis.com` to reproduce the failure live. The finding below is stated as "structurally confirmed, not reproduced" accordingly.
- **Exhaustive review of all 22 consent/POPIA-named files or manual verification of erasure-cascade completeness against all 103 tables** — sampled and structurally assessed, as in the first pass.

---

## 3. What Changed Between 10 and 13 September

Computed via a full recursive path diff between the two archives, not by description:

| Change | Detail |
| :--- | :--- |
| **Removed** | `coverage.json`, `coverage_expansion.json`, `coverage_latest.json` — the three contradictory coverage snapshots flagged in the first-pass report (Finding 4.9, 10 Sep) are gone. |
| **Added — tests** | 58 new test files, +29,818 lines in `tests/` (130,236 → 160,054), +702 test functions (6,661 → 7,363), organized as 17 named "batches" (412–428) per `docs/reports/coverage_target_90_completion_report.md` |
| **Added — scripts** | `scripts/audit_test_imports.py` (new); `scripts/maintenance/regenerate_codemaps.py` (new) |
| **Added — docs** | `docs/reports/coverage_target_90_completion_report.md`; a duplicate true-state verification report under both `audits/reports/` and `docs/audits/reports/` |
| **Changed — CI** | `pr-core.yml` gained a `COVERAGE_THRESHOLD: "90"` env var and three new steps: Test Import Integrity Audit, Pytest Blanket Test Collection Gate, Verify Coverage Threshold Alignment (see Finding 5.1) |
| **Unchanged** | `app/` (470 files, +102 lines only); ORM model set (103 tables); Alembic head/root; `mypy.ini` (byte-identical, 95 `ignore_errors` modules); route inventory (240 decorators, same dual-prefix mount); the actual `fast-unit-tests` and `runtime-services-integration` job bodies (same 4 + 7 named files); inference-image dependency pins (same 38 unique CVEs) |

---

## 4. Repository Composition (13 September Snapshot)

| Area | Files | Lines | Δ vs 10 Sep |
| :--- | :--- | :--- | :--- |
| `app/` | 470 | 83,936 | +102 lines |
| `tests/` | 1,350 | 160,054 | +58 files / +29,818 lines |
| `scripts/` | 1,150 | 151,148 | +2 files / +464 lines |
| `app/frontend` (TS/TSX) | 237 | 20,745 | unchanged |
| `alembic/versions/` (active) | 47 | 6,867 | unchanged |
| **Total test functions** (`grep def test_`) | 7,363 | — | +702 |

---

## 5. Detailed Findings

### 5.0 Findings at a Glance

| # | Domain | Finding | Severity |
| :--- | :--- | :--- | :--- |
| 5.1 | CI / Process | New CI "coverage" steps verify config paperwork, not real test execution or coverage | HIGH |
| 5.2 | Testing / CI | Test-execution gate still 70/7,363 (≈0.95%) — unchanged despite +702 new test functions | HIGH |
| 5.3 | Architecture | Dynamic importlib call in `diagnostics.py` bypasses the `.importlinter` router→repository contract | MEDIUM |
| 5.4 | Security | Bandit B608: 11 findings, all MEDIUM severity — 10 sound on manual review, 1 unchanged gap | LOW |
| 5.5 | Security | Two separate broken `.bandit` config files (root and `scripts/`), still unreferenced by CI | MEDIUM |
| 5.6 | Dependencies | Inference-image CVEs (38 unique, transformers/starlette) unchanged — not remediated in 3 days | HIGH |
| 5.7 | Type safety | `mypy ignore_errors` set unchanged (95 modules, same auth/consent/billing concentration) | HIGH |
| 5.8 | Compliance architecture | 22 consent/POPIA-named files (14 under `services/` alone) — adapter/compat naming suggests layering | MEDIUM |
| 5.9 | Frontend | `next/font/google` usage structurally explains reported offline-build failure (not reproduced live) | LOW |
| 5.10 | Testing | New test batches are substantively real on manual sampling, not superficial coverage padding | POSITIVE |
| 5.11 | Dependencies | Production API (`base.txt`, 121 pkgs) and production frontend deps — still zero known CVEs | POSITIVE |
| 5.12 | Data layer | ORM (103 tables) and Alembic graph (single root/head) — still clean, unchanged | POSITIVE |

---

### 5.1 New CI "Coverage" Steps Verify Configuration Consistency, Not Test Outcomes (HIGH)

This is the most consequential finding of this pass, and the one this audit spent the most effort independently confirming by reading source rather than names. `pr-core.yml` added three steps since 10 September:

| Step name | What it actually runs | What it actually checks |
| :--- | :--- | :--- |
| Test Import Integrity Audit | `python3 scripts/audit_test_imports.py` | AST-walks every `tests/test_*.py` file and confirms `from app.X import Y` statements refer to symbols that exist. Does not execute any test. |
| Pytest Blanket Test Collection Gate | `python3 -m pytest --collect-only -q` | Confirms pytest can gather (import + parametrize) all test items without a collection error. Does not run a single test body or assertion. |
| Verify Coverage Threshold Alignment | `scripts/coverage_suites/verify_coverage_contract.py --threshold-only` | Reads a JSON contract file, the Makefile, the CI YAML, `pytest-coverage.ini`, and `.coveragerc` as text, and checks they all state the number 90 (and a couple of related flags like `branch=True`). Never invokes `coverage.py` or pytest with coverage instrumentation. |

The third step was read line by line in `scripts/coverage_suites/coverage_contract.py`'s `evaluate_threshold_alignment()` function: its `"valid"` result is an `all([...])` over nine boolean checks, every one of them a string match or regex against a config file's contents — for example `"app"` in `thresholds.get("coverage_source_paths", [])` and `"branch = True"` in `coveragerc_text`. There is no code path in this function that runs a test, measures a statement, or computes a percentage. A build can pass this step with 0% real coverage, provided every config file quotes the number 90 consistently.

This matters because the surrounding documentation (`docs/reports/coverage_target_90_completion_report.md`, Finding 5.10) explicitly frames this window's work as closing a coverage gate. It does not close it. It adds visibility into whether the gate's configuration is self-consistent, which is a real and not-worthless check — but it is a different thing, and the CI log for this job will read as a coverage-related pass regardless of whether the underlying suite passes, fails, or was never run.

**Recommendation:** replace or supplement the threshold-alignment step with an actual coverage run (`make test-coverage`, which does exist and does enforce `--fail-under=$(COVERAGE_THRESHOLD)` against real instrumentation) inside the CI workflow itself.

---

### 5.2 Test-Execution Gate Unchanged at ~1% Despite Substantial New Test Volume (HIGH)

Directly diffed against the first pass: the `fast-unit-tests` job in `pr-core.yml` and the `runtime-services-integration` job in `product-runtime.yml` are byte-for-byte identical to their 10 September versions. Both still invoke pytest against the same 11 hand-named files:

```text
tests/unit/test_etl_mcp_server_startup.py, test_subscription_service.py, 
test_password_policy.py, test_popia_consent_versioning.py 

tests/integration/test_api_envelope.py, test_security_headers.py, test_v2_routers.py, 
test_deep_health.py, test_audit_immutability.py, test_diagnostic_session.py, 
test_rate_limits.py
```

- **Test functions executed automatically per PR:** 70 (unchanged)
- **Total test functions in the repository (13 Sep):** 7,363 (up from 6,661 on 10 Sep — +702 in three days)
- **Effective automatic execution coverage by function count:** ≈ 0.95% (was ≈1.05% three days ago — marginally worse in relative terms, because the denominator grew and the numerator didn't)

None of the 58 new test files added in this window — including the ones specifically targeting previously low-coverage packages like `app/services/` (92.9% claimed) — is reachable by an automatic PR check. They can only currently be exercised by a developer manually running `make test-coverage-full` or a similar target locally. Combined with Finding 5.1, the practical state is: substantial new test assets exist, are plausibly high quality (Finding 5.10), and are invisible to CI.

---

### 5.3 Import-Linter Contract Circumvented via Runtime Dynamic Import (MEDIUM)

`.importlinter` defines a forbidden-import contract intended to keep the router layer off the repository layer directly:

```ini
[importlinter:contract:api_v2_routers_do_not_import_repositories]
source_modules = app.api_v2_routers
forbidden_modules = app.repositories
```

`app/api_v2_routers/diagnostics.py` does not import `app.repositories` directly — it imports `app.api_v2_deps.diagnostic_repositories` (line 19), which the static contract does not forbid. That module, however, resolves the real repository classes at runtime:

```python
# app/api_v2_deps/diagnostic_repositories.py
from importlib import import_module 
_REPOSITORY_TARGETS: dict[str, tuple[str, ...]] = {
    "learner": ("app.repositories.repositories.LearnerRepository", ...),
    ...
}
# ... module = import_module(module_name)
```

Both files were read directly to confirm this. `lint-imports` is an AST/import-statement-level static checker; a string literal passed to `importlib.import_module()` at runtime is invisible to it by construction — this is not a bug in the linter, it is a structural blind spot that any dynamic-import indirection will produce against any static import-boundary tool. `diagnostics.py` then calls the resolved repository objects directly (e.g. `diagnostic_repositories.learner(db).update_theta(...)` at line 210), performing persistence operations from the router layer in practice, which is exactly what the contract exists to prevent.

**Recommendation:** either route `diagnostics.py` through the same domain-service layer other routers use, or if the dynamic-resolution pattern is intentional (e.g., for lazy loading or circular-import avoidance), add an explicit, documented exception and a runtime assertion rather than relying on the static contract to catch it — it currently cannot.

---

### 5.4 SQL-Injection Pattern Review (Bandit B608) — Refined From First Pass (LOW)

Re-run against the 13 September snapshot with nosec disabled: still exactly 11 B608 findings, and this pass captured the severity/confidence fields precisely, which the first-pass report did not state explicitly. All 11 are rated MEDIUM severity by Bandit; six of them (the `semantic_retrieval/{indexing,repository}.py` sites) carry LOW confidence, the remaining five MEDIUM confidence.

Severity alone, without reading the code, would fairly be characterised as "11 medium-severity SQL injection findings" — and a supplied review characterising a subset of these six as exactly that is not wrong about the raw tool output. This audit went a level deeper on all 11 sites (same methodology as the first pass, re-verified against this snapshot's current line numbers) and finds:

- **The 6 `semantic_retrieval` sites (LOW confidence):** the interpolated f-string content is exclusively generated SQLAlchemy bind-parameter names (e.g. `:chunk_id_0`, `:chunk_id_1`) used inside an `IN (...)` clause; actual values are bound separately via the `params` dict. This is the documented, correct pattern for variable-length parameter lists in SQLAlchemy `text()`, and Bandit's own low-confidence rating reflects that its pattern-matcher can't distinguish this from a genuine injection — it isn't one.
- **4 of the remaining 5 (MEDIUM confidence):** use either fixed literal clause text or an explicit column allow-list before interpolation — also sound.
- **1 (`etl_pipeline.py`, `normalize()`, line ~1140):** still lacks an explicit allow-list at the point of SQL construction, relying instead on `infer_metadata()` only ever assigning a fixed set of literal keys today. This is the same defense-in-depth gap identified on 10 September; it has not been addressed.

**Net assessment:** Bandit's MEDIUM severity label is an accurate description of its own heuristic, but is not, on independent code-level review, an accurate description of exploitability for 10 of the 11 sites. Reporting the raw count and severity without that review — whether by this audit or any other — would overstate the live risk here.

---

### 5.5 Two Non-Functional `.bandit` Configuration Files (MEDIUM)

Confirmed independently: both `/.bandit` and `/scripts/.bandit` exist, contain identical skip lists, and both throw a YAML parse error (expected `'<document start>'`, but found `'<scalar>'`) when loaded via `bandit -c` against the pinned Bandit 1.9.4. Neither file is present in the actual CI invocation (`bandit -r app scripts -ll -q`, no `-c` flag) in `.github/workflows/security-supply-chain.yml`, confirmed unchanged from the first pass. Two broken, unreferenced copies of the same dead configuration is a slightly worse version of the single-file finding reported on 10 September, not a new class of problem.

---

### 5.6 Inference-Service Dependency CVEs — Unremediated (HIGH)

pip-audit re-run against `docker/requirements.inference.txt` on the 13 September snapshot returns the same 38 unique CVEs across the same 7 packages as three days prior — the pinned versions have not moved:

| Package | Pinned version | Unique CVEs |
| :--- | :--- | :--- |
| `transformers` | 4.40.0 | 26 |
| `starlette` | 0.37.2 | 7 |
| `torch`, `sentencepiece`, `accelerate`, `python-dotenv`, `setuptools` | (unchanged) | 1 each |

`requirements/base.txt` (the production API's actual dependency set, 121 packages) remains at zero known CVEs, confirmed again in this pass. `security-supply-chain.yml`'s `pip-audit-dependencies` job still scopes only `-r requirements/base.txt -r requirements/dev.txt` — the inference image remains outside its coverage. This is the same highest-priority open item from the first-pass report, carried forward unresolved.

---

### 5.7 Type-Checking Suppression Set Unchanged (HIGH)

`mypy.ini` is byte-for-byte identical between the 10 and 13 September snapshots (diff confirms zero differences). The 95-module `ignore_errors = True` set, concentrated on authentication, consent/POPIA, billing/Stripe, JWT-keyring, and the base repository class, is unchanged and unaddressed.

A bounded attempt in this pass to independently test the externally supplied report's claim of "56+ real type errors" by removing the suppression for one module (`app/core/stripe_client.py`) and re-running mypy in this sandbox returned no findings — but with the `stripe` package not installed and `ignore_missing_imports = True` set repository-wide, mypy silently falls back to `Any` for the unresolved import, which is very likely to suppress exactly the errors a live install would surface. This audit treats the "56+" figure as unverified rather than confirmed or refuted, and recommends whoever owns a fully-installed environment re-run `mypy app --config-file <(sed 's/ignore_errors = True//' mypy.ini)` directly to get a real count.

---

### 5.8 Consent / POPIA Logic Spread Across at Least 22 Files (MEDIUM)

A direct filename search for consent/popia naming across `app/` (excluding tests) returns 22 files. Restricted to `app/services/` alone, 14:

```text
consent.py, consent_compat.py, consent_expiry_service.py, consent_renewal_service.py, 
consent_runtime_compatibility.py, consent_runtime_orchestrator.py, consent_service.py, 
first_consent_runtime_wiring.py, popia_consent_lifecycle_adapter.py, popia_dsr_service.py, 
popia_erasure_safety.py, popia_service.py, popia_transactional_lifecycle.py, 
runtime_consent_facade.py
```

This is a larger count than the 6 "overlapping POPIA services" characterised in the externally supplied review — that figure likely reflects a narrower reading of what counts as a service. Either way, the naming pattern itself is the finding: `compat`, `runtime_compatibility`, `adapter`, `facade`, and `first_..._wiring` are the vocabulary of successive shims layered over earlier implementations as requirements evolved, not a single, currently-owned consent path. This is not evidence of a functional defect — Finding 5.10's positive assessment of test quality and the first pass's confirmation that `data_subject_rights_service.py` is structurally complete both still stand — but 14 files carrying this much apparent historical layering in the platform's most compliance-sensitive domain is a maintainability and audit-surface risk worth a deliberate consolidation pass, independent of whether any one of them currently has a bug.

---

### 5.9 Frontend Build Fragility in Network-Restricted Environments (LOW)

`app/frontend/src/app/layout.tsx` imports `Geist`, `Geist_Mono` from `next/font/google` — confirmed directly by reading the file. Next.js's `next/font/google` integration fetches the referenced font files from Google's font CDN at build time to self-host them; in any CI runner, container build, or sandbox without egress to `fonts.googleapis.com` / `fonts.gstatic.com`, this step would fail or hang. This sandbox has no route to that domain either, so the failure itself was not reproduced live in this pass — the finding is limited to confirming the code pattern that would structurally cause it. If the production build pipeline already has that egress allowed, this is a non-issue in practice; if any offline/air-gapped build path is required (local dev without internet, restricted CI runners, etc.), this is the specific line that would need a self-hosted font or a `next/font/local` swap.

---

### 5.10 New Test Batches Are Substantively Real, Not Superficial (POSITIVE)

For balance, and because it would have been easy to assume otherwise given Finding 5.1: a direct read of sampled new test files (e.g. `tests/unit/modules/test_modules_burndown_complete_batch422.py`, 619 lines) shows genuine unit-test construction — AsyncMock-based repository mocking, patched audit-event writers, assertions against actual service method return values and side effects, targeting named, specific source modules and statement counts. This is not "import the module and assert True" padding. The batch-numbered, mechanically-named commit pattern (Batches 412–428) is unusual and worth noting as a style observation, but the content sampled does not support characterising the underlying work itself as low-value — only the claim that it is currently CI-enforced (Findings 5.1, 5.2).

---

## 6. Status Tracking From the First Pass (10 September)

| First-pass finding | Status on 13 September re-test |
| :--- | :--- |
| Dead `.bandit` suppression config (root) | **UNCHANGED** — still dead; a second copy at `scripts/.bandit` independently confirmed also dead (Finding 5.5) |
| ORM/Alembic integrity (clean) | **UNCHANGED** — still clean, identical head/root, zero collisions |
| B608 SQLi review (10 sound / 1 gap) | **UNCHANGED** — same 11 sites, same single unaddressed gap; severity/confidence fields now stated explicitly (Finding 5.4) |
| Inference-image CVEs (38 unique, out of CI scope) | **UNCHANGED** — not remediated, not brought into CI scope |
| Production API / frontend deps clean | **UNCHANGED** — still zero known CVEs |
| `mypy ignore_errors` on 95 high-risk modules | **UNCHANGED** — byte-identical `mypy.ini` |
| CI test gate ≈ 1% of test functions | **WORSE IN RELATIVE TERMS** — still 70 functions executed automatically, against a denominator that grew by 702 (Finding 5.2) |
| Three contradictory `coverage.json` snapshots | **SYMPTOM REMOVED, ROOT CAUSE NOT ADDRESSED** — files deleted; no CI step performs a real coverage run in their place (Finding 5.1) |

---

## 7. Prioritized Recommendations

### Do first
- **Add a real coverage-measuring step** (`make test-coverage` or equivalent, with actual instrumentation) to CI in place of, or alongside, the current threshold-alignment text check (Finding 5.1).
- **Expand the `fast-unit-tests` / `runtime-services-integration` jobs** to run the full `tests/unit` and `tests/integration` trees (or at minimum the 58 new files) rather than the same 11 named files (Finding 5.2).
- **Bring `docker/requirements.inference.txt` into the `pip-audit-dependencies` job's scope** and schedule a transformers / starlette upgrade (Finding 5.6, carried forward unresolved from 10 September).

### Do next
- **Close, document, or explicitly except the `diagnostics.py` → `diagnostic_repositories` dynamic-import path** against the `.importlinter` contract it currently evades (Finding 5.3).
- **Begin triaging the 95 mypy-suppressed modules in risk order**; re-run the type check in a fully-installed environment to get a real error count rather than relying on any secondhand figure (Finding 5.7).
- **Scope a consolidation pass for the 14 `services/` consent/POPIA files** — at minimum, document which of `consent_compat` / `consent_runtime_compatibility` / `first_consent_runtime_wiring` / `popia_consent_lifecycle_adapter` is the currently-authoritative path and which are retained for compatibility only (Finding 5.8).

### Low-cost cleanup
- Delete or fix `scripts/.bandit` alongside the root copy (Finding 5.5); if an offline/air-gapped build path is ever required, swap `next/font/google` for `next/font/local` (Finding 5.9).

---

## 8. Closing Note

This report and the 10 September report together give two verified, three-days-apart data points on the same codebase — which is more informative than either alone, because it separates what changed from what someone merely wrote about. The pattern that emerges is specific rather than generic: real product and test code moved forward this week; the CI mechanisms that would make that progress independently verifiable did not move in step, and the additions made to CI in this window describe themselves as coverage-related without measuring coverage. That is a precise, fixable gap, not a broad indictment of the engineering work — and the recommendations in Section 7 are scoped accordingly.
