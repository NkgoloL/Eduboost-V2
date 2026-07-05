---
title: Rr012 Production Telemetry Dashboard Policy
status: pending-evidence
owner: operations
reviewers: [operations, security, backend]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 30
evidence_command: make rr012-production-telemetry-dashboard-check
code_anchors: [docs/telemetry, scripts/roadmap_reconciliation]
---

    # RR-012 Production Telemetry Dashboard Policy

    Production telemetry dashboard authority recorded: true

    ## Existing prerequisites

    - RR-011 live billing provider integration is recorded before RR-012.
    - `docs/observability/production_observability_architecture_contract.md` remains the observability architecture contract.
    - `app/core/metrics.py`, `prometheus/alerts.yml`, and `alertmanager/alertmanager.yml` remain the primary metric and alerting anchors.

    ## Required dashboards

    - Production API overview
    - Learner journey health
    - POPIA privacy operations
    - AI and LLM operations
    - Billing operations
    - Infrastructure readiness

    ## Required controls

    - Grafana dashboard inventory is recorded.
    - Prometheus datasource linkage is recorded.
    - SLO panels are linked.
    - Alert rule links are recorded.
    - Runbook links are recorded.
    - Dashboard access control is reviewed.
    - Dashboard privacy boundary is reviewed.

    ## Known residual caveats carried forward

    - RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
    - RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
    - RR-011 live billing provider integration is recorded, but Billing launch authorised: false and Live payment processing authorised: false remain the boundary.
    - RR-013 advanced mastery-model research remains outstanding.
    - RR-015 external approvals remain outstanding.
    - RR-016 operational drills remain outstanding.

    ## Boundary markers

    Billing launch authorised: false  
    Live payment processing authorised: false  
    Production release authorised: false  
    Deployment authorised: false  
    Release tag authorised: false  
    Public beta authorised: false  
    Runtime KG implementation claimed: false
