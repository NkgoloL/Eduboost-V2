# EduBoost SA V2 — Comparative Technical Audit Report

**Report Date:** 4 May 2026  
**Reviewed Repo:** github.com/NkgoloL/Eduboost-V2 (master branch)  
**Compared Against:** EduBoost_V2_Technical_Report (report.js — the existing internal report)  
**Auditor:** Independent Review (Claude Sonnet 4.6)

> **Scope note:** GitHub's robots.txt prevented direct crawling of commit history pages and directory trees. This review is based on files successfully fetched: the root README, CHANGELOG.md, SECURITY.md, AGENT_INSTRUCTIONS_V2.md, and gemini-code-1777601244294.md (the declared V2 architectural north star). Where access was limited, this report flags the gap rather than assume.

---

## Executive Summary

The existing report presents EduBoost SA V2 as a largely complete, production-ready modular monolith with a clean architectural transition, closed POPIA compliance gaps, and a hardened security posture. Direct inspection of the publicly accessible NkgoloL/Eduboost-V2 repository tells a materially different story across several critical dimensions.

**The five most significant divergences are:**

1. The V1 "five-pillar" architecture has not been deleted — it coexists with V2 code in the active repository.
2. The existing report marks multiple security items as complete (refresh tokens, secrets scanning, dependency auditing) that SECURITY.md explicitly calls out as planned or not yet implemented.
3. The NkgoloL/Eduboost-V2 repo shows only 3 commits, not the 50 claimed. The higher commit count likely belongs to a private or alternative fork.
4. The JWT expiry the report states (15 minutes) directly contradicts what SECURITY.md documents (24 hours).
5. The Fourth Estate audit mechanism described in the report (PostgreSQL RULEs) still coexists in documentation with the legacy Redis stream approach described in SECURITY.md.

**Overall verdict:** The existing report accurately captures the intended target architecture and the progress made on the working fork, but it overstates the completion status of several items relative to what is verifiable in the public canonical repository. It should be treated as a forward-looking design document with aspirational completion claims, not a current-state audit.

---

## 1. Repository Metadata — Report vs Reality

| Attribute | Report Claims | Repo Reality | Verdict |
|---|---|---|---|
| Primary repo | github.com/NkgoloL/Eduboost-V2 | Confirmed | Match |
| Commits (fork) | ~50 commits | NkgoloL/Eduboost-V2 shows **3 commits** on master | **Mismatch — significant** |
| Commits (origin) | ~68 commits | Not publicly verifiable (alternative link blocked by robots.txt) | Unverifiable |
| Language split | Python 81.8%, JS 9.4%, PLpgSQL 5.5%, TS 1.4% | Python 81.8%, JS 9.5%, PLpgSQL 5.7%, TS 1.3% | Near-match (rounding) |
| License | MIT | MIT badge confirmed in README | Match |
| Python target | 3.11+ | `.python-version` file present; README confirms 3.11+ | Match |
| Frontend | Next.js 14 (App Router) | README confirms Next.js 14 | Match |
| Deployment target | Azure Container Apps | Confirmed (bicep/ directory, docker-compose.aca.yml present) | Match |

**Key finding:** The 3-commit count on the NkgoloL repo strongly suggests this is a mirror or early push of a much larger working fork, not the full development history. The report's commit-specific references (e.g., `commit 1160234`, `b715422`) are only verifiable against a fork that is either private or behind a different account.

---

## 2. Architectural State — V1 Deletion Claim

The existing report states: *"The V1 codebase has been entirely deleted and all V2 canonical files are in place."*

The README contradicts this directly:

> "The repository therefore currently contains **two truths**: a current runtime that remains operational and a V2 target architecture that is now the active implementation direction."

The README explicitly describes `app/api/routers/*` as the legacy compatibility surface still in place, including files like `judiciary.py`, `fourth_estate.py`, `orchestrator.py`, and `profiler.py` — all belonging to the original Five Pillar architecture. The V2 surface (`app/api_v2.py`, `app/api_v2_routers/`, `app/modules/`) exists alongside, not instead of, the legacy code.

**Verdict: The V1 deletion claim in the report is false as of the public repository state.** The repo is in an active, dual-state migration. The existing report may reflect a fork state where V1 was removed, but this is not confirmed in the canonical NkgoloL repo.

