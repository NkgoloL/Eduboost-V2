# Post-Baseline Roadmap Architecture Contract

**Date**: 2026-06-12  
**Status**: Active  
**Purpose**: Documents architectural implications of the post-baseline roadmap

---

## Introduction

This document describes the architectural decisions and implications resulting from the post-baseline roadmap strategy defined in ADR-019.

---

## Architectural Implications

### 1. Release Cadence

**Decision**: Fortnightly release cycles

**Architecture Impact**:
- CI/CD pipeline must support frequent deployments
- Database migrations must be backward-compatible
- Feature flags required for gradual rollouts
- Rollback procedures must be documented and tested

### 2. Technical Debt Quota

**Decision**: 20% engineering capacity for debt reduction

**Architecture Impact**:
- Quarterly debt audits scheduled
- Refactoring budget explicitly planned per sprint
- Technical debt backlog visible in project management

### 3. Content Expansion (P1)

**Roadmap Item**: Expand beyond Mathematics and Language

**Architecture Impact**:

| Component | Implication |
|----------|-------------|
| Item Bank | Add new IRT item tables per subject |
| Lesson Generator | Subject-specific prompt templates |
| Diagnostics | Subject-specific assessment templates |
| CAPS Integration | Subject-specific topic mappings |

### 4. Mobile Experience (P1)

**Roadmap Item**: Improve mobile UX

**Architecture Impact**:

| Component | Implication |
|----------|-------------|
| Frontend | Responsive design enforcement |
| API | Consider GraphQL for mobile efficiency |
| Offline | Service Worker + IndexedDB for caching |
| Push Notifications | FCM integration |

### 5. Offline Mode (P2)

**Roadmap Item**: Allow offline learning

**Architecture Impact**:

| Component | Implication |
|----------|-------------|
| Database | SQLite on device for sync |
| Sync Engine | Conflict resolution strategy |
| Auth | Token refresh while offline |
| Content | Pre-downloadable lesson packages |

---

## Contract Obligations

The following architectural standards must be maintained:

1. **API Stability**: Backward compatibility for at least 2 major versions
2. **Database Migrations**: Always backward-compatible
3. **Feature Flags**: All new features behind flags until stable
4. **Observability**: All services emit standard metrics

---

## Review Schedule

| Item | Review Frequency | Owner |
|------|------------------|-------|
| API stability | Per release | Backend Lead |
| Database schema | Monthly | DBA |
| Feature flags | Weekly | DevOps |
| Technical debt | Quarterly | Engineering Lead |

---

## References

- ADR-019: Roadmap After Production Readiness Baseline
- Production Readiness Baseline Boundary Contract: `docs/roadmap/production_readiness_baseline_boundary_contract.md`