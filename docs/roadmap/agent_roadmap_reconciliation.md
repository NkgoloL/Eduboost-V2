# Agent Roadmap Reconciliation

**North Star:** Convert post-530 repository completion into beta readiness by closing CI, Docker, content-review, POPIA, auth-hardening, and operational evidence gaps.

| ID | Priority | Area | Status | Task | Next action |
|---|---|---|---|---|---|
| T-01 | P0 | CI/CD | PARTIAL_OR_DONE_VERIFY | Trigger GitHub Actions CI on fork | Run task-specific checker and confirm evidence freshness. |
| T-02 | P0 | CI/CD | PARTIAL_OR_DONE_VERIFY | Fix README CI badge | Run task-specific checker and confirm evidence freshness. |
| T-03 | P0 | CI/CD | PARTIAL_OR_DONE_VERIFY | Enable branch protection | Run task-specific checker and confirm evidence freshness. |
| T-04 | P0 | Testing | PARTIAL_OR_DONE_VERIFY | Warning integrity check | Run task-specific checker and confirm evidence freshness. |
| T-05 | P1 | Content | PARTIAL_OR_DONE_VERIFY | Educator item review and beta content gate | Run task-specific checker and confirm evidence freshness. |
| T-06 | P1 | Docker | PARTIAL_OR_DONE_VERIFY | Remove --reload from base Compose | Run task-specific checker and confirm evidence freshness. |
| T-07 | P1 | Docker | PARTIAL_OR_DONE_VERIFY | Frontend production build | Run task-specific checker and confirm evidence freshness. |
| T-08 | P1 | Docker | PARTIAL_OR_DONE_VERIFY | Compose resource limits | Run task-specific checker and confirm evidence freshness. |
| T-09 | P1 | Docker/Security | PARTIAL_OR_DONE_VERIFY | Require Grafana admin secret | Run task-specific checker and confirm evidence freshness. |
| T-10 | P1 | Docker | PARTIAL_OR_DONE_VERIFY | Add nginx production config | Run task-specific checker and confirm evidence freshness. |
| T-11 | P1 | Security | PARTIAL_OR_DONE_VERIFY | Login rate limiting/account lockout | Run task-specific checker and confirm evidence freshness. |
| T-12R | P2 | Architecture | PARTIAL_OR_DONE_VERIFY | Service boundary consolidation without deleting active facades | Run task-specific checker and confirm evidence freshness. |
| T-13 | P1 | Governance | PARTIAL_OR_DONE_VERIFY | PR template and CODEOWNERS | Run task-specific checker and confirm evidence freshness. |
| T-14 | P1 | POPIA | PARTIAL_OR_DONE_VERIFY | Run POPIA sweep and archive evidence | Run task-specific checker and confirm evidence freshness. |
| T-15 | P2 | Dependencies | PARTIAL_OR_DONE_VERIFY | Pin Python dependencies | Run task-specific checker and confirm evidence freshness. |
| T-16 | P2 | Security | PARTIAL_OR_DONE_VERIFY | JWT key rotation | Run task-specific checker and confirm evidence freshness. |
| T-17 | P2 | Testing | PARTIAL_OR_DONE_VERIFY | Object-level authz for every router | Run task-specific checker and confirm evidence freshness. |
| T-18 | P2 | Observability | PENDING_INFRA | Alertmanager live notification | Wire notification secret and fire test alert. |
| T-19 | P2 | Operations | PENDING_INFRA | Backup/restore drill | Execute real drill and archive output. |
| T-20 | P2 | Localisation | PARTIAL_OR_DONE_VERIFY | Multilingual educator validation | Run task-specific checker and confirm evidence freshness. |
| T-21 | P3 | Frontend | PARTIAL_OR_DONE_VERIFY | Bundle analysis/performance budget | Run task-specific checker and confirm evidence freshness. |
| T-22 | P3 | Architecture | PARTIAL_OR_DONE_VERIFY | ADRs for major decisions | Run task-specific checker and confirm evidence freshness. |