---

## 3. Security Claims — Critical Contradictions

This is the most consequential section. The existing report's security status table marks multiple items as complete with specific commit references. The SECURITY.md committed in the same repository marks the same items as incomplete.

### 3.1 Refresh Token Rotation

- **Report claims:** "Rotating refresh cookies with Redis-backed denylist for forced session invalidation" — listed as implemented.
- **SECURITY.md states:** "Refresh token flow: planned but not yet implemented" (listed under Known Gaps).
- **Verdict: Direct contradiction.**

### 3.2 JWT Token Expiry

- **Report claims:** "JWT access tokens with 15-minute expiry."
- **SECURITY.md states:** `JWT_EXPIRY_HOURS=24` (24-hour expiry).
- **Verdict: Direct numerical mismatch.** A 24-hour expiry on a platform handling children's data, without refresh token rotation, is a material security gap. Either the SECURITY.md has not been updated to reflect working fork changes, or the report describes a desired future state.

### 3.3 Automated Dependency Vulnerability Scanning

- **Report claims:** pip-audit, npm audit, Bandit, and gitleaks complete (commits b715422, b1bfa3e, 25488dc).
- **SECURITY.md states:** "Automated dependency vulnerability scanning (Dependabot or `pip-audit`) is not yet configured — this is a known gap."
- **Verdict: Direct contradiction.**

### 3.4 CI/CD Secrets Scanning

- **Report claims:** Complete — commits 7407889 and d8a6b54 cited.
- **SECURITY.md states:** "CI/CD secrets scanning not configured — Planned."
- **Verdict: Direct contradiction.**

### 3.5 Right-to-Erasure (POPIA §24) E2E Verification

- **Report claims:** Complete — commit 1160234 cited. E2E test suite with 10 tests described.
- **SECURITY.md states:** "Right-to-erasure (POPIA Section 24) not end-to-end verified — In progress."
- **Verdict: Direct contradiction.** The SECURITY.md Known Gaps table has not been updated to reflect claimed completions.

### 3.6 Consent Audit Trail

- **Report claims:** Complete — commit 1160234 cited.
- **SECURITY.md states:** "Consent audit trail incomplete across all workflows — In progress."
- **Verdict: Direct contradiction.**

### Summary Security Contradiction Table

| Security Item | Report Status | SECURITY.md Status | Verdict |
|---|---|---|---|
| Refresh token rotation | Complete | Planned — not implemented | **CONTRADICTED** |
| JWT expiry | 15 minutes | 24 hours (`JWT_EXPIRY_HOURS=24`) | **CONTRADICTED** |
| Dependency scanning | Complete (pip-audit, Bandit) | Not configured — known gap | **CONTRADICTED** |
| CI/CD secrets scanning | Complete | Planned — not configured | **CONTRADICTED** |
| Right-to-erasure E2E | Complete | In progress — not verified | **CONTRADICTED** |
| Consent audit trail | Complete | Incomplete — in progress | **CONTRADICTED** |
| HTTPS enforcement | Complete | By design; production only | Match (nuanced) |
| RBAC (4-role) | Implemented | Confirmed in architecture docs | Match |
| Pseudonymisation | Implemented | Confirmed in SECURITY.md | Match |
| Fernet/AES encryption | Implemented | Confirmed (Fernet used) | Match |
| PII scrubbing (RLHF) | Complete | Confirmed in CHANGELOG | Match |

---

## 4. Audit Trail Architecture — Dual-Mechanism Inconsistency

The existing report describes a clean, PostgreSQL-native audit implementation (migration 0006, `audit_events` table, PostgreSQL RULEs for immutability). This is described as the V2 audit approach, explicitly replacing the legacy Redis stream.

SECURITY.md documents the current audit mechanism differently:

> "The `fourth_estate.py` module writes all sensitive operations to a Redis stream (`eduboost:audit_stream`). Stream max length: 100,000 entries. Audit records are immutable once written (append-only stream)."

The gemini-code V2 north star document confirms the migration intent: "The Fourth Estate must now write directly to a PostgreSQL append-only audit table, completely removing the Redis Streams dependency."

This means the repo contains at minimum three states of the audit system simultaneously:

