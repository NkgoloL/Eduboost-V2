---
title: "ADR-024: Frontend Rollback Plan"
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
# ADR-024: Frontend Rollback Plan

## Status
Approved (Contingency Plan)

## Context
Frontend upgrade to React 19 + Next 15 requires comprehensive rollback strategy to ensure production stability. This plan defines rollback triggers, procedures, and recovery mechanisms.

## Rollback Triggers

### Critical Triggers (Immediate Rollback)
- **Frontend build failures**: Production deployment cannot build successfully
- **Runtime errors**: >5% error rate in frontend error monitoring
- **Performance regression**: >2x increase in load time or bundle size
- **Authentication failures**: Users cannot log in or maintain sessions
- **API integration failures**: Frontend cannot communicate with backend

### Warning Triggers (Monitor, Consider Rollback)
- **Bundle size increase**: >20% increase over baseline
- **Memory usage**: >50% increase in client-side memory consumption
- **Accessibility failures**: New WCAG violations introduced
- **Browser compatibility**: Issues in supported browser versions

## Rollback Procedures

### Immediate Rollback (Critical Triggers)

#### Step 1: Traffic Routing
```bash
# Route to previous stable version
kubectl patch service frontend-service -p '{"spec":{"selector":{"version":"stable"}}}'
```

#### Step 2: Database Independence
Frontend rollback is database-independent - no data migration required
- Backend API remains unchanged
- User sessions preserved through JWT tokens
- No data loss risk

#### Step 3: Asset Rollback
```bash
# Restore previous Docker image
docker pull eduboost/frontend:stable-v1
docker tag eduboost/frontend:stable-v1 eduboost/frontend:latest
docker push eduboost/frontend:latest
```

#### Step 4: Verification
```bash
# Health checks
curl -f https://app.eduboost.sa/health
curl -f https://app.eduboost.sa/api/health
```

### Gradual Rollback (Warning Triggers)

#### Step 1: Feature Flags
```typescript
// Disable problematic features via feature flags
const config = {
  features: {
    newReactComponents: false,
    next15Features: false,
    experimentalFeatures: false
  }
};
```

#### Step 2: A/B Testing
- Route 10% traffic to previous version
- Monitor error rates and performance
- Gradually increase rollback traffic if needed

## Recovery Mechanisms

### Automated Recovery
- **Health monitoring**: Automated checks every 30 seconds
- **Auto-rollback**: Triggered by critical error thresholds
- **Alerting**: Immediate notifications to on-call team

### Manual Recovery
- **Rollback playbook**: Step-by-step procedures documented
- **Emergency contacts**: On-call engineer escalation
- **Communication plan**: Stakeholder notification templates

### Data Protection
- **No data migration**: Frontend changes are stateless
- **Session continuity**: JWT tokens remain valid
- **API compatibility**: Backend contracts unchanged

## Rollback Testing

### Pre-Deployment Validation
```bash
# Test rollback procedure
./scripts/test-frontend-rollback.sh

# Verify previous version still works
docker run --rm eduboost/frontend:stable-v1 npm test
```

### Monitoring Setup
```typescript
// Error rate monitoring
const errorThreshold = 0.05; // 5%
const performanceThreshold = 2000; // 2 seconds

if (errorRate > errorThreshold || loadTime > performanceThreshold) {
  triggerRollback();
}
```

## Rollback Communication

### Internal Communication
- **Slack**: #frontend-deployments channel
- **Email**: eng-team@eduboost.sa
- **PagerDuty**: On-call escalation

### External Communication
- **Status page**: Update deployment status
- **User notifications**: In-app messages if needed
- **Support team**: Known issues and workarounds

## Post-Rollback Actions

### Analysis
- **Root cause investigation**: Why upgrade failed
- **Impact assessment**: User experience and business impact
- **Lessons learned**: Documentation for future upgrades

### Preparation for Re-attempt
- **Issue resolution**: Fix identified problems
- **Enhanced testing**: Additional test coverage
- **Staged rollout**: Slower, more controlled deployment

## Related Documents
- [ADR-023](ADR-023-frontend-upgrade-react-19-next-15.md) - Frontend Upgrade Decision
- [ADR-012](ADR-012-ci-cd-infrastructure-deployment.md) - CI/CD Infrastructure
- [Frontend Monitoring Dashboard](https://monitoring.eduboost.sa/frontend)

## Approval
- **Frontend Lead**: Approved
- **DevOps Lead**: Approved  
- **Product Owner**: Approved
- **Date**: 2026-05-28
