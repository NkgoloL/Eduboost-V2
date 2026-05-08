# Critical Path

This sequence is optimized to reduce implementation risk, not checkbox velocity.

## Phase order

1. **PR-001 Repo governance and backlog hygiene** — 8 open, 0 critical.
2. **PR-002 Backend runtime/API contract baseline** — 22 open, 6 critical.
3. **PR-003 Auth/session/RBAC hardening** — 26 open, 15 critical.
4. **PR-004 POPIA consent/data-rights/audit** — 51 open, 28 critical.
5. **PR-005 Database/migration integrity** — 13 open, 2 critical.
6. **PR-006 AI/CAPS/diagnostics safety** — 64 open, 15 critical.
7. **PR-007 Frontend core flows and accessibility** — 18 open, 7 critical.
8. **PR-008 DevOps/observability/DR** — 68 open, 31 critical.
9. **PR-009 Product/ops/future differentiation** — 120 open, 15 critical.

## External blockers / human decisions

| ID | Priority | Status | Task |
|---|---|---|---|
| TODO-013 | critical | Blocked | Automated database backups are enabled, encrypted, monitored, and restore-tested. |
| TODO-014 | critical | Blocked | Security headers, CORS, cookie policy, JWT policy, and rate limits are verified in staging. |
| TODO-015 | critical | Blocked | Logs, metrics, traces, alerts, and dashboards are live before real learner data is processed. |
| TODO-195 | critical | Human-decision | Decide production billing provider. |
| TODO-201 | critical | Human-decision | Choose production email provider. |
| TODO-213 | critical | Human-decision | Choose production target explicitly: Azure Container Apps, AKS, or another managed container platform. |
| TODO-214 | critical | Blocked | Make Docker Compose, Kubernetes, Bicep, and CI deployment assets match the chosen target. |
| TODO-024 | high | Blocked | Protect `master`/`main`: require PR review, required checks, no force-push, no branch deletion, and signed commits if feasible. |
| TODO-028 | high | Human-decision | Audit dependency files and decide canonical dependency paths for runtime, dev, docs, and ML extras. |
| TODO-044 | high | Human-decision | Decide canonical business-logic location: either `app/services` as application layer or `app/modules/<context>/service.py` as bounded-context services. |
| TODO-063 | high | Blocked | Require backup, staging dry-run, validation script, and rollback plan for migrations touching learner/guardian data. |
| TODO-143 | high | Human-decision | Add adaptive remediation: detect misconception, choose explanation strategy, generate targeted practice, re-assess. |
| TODO-198 | high | Human-decision | Define pricing: free tier, parent plan, school plan, sponsored learner plan, NGO/community plan. |
| TODO-335 | high | Human-decision | Add product overview, parent guide, learner guide, teacher guide, FAQ, pricing/billing FAQ, and AI transparency FAQ. |
| TODO-392 | high | Human-decision | Define production support model, pricing operations, refund process, and escalation process. |
| TODO-057 | medium | Blocked | Add slow-query logging in staging and production. |
| TODO-100 | medium | Human-decision | Add school-mediated consent model if institutional deployments enter scope. |
| TODO-204 | medium | Human-decision | Add SMS/WhatsApp notifications only after privacy impact review. |
| TODO-372 | medium | Human-decision | Let learners choose explanation style, difficulty, theme/avatar, and daily goal. |
| TODO-393 | medium | Human-decision | Define school procurement workflow, sponsored learner workflow, and NGO/community deployment model. |
| TODO-147 | research | Human-decision | Investigate retrieval-augmented generation using only approved CAPS-aligned content. |
| TODO-148 | research | Human-decision | Investigate local/smaller models for cost and privacy-sensitive workloads. |
| TODO-167 | research | Human-decision | Evaluate Bayesian Knowledge Tracing or Deep Knowledge Tracing once enough usage data exists. |
| TODO-297 | research | Human-decision | Explore partnerships with schools, NGOs, after-school programs, and community learning centers. |
| TODO-315 | research | Human-decision | Explore sponsored learner and low-data partnership models. |
| TODO-343 | research | Human-decision | Define ethical experimentation guidelines for minors and education. |
| TODO-358 | research | Human-decision | Explore local inference for cheaper high-volume tasks. |
| TODO-366 | research | Human-decision | Evaluate fairness of recommendations across language and socioeconomic context. |
| TODO-383 | research | Human-decision | Partner with educators for expert review. |
| TODO-387 | research | Human-decision | Validate translations with native speakers and educators. |
| TODO-406 | research | Human-decision | Build CAPS-aligned knowledge graph: topics, prerequisites, misconceptions, diagnostic items, lessons, practice questions, local examples. |
| TODO-414 | research | Human-decision | Validate workflow with real classroom constraints before scaling this mode. |
| TODO-417 | research | Human-decision | Explore intermittent-internet school/community deployment. |
| TODO-424 | research | Human-decision | Add sponsored learner model. |
| TODO-425 | research | Human-decision | Add NGO/community dashboard. |
| TODO-426 | research | Human-decision | Add anonymized impact reports: learners supported, topics mastered, practice hours, regions served, language support usage. |