1. **Legacy (V1):** `fourth_estate.py` → Redis stream (documented in SECURITY.md as current)
2. **Target (V2 spec):** PostgreSQL `audit_events` table with RULEs (described in gemini-code)
3. **Claimed complete (report):** `app/repositories/audit_repository.py` + migration 0006

**Verdict:** The PostgreSQL audit trail described in the report is likely implemented in the working fork but has not been reflected back into canonical-repo documentation. The SECURITY.md still describes the legacy Redis stream as the active mechanism, creating a compliance documentation risk.

---

## 5. V2 Architecture Completion — Revised Assessment

The gemini-code-1777601244294.md file (the V2 architectural north star) describes the project state as: `V2_BASELINE_IN_PROGRESS`.

The existing report rates Architecture Completeness as "High" and describes the V2 modular monolith as "fully structured."

These are only reconcilable if the working fork has progressed significantly beyond the canonical 3-commit NkgoloL repo. The baseline state in the canonical repo is more accurately described as: V2 directory structure in place alongside legacy code, with Docker Compose and documentation scaffolded, and business logic migration in progress.

| Dimension | Report Rating | Revised Rating | Notes |
|---|---|---|---|
| Architecture Completeness | High | **Medium — In Progress** | V1 and V2 coexist; not a clean cutover in canonical repo |
| POPIA Compliance | Functional | **Partially Functional** | Core mechanisms present; key gaps still listed in SECURITY.md |
| Audit Trail (Task 23) | Complete | **Implemented in fork — unverified in canonical repo** | SECURITY.md still describes Redis stream approach |
| Security Controls | Partially Hardened | **Partially Hardened — worse than reported** | Multiple claimed completions contradicted by SECURITY.md |
| Test Coverage | Partial | **Partial** | Consistent with report |
| Deployment Readiness | Staging-Ready | **Development/Baseline — not staging-ready** | Dual architecture, SECURITY.md gaps suggest more work needed |
| Frontend/Backend Contract | Unvalidated | **Unvalidated** | Consistent with report |
| CI/CD Pipeline | Structured | **Scaffolded — gates not fully enforced** | ci.yml at repo root, not in .github/workflows/; scanning gaps unresolved |

---

## 6. Confirmed Positive Findings

Despite the discrepancies, several report claims are confirmed by the publicly accessible repo:

- The modular monolith architectural direction is clearly documented and actively pursued via a comprehensive V2 execution manifest.
- The V2 Docker Compose target (`docker-compose.v2.yml`) and ACA production stack (`docker-compose.aca.yml`) are present, confirming Azure deployment intent.
- POPIA pseudonymisation (pseudonym_id isolation from LLM providers) is confirmed in both SECURITY.md and the README.
- The RLHF pipeline, multilingual support (English, isiZulu, Afrikaans, isiXhosa), and PWA capability are confirmed in CHANGELOG and README.
- `bicep/` and `k8s/` directories are present, confirming IaC posture.
- MkDocs documentation scaffolding is confirmed.
- Pre-commit hooks (`.pre-commit-config.yaml`) are present.
- The Grafana dashboard provisioning directory is confirmed present.
- Inference service isolation from the public internet is confirmed in CHANGELOG and SECURITY.md.

---

## 7. New Findings Not in the Original Report

The following observations emerged from direct repo inspection that the existing report does not address:

**7.1 Committed AI Session Artifacts**  
The repository contains a `mnt/user-data/outputs/eduboost` directory path in the root file tree. This is consistent with the output path used by AI coding sessions. Committing session output directories to a production repository is a hygiene concern that should be resolved via `.gitignore` updates and a git history purge before any public or regulatory review.

**7.2 Gemini-Code File as Architectural North Star**  
The existence of `gemini-code-1777601244294.md` as the "active architectural north star" (per AGENT_INSTRUCTIONS_V2.md) is architecturally significant and not acknowledged in the existing report. The V2 migration is being driven by an AI agent execution manifest. This is an unconventional but viable approach, with the caveat that it creates reliance on an auto-generated file with a non-descriptive name as a critical governance document.

**7.3 CI Pipeline File Location**  
The report references `.github/workflows/ci-cd.yml` as the canonical pipeline. The repo file tree shows `ci.yml` at the root level. Root-level CI files are not auto-detected by GitHub Actions. Whether `.github/workflows/` also contains the workflow could not be verified, but the presence of a root-level `ci.yml` warrants explicit confirmation.

