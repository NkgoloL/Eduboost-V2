# EduBoost SA — System Status Roadmap

**Last Updated:** May 2, 2026  
**Status:** 🟢 Active — V2 Architecture Migration Complete  

This roadmap outlines the core functionalities and capabilities of the EduBoost SA system. Each entry below has a corresponding detail block in the [System Status Report](../reports/System_Status_Report_2.md) for current implementation details and status checks.

## System Capabilities

### 1. Authentication & Security
- [x] Implement JWT-based authentication for Learners and Guardians.
- [x] Enforce POPIA-compliant data deletion mechanisms.
- [x] Secure password hashing and token lifecycle management.

### 2. Constitutional AI & Judiciary Pipeline
- [x] Validate and sanitize all LLM responses against educational guidelines.
- [x] Implement PII scrubbing to prevent data leakage.
- [x] Apply Subject-specific pedagogical rules (Maths vs Language).

### 3. Adaptive Diagnostics (IRT Engine)
- [x] Deploy stateful Item Response Theory assessment sessions.
- [x] Generate baseline capability reports from initial evaluations.
- [x] Real-time gap detection and reporting.

### 4. Personalised Study Plan Generation
- [x] Orchestrate weekly plan generation using OpenAI/Anthropic APIs.
- [x] Map diagnostic gaps to specific learning objectives.
- [x] Celery-driven background processing for automated plan renewal.

### 5. Interactive Learning & Execution
- [x] Deliver dynamic lesson content with interactive components.
- [x] Track Time-on-Task and granular mastery progress.
- [x] Implement robust offline caching and Service Worker synchronization.

### 6. Gamification Engine
- [x] Calculate and award XP for lesson completion.
- [x] Track consecutive daily activity streaks.
- [x] Unlock level progression and distribute achievement badges.

### 7. Parent Portal & Guardian Reporting
- [x] Provide high-level progress dashboards for guardians.
- [x] Support granular consent management and data requests.
- [x] Generate comprehensive parent-friendly performance reports.

### 8. Auditing & Logging (Fourth Estate) — V2 Modernized
- [x] Immutable event tracking for PII, Consent, and System mutations.
- [x] **Migrated from RabbitMQ to PostgreSQL-backed async audit trail** (`core/audit.py`)
- [x] Simplified audit enforcement with FastAPI dependencies (no middleware bloat)
- [x] Structured async audit writes via `BackgroundTasks` (non-blocking)

### 9. Infrastructure & Tooling
- [x] Post-startup Dummy Data Generator for demo/dev environments.
- [x] Alembic-driven database migrations and schema drift detection.
- [x] Prometheus metrics and Grafana observability stack.
- [x] CI/CD and Release Automation workflows.

### 10. V2 Modular Monolith Pivot — ✅ COMPLETED
- [x] Establish modular structure: `app/modules/`, `app/core/`, `app/repositories/`, `app/models/`
- [x] Migrate all business logic from V1 domain/services into V2 module architecture
- [x] Replace broker-first audit with V2 PostgreSQL append-only audit in `core/audit.py`
- [x] Replace Celery with `arq` (async Redis queue) for single-node simplicity
- [x] Align deployment to V2 single-node modular monolith constraint
- [x] **Delete all V1 code** — no active clients, zero migration obligation
- [x] Reorganize CI/CD to `.github/workflows/` standard location
- [x] Update all tracking documents with completion status
