# Production Readiness Baseline Boundary Contract

**Date**: 2026-06-12  
**Status**: Active  
**Purpose**: Documents what is and isn't included in the production readiness baseline

---

## Introduction

This contract defines the boundaries of the production readiness baseline achieved in Phase 10. It serves as a reference for what functionality is considered "production-ready" versus what requires further work.

---

## What's Included in Baseline

### Core Platform

| Component | Status | Notes |
|-----------|--------|-------|
| User authentication | ✅ | JWT-based with refresh tokens |
| Learner management | ✅ | CRUD, progress tracking |
| Adaptive diagnostics | ✅ | IRT-powered item bank (200+ items) |
| AI lesson generation | ✅ | Groq + Anthropic fallback |
| Consent management | ✅ | POPIA-compliant |
| Audit logging | ✅ | Append-only with HMAC |
| Payment processing | ✅ | Stripe integration |

### Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| API (FastAPI) | ✅ | /health, /ready, /metrics |
| Database (PostgreSQL) | ✅ | Migrations tested from empty |
| Cache (Redis) | ✅ | Sessions + rate limiting |
| Container (Docker) | ✅ | Non-root user |
| CI/CD | ✅ | GitHub Actions |
| Observability | ✅ | Grafana + Sentry |

### Security

| Component | Status | Notes |
|-----------|--------|-------|
| TLS termination | ✅ | Via Azure App Gateway / Nginx |
| CORS configuration | ✅ | Explicit origins only |
| CSP headers | ✅ | Nonce-based in production |
| HSTS | ✅ | Production only |
| Rate limiting | ✅ | Per-endpoint configuration |
| Secret management | ✅ | Azure Key Vault |

---

## What's NOT Included in Baseline

### Content

| Component | Status | Notes |
|-----------|--------|-------|
| Offline mode | ❌ | P2 — future roadmap |
| Voice input | ❌ | P2 — future roadmap |
| Mobile app | ❌ | Web-only at launch |
| Advanced analytics | ❌ | Basic dashboards only |

### Features

| Component | Status | Notes |
|-----------|--------|-------|
| School management console | ❌ | Basic teacher view only |
| Bulk import/export | ❌ | Manual CSV only |
| White-label | ❌ | Single brand |
| API for third-parties | ❌ | Internal use only |

### Advanced

| Component | Status | Notes |
|-----------|--------|-------|
| Multi-tenancy | ❌ | Single-tenant architecture |
| Real-time collaboration | ❌ | Not in scope |
| Advanced AI (LLM fine-tuning) | ❌ | Using pre-trained models only |

---

## Boundary Rules

### What's Allowed Under Baseline

- Bug fixes within existing components
- Security patches
- Performance optimizations
- Documentation updates
- Adding new CAPS topics to existing subjects
- Adding new subjects (Mathematics, Language only)

### What Requires Baseline Extension

- New user-facing features beyond current scope
- Architectural changes (database, auth, API)
- Third-party integrations not listed
- Changes to core data models

---

## Extension Process

To extend the baseline:

1. Write ADR explaining the change
2. Get approval from Engineering Lead
3. Update this document
4. Update test coverage
5. Document in release notes

---

## References

- ADR-019: Roadmap After Production Readiness Baseline
- Post-Baseline Architecture Contract: `docs/roadmap/post_baseline_roadmap_architecture_contract.md`
- Production Readiness Checklist: `docs/backlog/production_readiness/20_final_release-blocker_checklist.md`