**7.4 Multiple Docker Compose Files**  
Four Docker Compose files are present (`docker-compose.yml`, `docker-compose.v2.yml`, `docker-compose.aca.yml`, `docker-compose.prod.yml`). The report does not address configuration drift risk between these files or establish a clear environment-to-file mapping.

**7.5 `scratch/` Directory**  
A `scratch/` directory is present in the root. This suggests experimental or throwaway code has been committed. This should be reviewed and either removed or formally incorporated before any public or production release.

---

## 8. Risk Register — Additions to Original Report

| Risk ID | Description | Likelihood | Impact |
|---|---|---|---|
| R-NEW-001 | Canonical repo (NkgoloL) significantly behind working fork — documentation inaccurate for any external reviewer or regulator | High | High |
| R-NEW-002 | SECURITY.md not updated to reflect V2 progress — creates compliance audit risk | High | High |
| R-NEW-003 | JWT expiry discrepancy (15 min vs 24 hrs) — if 24 hrs is live, session hijack window is very wide for children's data platform | Medium | Critical |
| R-NEW-004 | AI session artifacts committed to repo — potential for sensitive file leakage | Low | Medium |
| R-NEW-005 | root-level `ci.yml` may not be auto-detected by GitHub Actions — CI gates may not be enforced | Medium | Medium |
| R-NEW-006 | `scratch/` directory committed — unclear status of contents | Low | Low |
| R-NEW-007 | Gemini-code north star uses auto-generated filename — not linked from formal architecture docs, easy to overlook | Low | Medium |

*Risks R-001 through R-008 from the original report remain valid and are not repeated here.*

---

## 9. Recommendations

**Immediate (before any further development or deployment):**

1. **Merge the working fork into the canonical NkgoloL/Eduboost-V2 repo.** The 3-commit gap means the canonical public source of truth is materially behind the actual working state.

2. **Update SECURITY.md to reflect actual implementation state.** Every item listed as "In Progress" or "Planned" that has been completed in the working fork must be updated with commit references. This is a POPIA §8 accountability concern.

3. **Resolve the JWT expiry discrepancy.** Confirm which value is live. A 24-hour token expiry without refresh token rotation is a material security gap for a platform handling children's data.

4. **Clean the repository of committed session artifacts.** Add `mnt/` to `.gitignore` and purge the path from git history using `git filter-repo`.

5. **Verify CI pipeline file placement.** Confirm `.github/workflows/` contains the canonical workflow and the root `ci.yml` is accounted for.

**Short-term:**

6. **Complete the V1 deletion.** Set a dated deadline for retiring `fourth_estate.py`, `judiciary.py`, `orchestrator.py`, and all V1 router files. Track this in the roadmap.

7. **Confirm the audit trail mechanism in production.** If `audit_repository.py` and migration 0006 are live, remove all Redis stream audit references from SECURITY.md and README.

8. **Rename the gemini-code north star.** `gemini-code-1777601244294.md` → `V2_ARCHITECTURE_MANIFEST.md` and link it from README under an "Architecture" section.

9. **Remove or formalise the `scratch/` directory.** If contents are useful, move them to a `docs/` or `audits/` subdirectory with appropriate context.

---

## 10. Conclusion

EduBoost SA V2 demonstrates genuine architectural ambition and a sophisticated understanding of POPIA compliance requirements. The modular monolith direction, pseudonymisation strategy, and audit trail design are sound at the conceptual level — and the working fork appears to have made real progress that the canonical repo has not yet captured.

The core problem is a documentation and synchronisation gap: the public canonical repository and its committed documentation (SECURITY.md, README) describe a state that is materially inconsistent with the claims made in the existing technical report. For any project handling children's personal data, this inconsistency carries regulatory weight — a POPIA information regulator reviewing the public repository would find documented gaps that the project believes are closed.

The path forward is clear: merge the working fork, update all documentation to reflect verified committed state, and ensure the canonical repository is the single source of truth before any production deployment, external review, or stakeholder demonstration.

---

*End of Comparative Audit Report — EduBoost SA V2 — 4 May 2026*
