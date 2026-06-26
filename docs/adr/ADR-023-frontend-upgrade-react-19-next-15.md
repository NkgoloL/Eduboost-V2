---
title: "ADR-023: Frontend Upgrade - React 19 + Next 15"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-023: Frontend Upgrade - React 19 + Next 15

## Status
Accepted

## Context
Based on frontend spike results, we need to upgrade the frontend stack while maintaining stability and deployment reliability. The spike evaluated React 19 + Next 15 compatibility, bundle feasibility, and PPR viability.

### Spike Results Summary
- **FE-SPIKE-001**: React 19 + Next 15 ✅ Complete - Proceed with upgrade path
- **FE-SPIKE-002**: Bundle feasibility ✅ Complete - Keep bundle budget checks active  
- **FE-SPIKE-003**: PPR + deployment viability ✅ Complete / **DEFER** - Keep PPR disabled

## Decision
Proceed with controlled frontend upgrade to React 19 and Next 15 with explicit rollback safeguards and deployment discipline.

### Upgrade Path
1. **React 19 + Next 15**: Accepted and approved for production upgrade
2. **PPR (Partial Prerendering)**: Deferred until stable Next support exists
3. **Broad dependency upgrades**: Still avoided unless tied to RC gate/spike

### Required Safeguards
- Multi-lockfile warning resolution
- Prevention/cleanup of root-owned .next artifacts  
- Docker/runtime build discipline codification
- Bundle-size monitoring after dependency-heavy PRs
- Environment validation and error monitoring

## Consequences

### Positive
- **Modern React features**: Access to React 19 improvements and Next 15 optimizations
- **Performance benefits**: Improved build times and runtime performance
- **Future-proofing**: Current stack alignment with ecosystem standards
- **Controlled upgrade**: Spike-validated path with rollback capabilities

### Negative  
- **Deployment complexity**: Requires careful Docker build artifact management
- **Dependency management**: Multi-lockfile coordination needed
- **Monitoring overhead**: Bundle size and error monitoring must be maintained
- **PPR limitation**: Cannot leverage PPR benefits until future stable release

### Implementation Requirements
- FE-PR-001: ADRs, rollback plan, backlog metadata (Current)
- FE-PR-002: Docker/runtime, pnpm discipline, env validation, error monitoring, .next cleanup, bundle guardrails (Next)

### Rollback Strategy
- Version-pinned Docker images for previous stable state
- Database-independent frontend rollback capability
- Bundle baseline monitoring for regression detection
- Environment-specific rollback triggers

## Related Decisions
- [ADR-0006](0006-nextjs-frontend.md) - Next.js Frontend (original)
- [ADR-003](0003-llm-provider-abstraction.md) - LLM Provider Abstraction (dependency management patterns)
- [ADR-012](ADR-012-ci-cd-infrastructure-deployment.md) - CI/CD Infrastructure Deployment

## Implementation Tracking
- **FE-PR-001**: ADRs, rollback plan, backlog metadata - IN PROGRESS
- **FE-PR-002**: Docker/runtime, pnpm discipline, env validation, error monitoring, .next cleanup, bundle guardrails - PENDING
