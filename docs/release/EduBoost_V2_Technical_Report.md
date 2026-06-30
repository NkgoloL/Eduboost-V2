# EduBoost SA V2 — Comprehensive Technical Report

**Report Date:** 2 May 2026
**Repository:** [NkgoloL/Eduboost-V2](https://github.com/NkgoloL/Eduboost-V2)
**Current Version:** `0.2.0-rc1` (Beta)
**Report Author:** Independent Technical Assessment

---

## Executive Summary

EduBoost SA is an AI-powered adaptive learning platform targeting South African learners in Grades R–7, built with a strong compliance focus (POPIA), CAPS curriculum alignment, and multilingual support. The project is currently in an active architectural migration from a legacy five-pillar monolith to a cleaner V2 modular monolith.

The repository demonstrates **high engineering ambition and thoughtful compliance design**, but it is currently in a state of **significant structural tension**: two parallel architectures coexist in the same codebase without a clear deprecation timeline or feature parity map. Documentation is excellent in breadth but inconsistent in depth. The CI/CD pipeline is sophisticated but contains a critical misplacement issue. Several dependency and security hygiene items require immediate attention before any production release.

**Overall Assessment: 🟡 In Transition — Solid Foundation, Needs Structural Resolution**

---

## 1. Repository Overview

### 1.1 Technology Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.111 + Python 3.11 |
| Frontend | Next.js 14 (App Router) + TypeScript |
| Database | PostgreSQL 16 (async via asyncpg + SQLAlchemy 2.0) |
| Migrations | Alembic |
| Cache | Redis 7 |
| Background Tasks | Celery 5.4 + Redis (legacy path); Celery/RabbitMQ (legacy) |
| LLM Providers | Anthropic Claude, Groq (primary), OpenAI-compatible |
| ML / IRT Engine | scikit-learn, NumPy, SciPy |
| Inference Service | torch + transformers (decoupled sidecar) |
| Observability | Prometheus + Grafana + Loki + Promtail |
| IaC | Azure Bicep (Azure Container Apps target) |
| Containerisation | Docker / Docker Compose |
| Orchestration | Kubernetes manifests + ACA compose file |
| CI/CD | GitHub Actions (ci.yml) |
| E2E Testing | Playwright |
| Documentation | MkDocs + mkdocstrings |

### 1.2 Language Breakdown

- Python: **81.8%**
- JavaScript: **9.5%**
- PLpgSQL: **5.7%**
- TypeScript: **1.3%**
- Shell: **0.9%**
- Bicep: **0.8%**

### 1.3 Commit Activity

The repository has only **3 commits** on the `master` branch, with the entire codebase pushed in a single large batch. This is a hallmark of AI-agent-driven development (confirmed by the presence of `AGENT_INSTRUCTIONS.md` and `AGENT_INSTRUCTIONS_V2.md`). There is no incremental commit history, which has meaningful implications for code review, bisecting bugs, and auditability.

---

## 2. Architecture Assessment

### 2.1 Dual-Architecture State (Critical Finding)

The repository currently maintains **two active architectures simultaneously**:

**Legacy Path (Five-Pillar Architecture):**
- `app/api/` — original routers, services, models
- `app/api/main.py` — FastAPI entrypoint
- `docker-compose.yml` — 9-service legacy stack
- Includes Celery, RabbitMQ, `fourth_estate.py` (RabbitMQ audit trail)

**V2 Target (Modular Monolith):**
- `app/api_v2.py` — new entrypoint
- `app/api_v2_routers/` — V2 router surface
- `app/repositories/` — repository pattern for DB access
- `docker-compose.v2.yml` — lean 4-service stack (no Celery/RabbitMQ)

The README acknowledges this explicitly, calling the legacy path "compatibility mode." However, there is **no documented feature parity matrix** between V1 and V2 endpoints, **no deprecation timeline**, and **no migration guide** for dependent clients. The `AGENT_INSTRUCTIONS_V2.md` references `gemini-code-1777601244294.md` as the "architectural north star," but this is a raw Gemini AI output file committed directly to the repository root — an unusual and risky source of architectural truth.

### 2.2 The Five-Pillar Pattern

The legacy architecture uses named conceptual pillars:

| Pillar | Module | Responsibility |
|---|---|---|
| 2 (Executive) | `orchestrator.py` | Workflow orchestration |
| 3 (Judiciary) | `judiciary.py` | Constitutional policy enforcement |
| 4 (Fourth Estate) | `fourth_estate.py` | RabbitMQ-backed audit trail |
| 5 (Ether) | `profiler.py` | Psychological archetype profiling |

The V2 target discards Celery and RabbitMQ in favour of synchronous repository calls. The fate of Pillar 4's durability guarantees under V2 is **not clearly defined** in accessible documentation.

### 2.3 V2 Docker Compose Analysis

The `docker-compose.v2.yml` is lean and correct (Postgres + Redis + API + Docs). However:

- The `docs` service **reuses the same `Dockerfile.v2`** as the API, only overriding the command to `mkdocs serve`. This means the full application image is built twice, and the docs service carries unnecessary application dependencies. A dedicated lightweight Dockerfile for docs would reduce build time and image size.
- The `redis` service has **no healthcheck** defined, unlike the postgres service. This can cause race conditions on startup.
- **No volume is defined for Redis**, meaning cache data is lost on container restart in development, which may mask caching bugs.

---

## 3. CI/CD Pipeline Assessment

### 3.1 Pipeline Structure

The `ci.yml` is well-structured and demonstrates mature thinking:

- Lint & type-check (ruff + mypy)
- Unit tests with 80% coverage threshold
- Integration tests (with real Postgres + Redis service containers)
- V2 smoke test (import validation only)
- Frontend build + tests
- Schema drift gate (`alembic check`)
- POPIA compliance test suite
- Docker image Trivy security scan
- Production promotion gate (release-triggered, requires all prior jobs)

### 3.2 Critical Issue: `ci.yml` Location

**The `ci.yml` file is placed at the repository root, not in `.github/workflows/`.** GitHub Actions only automatically discovers workflow files inside `.github/workflows/`. This means the entire CI/CD pipeline is currently **not executing on any push or pull request**. The CHANGELOG references a `.github/workflows/ci-cd.yml` as the canonical pipeline, suggesting this root-level `ci.yml` is either a draft or was misplaced. The `.github/` directory exists in the repo but its contents were not verifiable — this should be audited immediately.

### 3.3 Other CI Observations

- The `ENCRYPTION_KEY` environment variable is **declared twice** in the integration-tests job with the same value, indicating a copy-paste oversight.
- The `v2-smoke` job only validates that modules can be imported (`importlib.import_module`), not that any endpoint actually responds correctly. This is a very shallow smoke test for a production gate.
- The production promotion job deploys to Kubernetes (`kubectl set image`) but the infrastructure target is Azure Container Apps (Bicep). This inconsistency suggests the deployment step was not updated to match the chosen production platform.
- `mypy --strict-optional` is used without `--strict`, which means many strict-mode checks (e.g., untyped function bodies) are silently skipped.

---

## 4. Dependency Management

### 4.1 Requirements Structure

The project correctly separates concerns across:
- `requirements.txt` — core API dependencies
- `requirements-ml.txt` — heavy ML/inference dependencies (torch, transformers)

This is a good pattern that keeps the main API container small (~500MB as noted in the CHANGELOG).

### 4.2 Version Pinning

All dependencies in `requirements.txt` are **hard-pinned** (e.g., `fastapi==0.111.0`). While this ensures reproducibility, it also means:

- Security patches in upstream packages are not automatically applied.
- There is no mechanism (e.g., Dependabot, Renovate) visible in the repository to automate update PRs.
- `anthropic==0.40.0` is noted in comments as having been updated from `0.28.0`, but the current latest stable Anthropic SDK is significantly newer, meaning Claude 4 model support may be incomplete.

### 4.3 Mixed Package Files

Both `requirements.txt` (Python) and `package.json` / `package-lock.json` (Node) exist at the repository root, in addition to what is likely another `package.json` inside `app/frontend/`. This creates potential confusion about which Node configuration governs the frontend build. The root-level `package.json` appears to be for Playwright E2E tests, but this is not documented.

### 4.4 Missing Lock File for Python

There is no `requirements.lock`, `poetry.lock`, or `pdm.lock`. Combined with pip's lack of a native lock file, builds between environments may diverge despite pinned versions (transitive dependencies are not locked). Using `pip-compile` or migrating to Poetry/uv would resolve this.

---

## 5. Security Assessment

### 5.1 Strengths

The project demonstrates strong security intent:

- **PII pseudonymisation:** Learner real UUIDs are never sent to LLM providers; a `pseudonym_id` is used exclusively.
- **Email storage:** SHA-256 hash + pgcrypto-encrypted ciphertext — never plaintext.
- **POPIA consent gating:** `ConsentService.require_active_consent()` documented as mandatory at all learner endpoints.
- **Right to erasure:** Soft-delete pattern with atomic consent revocation.
- **Annual consent renewal:** Enforced via `expires_at` column.
- **Input sanitisation:** `bleach` used for PII scrubbing; regex-based PII scrubbing in RLHF service.
- **Rate limiting:** `slowapi` included for API rate limiting.
- **Trivy image scanning:** Integrated in CI for CRITICAL/HIGH vulnerabilities.

### 5.2 Concerns

- **`JWT_SECRET` and `ENCRYPTION_KEY` hardcoded in CI test environment variables.** While using test-specific values is expected, these appear as plain strings in the workflow YAML file in the repository. If this YAML is ever used as a template and real secrets substituted without using GitHub Secrets, leakage is likely.
- **RabbitMQ default credentials** (`guest/guest`) are documented in the README for local development. These should be overridden even in development to build good habits and avoid accidental exposure.
- **The `gemini-code-1777601244294.md` file** is committed to the repo root. This AI-generated file likely contains architectural descriptions including potential infrastructure details, API surface designs, and possibly example secrets or configuration values that should not be in a public repository.
- **Azure Key Vault** (`azure-keyvault-secrets`) is listed as a dependency but labelled as "Medium-Term" in a comment. Until it is implemented, the primary secret delivery mechanism is `.env` files, which rely on operator discipline.
- **No SAST (Static Application Security Testing)** tool (e.g., Bandit for Python, Semgrep) is present in the CI pipeline beyond Trivy image scanning.

---

## 6. Testing Assessment

### 6.1 Test Structure

The test suite is well-organised:
- `tests/unit/` — unit tests
- `tests/integration/` — integration tests (with real DB)
- `tests/popia/` — dedicated POPIA compliance tests
- `tests/smoke/` — smoke tests for staging validation
- Playwright E2E tests at root level (`playwright.config.ts`)

### 6.2 Coverage & Quality Gaps

- The **80% coverage threshold** is reasonable but not currently verifiable since the CI pipeline may not be running (see §3.2). Without CI execution evidence, the actual coverage figure is unknown.
- The `v2-smoke` job in CI only tests that V2 modules import successfully, not that they function correctly. This gap means a V2 release could pass CI with broken endpoint logic.
- **No contract testing** (e.g., Pact) is present to validate that the frontend's API calls are compatible with the backend's response schemas. This matters significantly given the dual-API-surface situation.
- **No performance or load testing** is visible (e.g., Locust, k6). For a platform serving children at scale, understanding throughput limits for the IRT engine and LLM calls is important.
- The `factory-boy` and `faker` libraries are included (good for test data generation), but their usage patterns cannot be verified without source access.

---

## 7. Documentation Assessment

### 7.1 Strengths

- `README.md` is comprehensive, well-structured, and honest about the current dual-architecture state.
- `CHANGELOG.md` follows Keep a Changelog format and Semantic Versioning correctly.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` are all present — strong open-source hygiene.
- MkDocs + mkdocstrings is set up for auto-generated technical docs from Python docstrings.
- `AGENT_INSTRUCTIONS.md` and `AGENT_INSTRUCTIONS_V2.md` provide context for AI-assisted development workflows.
- `audits/` directory contains roadmaps and implementation reports.

### 7.2 Weaknesses

- **`gemini-code-1777601244294.md` is an AI session output file** committed to the root. Treating a raw AI conversation output as the canonical "architectural north star" (per `AGENT_INSTRUCTIONS_V2.md`) is fragile — it cannot be version-controlled, reviewed via PR, or diffed meaningfully. This information should be distilled into proper ADRs (Architecture Decision Records).
- **No API changelog or versioning strategy** is documented between V1 and V2 endpoints.
- **The `scratch/` directory** at the repository root is unexplained. Its presence alongside production code suggests it contains work-in-progress material that should not be in the main branch.
- **`mnt/user-data/outputs/eduboost/`** — a Claude artifact output path — is committed directly into the repository tree. This is almost certainly an accidental inclusion from an AI development session and should be removed and added to `.gitignore`.

---

## 8. Infrastructure & Deployment Assessment

### 8.1 Infrastructure as Code

The project targets Azure Container Apps (ACA) with Bicep IaC in the `bicep/` directory. This is a sensible, cost-effective choice for a startup-stage platform. The presence of `docker-compose.aca.yml` as a production validation stack is a good intermediate step.

### 8.2 Kubernetes Manifests

The `k8s/` directory contains Kubernetes manifests. However, the CI production promotion step deploys to Kubernetes, while the stated production target is Azure Container Apps. This discrepancy needs to be resolved — running both would result in duplicated infrastructure costs and operational complexity.

### 8.3 Observability

The Prometheus/Grafana/Loki stack is well-considered, with pre-built dashboards for:
- Learner Journey SLOs
- LLM Provider Health
- Constitutional Health (Judiciary approval rates)

This is production-grade observability for a beta product — a genuine strength.

---

## 9. Prioritised Recommendations

### 🔴 Critical — Address Before Any Production Traffic

**1. Fix CI/CD Pipeline Placement**
Move `ci.yml` to `.github/workflows/ci-cd.yml`. Verify whether a working pipeline already exists in `.github/workflows/` and reconcile. Without this, no automated quality gates are running.

**2. Remove Accidental Artifacts from Repository**
Remove the `mnt/user-data/outputs/` directory tree from the repository — this is an AI session artifact. Add `mnt/` to `.gitignore`. Also review `gemini-code-1777601244294.md` for any sensitive content before it remains in a public repository.

**3. Resolve V2 Smoke Test Shallowness**
Replace the import-only smoke test with actual endpoint health checks using an in-process `TestClient` (FastAPI's built-in `httpx` test client). At minimum, test `/health`, one authenticated endpoint, and the consent gate.

**4. Add SAST to CI**
Add `bandit` (Python security linter) and `semgrep` to the lint job. This catches common security anti-patterns (e.g., hardcoded secrets, SQL injection, insecure deserialization) that Trivy image scanning does not cover at the source level.

---

### 🟠 High Priority — Address Within 2 Sprints

**5. Establish a V2 Feature Parity Matrix**
Document exactly which V1 endpoints have been replicated in V2, which are planned, and which are being dropped. This is essential for planning the V1 deprecation and preventing regressions during migration.

**6. Replace `gemini-code-1777601244294.md` with Proper ADRs**
Extract the architectural decisions from this file into structured Architecture Decision Records (ADRs) using a standard format (e.g., `docs/adr/0001-v2-modular-monolith.md`). ADRs should be reviewed via PR like code.

**7. Add Python Dependency Lock File**
Adopt `uv` or `pip-tools` to generate a `requirements.lock` file that pins all transitive dependencies. This ensures reproducible builds across developer machines, CI, and production containers.

**8. Add Redis Healthcheck to docker-compose.v2.yml**
Add the same healthcheck pattern used for Postgres to the Redis service:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**9. Fix Duplicate `ENCRYPTION_KEY` in CI**
Remove the duplicated environment variable in the `integration-tests` job. Review all CI jobs for similar copy-paste issues.

**10. Clarify Kubernetes vs ACA Deployment Target**
Choose one deployment target for production (Azure Container Apps is the documented intent) and remove or clearly archive the conflicting Kubernetes production deployment step in `ci.yml`.

---

### 🟡 Medium Priority — Address in Next Major Milestone

**11. Migrate to Incremental Git Commits**
Even in AI-assisted development, commits should be atomic and meaningful. Establish a workflow where every completed "slice" (as defined in `AGENT_INSTRUCTIONS_V2.md`) results in a descriptive commit with a conventional commit message. This enables `git bisect`, cleaner PRs, and better audit trails.

**12. Implement API Contract Testing**
Add Pact or a similar contract testing tool to validate that the Next.js frontend's API client layer is compatible with the FastAPI response schemas for both V1 and V2 surfaces.

**13. Add Dependabot or Renovate**
Configure automated dependency update PRs in `.github/dependabot.yml` for both Python (pip) and Node (npm). This is especially important for security patch delivery given the current fully-pinned strategy.

**14. Separate the Docs Dockerfile**
Create a minimal `docker/Dockerfile.docs` that only installs MkDocs and mkdocstrings, rather than building the full API image just to serve documentation.

**15. Clean Up `scratch/` Directory**
Either move work-in-progress code into a feature branch, or if it contains useful reference material, document it and move it into `docs/`. The `scratch/` directory at repo root signals unfinished work and creates confusion for contributors.

**16. Upgrade anthropic SDK**
`anthropic==0.40.0` is behind current stable. Update to the latest version to ensure Claude 4 model families (including claude-opus-4 and claude-sonnet-4 strings) are fully supported.

**17. Add Load / Performance Tests**
Introduce a lightweight performance test suite using `locust` or `k6` targeting the IRT diagnostic engine and LLM lesson generation endpoints. LLM calls with Groq/Anthropic have variable latency that must be characterised before scaling.

---

### 🟢 Low Priority / Long-Term Improvements

**18. Type Safety Upgrade**
Upgrade mypy invocation from `--strict-optional` to `--strict` to enforce full type coverage including untyped function bodies. Address the resulting errors incrementally.

**19. Frontend TypeScript Coverage**
At 1.3% TypeScript, the frontend is predominantly JavaScript. Incrementally migrate `.js` files in `src/` to `.ts`/`.tsx` to improve type safety, IDE support, and refactoring confidence.

**20. Formalise the RLHF Pipeline**
The `RLHFService` for capturing lesson feedback is implemented but its feedback loop (how captured data improves model prompts or fine-tuning) is not documented. Define and document the full loop from feedback capture → dataset export → model improvement trigger.

**21. IRT Engine Validation**
The IRT (Item Response Theory) engine is a core educational differentiator. Add dedicated tests that validate its statistical correctness (e.g., known-answer calibration tests, ability estimation convergence tests) separate from integration tests.

**22. Consider OpenTelemetry**
The current observability stack (Prometheus metrics + Loki logs) is solid, but lacks distributed tracing across the API → LLM provider → inference service call chain. Adding OpenTelemetry traces would dramatically improve debugging of latency issues in production.

---

## 10. Summary Scorecard

| Area | Score | Notes |
|---|---|---|
| Architecture Design Intent | 🟢 Strong | Repository pattern, modular monolith, compliance-by-design |
| Architecture Current State | 🟡 Mixed | Dual-architecture tension, no deprecation timeline |
| CI/CD Pipeline Design | 🟢 Strong | Comprehensive jobs, good gate structure |
| CI/CD Pipeline Execution | 🔴 Broken | `ci.yml` misplaced — not running |
| Security Design | 🟢 Strong | POPIA, pseudonymisation, consent gating |
| Security Implementation | 🟡 Mixed | SAST missing, accidental artifacts in repo |
| Testing Strategy | 🟢 Strong | Good layering (unit/integration/POPIA/E2E) |
| Test Coverage Verifiability | 🔴 Unknown | CI not running; no badge or report visible |
| Documentation | 🟢 Strong | README, CHANGELOG, MkDocs, ADRs missing |
| Dependency Management | 🟡 Mixed | Pinned but no lock file, stale Anthropic SDK |
| Infrastructure Design | 🟢 Strong | ACA + Bicep, Kubernetes manifests, Grafana |
| Infrastructure Consistency | 🟡 Mixed | K8s vs ACA discrepancy in CI deploy step |
| Git Hygiene | 🔴 Poor | 3 commits, accidental artifacts, scratch dir |
| Observability | 🟢 Strong | Prometheus, Grafana, Loki, SLO dashboards |

---

## 11. Conclusion

EduBoost SA V2 is a technically ambitious project with genuine strengths in compliance architecture, observability, and feature breadth. The engineering decisions around POPIA compliance, pseudonymisation, and the IRT-based diagnostic engine are well-considered and appropriate for the target market.

The project's primary risk is not technical capability but **structural coherence**: two architectures coexist without a clear convergence plan, the CI/CD pipeline is likely not executing, and the repository's commit history obscures the true state of implementation. These issues must be resolved before the project can safely move from `0.2.0-rc1` to a production release.

The recommended immediate focus is: **fix CI/CD execution, remove accidental artifacts, define a V2 feature parity matrix, and establish incremental commit discipline.** With these resolved, the underlying engineering quality is high enough to support a confident production launch.

---

*Report generated via static analysis of publicly accessible repository files. Source code files within the `app/` directory tree could not be individually inspected due to GitHub robots.txt restrictions on tree-level pages. Findings are based on README, CHANGELOG, CI configuration, docker-compose files, requirements files, and agent instruction documents.*
