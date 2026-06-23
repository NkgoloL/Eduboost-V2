---
title: "ADR-024 — Frontend Rollback Plan (React 19 + Next 15)"
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
# ADR-024 — Frontend Rollback Plan (React 19 + Next 15)

```text
Status: Accepted (Contingency Plan)
Date: 2026-05-28
Owner: Frontend Lead
RC Gate: RC1 -> RC2
Blocks: FE-PR-001 · FE-PR-002 · FE-PR-003
Reviewers: DevOps Lead, Product Owner, POPIA Compliance Officer
Evidence: FE-SPIKE-001..003, FE-PR-002 runtime verification, monitoring dashboard
```

## Context

The React 19 + Next 15 upgrade must remain reversible at all times. This ADR codifies the triggers, rollout/rollback mechanics, and communication plan so production stability is protected even if the upgrade introduces regressions.

## Rollback Triggers

### Critical (Immediate rollback)

- Frontend build failures in production pipeline.
- Runtime errors > 5% in error monitoring (synthetic data only).
- Performance regression > 2× page load or bundle size baseline.
- Authentication failures preventing user login/session renewal.
- API integration failures between frontend and backend contracts.

### Warning (Monitor + evaluate rollback)

- Bundle size increase > 20% vs FE-SPIKE-002 baseline.
- Client memory usage > 50% increase.
- New WCAG violations introduced.
- Browser compatibility issues across supported browsers.

## Rollback Procedures

### Immediate rollback (Critical triggers)

1. **Traffic routing** — point ingress to previous stable deployment:

   ```bash
   kubectl patch service frontend-service -p '{"spec":{"selector":{"version":"stable"}}}'
   ```

2. **Assets** — promote the prior Docker image:

   ```bash
   docker pull eduboost/frontend:stable-v1
   docker tag eduboost/frontend:stable-v1 eduboost/frontend:latest
   docker push eduboost/frontend:latest
   ```

3. **Verification** — run health checks:

   ```bash
   curl -f https://app.eduboost.sa/health
   curl -f https://app.eduboost.sa/api/health
   ```
4. **Database independence** — no migrations are required; JWT sessions remain valid.

### Gradual rollback (Warning triggers)

1. Disable problematic features via feature flags:

   ```typescript
   const config = {
     features: {
       newReactComponents: false,
       next15Features: false,
       experimentalFeatures: false,
     },
   };
   ```
2. Route 10% of traffic back to the previous version, monitor error/perf metrics, and increase rollback percentage if degradation persists.

## Recovery Mechanisms

- **Automated** — monitoring every 30 seconds, auto-rollback when thresholds exceed limits, on-call alerts.
- **Manual** — documented playbook (`scripts/test-frontend-rollback.sh`), emergency contacts, stakeholder comms templates.
- **Data protection** — frontend is stateless; backend contracts unchanged; JWT sessions survive rollbacks.

## Rollback Testing

```bash
./scripts/test-frontend-rollback.sh
# Validate prior image still passes tests
docker run --rm eduboost/frontend:stable-v1 npm test
```

Monitoring snippets:
```typescript
const errorThreshold = 0.05; // 5%
const performanceThreshold = 2000; // 2s
if (errorRate > errorThreshold || loadTime > performanceThreshold) {
  triggerRollback();
}
```

## Communication Plan

- **Internal:** Slack `#frontend-deployments`, email `eng-team@eduboost.sa`, PagerDuty escalation.
- **External:** Status page updates, in-app notifications if user-facing impact, support briefing.

## Post-Rollback Actions

1. Run root-cause analysis, impact assessment, and lessons learned.
2. Resolve issues, add tests, and schedule a staged re-deploy.
3. Update release evidence with rollback timestamps and approvals.

## Related Documents

- ADR-023 — Frontend upgrade decision.
- ADR-012 — CI/CD infrastructure deployment.
- Frontend monitoring dashboard: <https://monitoring.eduboost.sa/frontend>

## Approval

| Role | Status | Date |
| --- | --- | --- |
| Frontend Lead | Approved | 2026-05-28 |
| DevOps Lead | Approved | 2026-05-28 |
| Product Owner | Approved | 2026-05-28 |
| POPIA Compliance Officer | Approved | 2026-05-28 |
