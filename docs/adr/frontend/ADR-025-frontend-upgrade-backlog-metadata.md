---
title: "ADR-025 — Frontend Upgrade Backlog Metadata"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-025 — Frontend Upgrade Backlog Metadata

```text
Status: Active
Date: 2026-05-28
Owner: Frontend Team Lead
RC Gate: RC1 → RC4 (spans the full upgrade)
Blocks: FE-PR-001 · FE-PR-002 · FE-PR-003 · FE-PR-004 · FE-P1-021 · FE-NS-004
Reviewers: DevOps Lead, Product Owner
Evidence: FE-SPIKE-001..003, ADR-023, ADR-024, package.json diff
```

## Context

The React 19 + Next 15 upgrade requires structured backlog metadata so dependencies, risks, and guardrails remain visible through RC1–RC4. This ADR tracks the upgrade scope, risk profile, implementation tasks, and monitoring requirements.

## Upgrade Scope

### Current State Analysis

- React: `18.3.1` → `19.x`
- Next.js: `15.5.18` (already on target)
- Node engine: `>=20.0.0`
- Package manager: npm (pnpm migration introduced in FE-PR-002)
- Build tool: Next.js (no change)

### Dependency Inventory

#### Core dependencies

```json
{
  "react": "18.3.1 → 19.x",
  "react-dom": "18.3.1 → 19.x",
  "@types/react": "18.3.1 → 19.x"
}
```

#### Next.js stack

```json
{
  "next": "15.5.18",
  "eslint-config-next": "15.5.18"
}
```

#### UI libraries (validate compatibility)

```json
{
  "@radix-ui/react-avatar": "^1.1.11",
  "@radix-ui/react-checkbox": "^1.3.3",
  "@radix-ui/react-dialog": "^1.1.15",
  "@radix-ui/react-dropdown-menu": "^2.1.16",
  "@radix-ui/react-label": "^2.1.8",
  "@radix-ui/react-select": "^2.2.6",
  "@radix-ui/react-separator": "^1.1.8",
  "@radix-ui/react-slot": "^1.2.4",
  "@radix-ui/react-tabs": "^1.1.13",
  "@radix-ui/react-tooltip": "^1.2.8"
}
```

#### Testing libraries

```json
{
  "@testing-library/react": "^15.0.7",
  "@testing-library/jest-dom": "^6.4.5",
  "vitest": "4.1.7",
  "@vitest/coverage-v8": "4.1.7"
}
```

## Risk Assessment

**High risk:** React 19 breaking changes (RSC/Suspense), type definition shifts, testing-library compatibility, Next build behavior.

**Medium risk:** Radix UI compatibility, HMR changes, bundle/perf drift, accessibility regressions.

**Low risk:** Tailwind CSS, Zustand/SWR, React Hook Form (monitor but expect minimal issues).

## Implementation Tasks

### Phase 1 — Preparation (FE-PR-001)

- [x] ADR-023 upgrade decision
- [x] ADR-024 rollback plan
- [x] ADR-025 backlog metadata
- [ ] Dependency compatibility validation
- [ ] Test suite compatibility assessment
- [ ] Build process validation

### Phase 2 — Infrastructure (FE-PR-002)

- [ ] Docker build optimization
- [ ] pnpm migration
- [ ] Environment validation enhancements
- [ ] Error monitoring setup
- [ ] `.next` cleanup automation
- [ ] Bundle size monitoring
- [ ] Multi-lockfile resolution

### Phase 3 — Core Upgrade (FE-PR-003)

- [ ] React 19 upgrade
- [ ] TypeScript updates
- [ ] Breaking-change mitigation
- [ ] Component compatibility fixes
- [ ] Test suite updates

### Phase 4 — Validation (FE-PR-004)

- [ ] End-to-end testing
- [ ] Performance benchmarking
- [ ] Accessibility testing
- [ ] Security validation
- [ ] Production deployment testing

## Monitoring & Guardrails

### Pre-deployment checks

```bash
pnpm run build && pnpm run analyze
pnpm run type-check
pnpm run test:coverage
pnpm run env-check
```

### Post-deployment monitoring

```typescript
const errorThreshold = 0.02;
const performanceThreshold = 1500;
const bundleSizeThreshold = 500000;
const a11yScoreThreshold = 95;
```

### Rollback triggers

- Error rate > 5%
- Performance regression > 2× baseline
- Bundle size increase > 20%
- Accessibility score < 90
- Browser compatibility issues

## Dependencies & Blockers

- **External:** React 19 GA support, Next.js docs, Vercel deployment compatibility, Testing Library updates.
- **Internal:** Backend API contract stability, CI/CD updates, monitoring stack readiness, security review approvals.
- **Timeline:** React 19 target Q2 2026; production deployment Q3 2026 with two-week testing window.

## Success Criteria

- Zero critical prod errors, equal or better performance, bundle within limits, tests green, accessibility maintained.
- No user-impacting issues, dev velocity preserved, security posture intact, scalability unaffected.
- Deployment smooth, monitoring effective, rollback validated, team trained.

## Related Documents

- ADR-023 — Frontend Upgrade (React 19 + Next 15)
- ADR-024 — Frontend Rollback Plan
- Frontend spike results (see `docs/frontend/spikes/*.md`)
- `app/frontend/package.json` (current dependency manifest)

## Maintenance

- **Owner:** Frontend Team Lead
- **Review frequency:** Weekly during upgrade
- **Update cadence:** As implementation tasks complete
- **Archive date:** 30 days post-upgrade completion
