# EduBoost V2 Agent Instructions — "The High-Assurance Mandate"

## 1. Core Mission
You are an expert AI software engineer tasked with maintaining and extending the EduBoost SA V2 platform. This is a modular monolith designed for South African primary education, with strict requirements for POPIA compliance, pedagogical accuracy (CAPS alignment), and operational reliability.

## 2. Architectural Principles (Modular Monolith)
- **Domain Isolation**: All business logic must live within `app/modules/`.
- **Bounded Contexts**: Modules must not import from each other directly if it creates circular dependencies. Use shared kernel `app/core/` for common utilities.
- **Persistence**: Use the repository pattern (`app/repositories/`). Services should NOT use `AsyncSession` to run raw SQL; they must use repository methods.
- **Async First**: All I/O (Database, Redis, LLM, HTTP) must be asynchronous. Use `await`.

## 3. Mandatory Development Workflow
### TDD Loop
1.  **Write Failing Test**: Create a test in `tests/unit/` or `tests/integration/` that covers the new feature or bug fix.
2.  **Implement**: Write the minimum code necessary to pass the test.
3.  **Refactor**: Clean up the implementation while keeping tests green.
4.  **POPIA Sweep**: Before committing, run `python scripts/popia_sweep.py --fail-on-issues`.

### Import Boundaries
- Enforcement is handled by `import-linter`.
- Run `lint-imports` (via `Makefile` or `pytest`) to ensure no boundary violations occur (e.g., API layer importing from repositories directly).

## 4. Background Tasks (arq)
- We use `arq` (Async Redis Queue) for all background work (backups, consent renewal, lesson generation).
- Do NOT use Celery or RabbitMQ.
- Ensure all jobs are registered in the worker entrypoint and have proper error handling.

## 5. Security & Compliance (POPIA)
- **PII Isolation**: Never send real learner names or IDs to LLM providers. Use `pseudonym_id`.
- **Consent Gates**: All learner-facing endpoints MUST be protected by the `require_consent` dependency.
- **Audit Trail**: Every PII access or consent change MUST be recorded in the `audit_events` table via the `AuditRepository`.

## 6. Observability
- Instrument new features with Prometheus metrics in `app/core/metrics.py`.
- Ensure all logs are structured (JSON) and include `request_id`.

## 7. Operational Discipline
- **No Silent Failures**: Always raise specific exceptions from `app/core/exceptions.py`.
- **Reproducible Deps**: Update `requirements/base.in` and run `pip-compile` to lock dependencies.
- **Stable Docs**: Keep `docs/architecture/ARCHITECTURE.md` as the source of truth for architectural decisions.