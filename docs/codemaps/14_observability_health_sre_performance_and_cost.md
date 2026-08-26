# EduBoost V2 Observability, Health, SRE, Performance, and Cost

Maps structured logs, metrics, tracing context, health and readiness, alerts, incident evidence, performance budgets, scale controls, and cost assurance.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/core/logging.py`
- `app/core/metrics.py`
- `app/core/middleware.py`
- `app/core/health.py`
- `app/services/telemetry.py`
- `app/modules/observability`
- `app/modules/performance_scale_cost`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Structured logging, metrics, request context, and telemetry

**Description:** Follows a request or job as it emits correlated logs, counters, histograms, and domain telemetry.

**Motivation:**
Operators need evidence that joins user-visible failures to the responsible route, dependency, job, or provider without logging private learner data.

**Details:**

**Execution path**

1. Create or propagate correlation and trace identifiers.
2. Attach route, actor class, and runtime metadata.
3. Emit structured request and domain logs.
4. Record latency, outcome, queue, and dependency metrics.
5. Export telemetry to configured sinks.
6. Use identifiers to join incidents with audit and release evidence.

**State and ownership boundaries**

Operational telemetry is distinct from audit evidence and is retained with privacy-minimizing dimensions.

**Failure, privacy, and control points**

Logs redact secrets and PII, cardinality is bounded, metrics do not encode learner IDs, and failures remain observable.

**Verification signals**

Run logging redaction, metrics, middleware, telemetry, and observability contract tests.

**Trace text diagram:**
```text
1. Create or propagate correlation and trace identifiers [1a]
   |
   v
2. Attach route, actor class, and runtime metadata [1b]
   |
   v
3. Emit structured request and domain logs [1c]
   |
   v
4. Record latency, outcome, queue, and dependency metrics [1d]
   |
   v
5. Export telemetry to configured sinks [1d]
   |
   v
6. Use identifiers to join incidents with audit and release evidence [1d]
```

**Location ID: 1a**
- **Title:** Structured logging
- **Description:** Logging configuration and redaction.
- **Path:LineNumber:** app/core/logging.py:19

**Location ID: 1b**
- **Title:** Metrics
- **Description:** Prometheus metric definitions.
- **Path:LineNumber:** app/core/metrics.py:3

**Location ID: 1c**
- **Title:** Request instrumentation
- **Description:** Per-request telemetry.
- **Path:LineNumber:** app/core/middleware.py:3

**Location ID: 1d**
- **Title:** Telemetry service
- **Description:** Domain and operational event emission.
- **Path:LineNumber:** app/services/telemetry.py:13

### AI Guide: Structured logging, metrics, request context, and telemetry

**Motivation:**
Operators need evidence that joins user-visible failures to the responsible route, dependency, job, or provider without logging private learner data.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors structured logging. [1b] anchors metrics. [1c] anchors request instrumentation. [1d] anchors telemetry service.

**Safe change boundary.** Operational telemetry is distinct from audit evidence and is retained with privacy-minimizing dimensions. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Logs redact secrets and PII, cardinality is bounded, metrics do not encode learner IDs, and failures remain observable.

**How to verify the change.** Run logging redaction, metrics, middleware, telemetry, and observability contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Health, readiness, alerting, and incident response

**Description:** Maps runtime signals from probes and metrics through alert evaluation, staging validation, and incident handling.

**Motivation:**
Truthful readiness and actionable alerts are required before live learner traffic can be operated safely.

**Details:**

**Execution path**

1. Expose liveness, readiness, and deep dependency probes.
2. Scrape metrics and evaluate service-level signals.
3. Trigger alerts with severity and ownership.
4. Link alerts to runbooks and current deployment.
5. Execute incident triage, mitigation, and communication.
6. Capture incident and recovery evidence.

**State and ownership boundaries**

Probe results are ephemeral; incidents, runbook actions, and release decisions become persistent evidence.

**Failure, privacy, and control points**

Alerts avoid noisy duplicates, probes are bounded and non-mutating, and release gates do not suppress active critical incidents.

**Verification signals**

Run observability/SRE routes, readiness assurance, alert rule, staging smoke, and operational drill tests.

**Trace text diagram:**
```text
1. Expose liveness, readiness, and deep dependency probes [2a]
   |
   v
2. Scrape metrics and evaluate service-level signals [2b]
   |
   v
3. Trigger alerts with severity and ownership [2c]
   |
   v
4. Link alerts to runbooks and current deployment [2d]
   |
   v
5. Execute incident triage, mitigation, and communication [2d]
   |
   v
6. Capture incident and recovery evidence [2d]
```

**Location ID: 2a**
- **Title:** SRE routes
- **Description:** Operational readiness API.
- **Path:LineNumber:** app/api_v2_routers/observability_sre.py:15

**Location ID: 2b**
- **Title:** Observability assurance
- **Description:** SRE evidence and controls.
- **Path:LineNumber:** app/modules/observability/assurance.py:33

**Location ID: 2c**
- **Title:** Readiness aggregation
- **Description:** Dependency readiness authority.
- **Path:LineNumber:** app/core/runtime_readiness.py:61

**Location ID: 2d**
- **Title:** Observability workflow
- **Description:** Hosted monitoring gate.
- **Path:LineNumber:** .github/workflows/observability_check.yml:14

### AI Guide: Health, readiness, alerting, and incident response

**Motivation:**
Truthful readiness and actionable alerts are required before live learner traffic can be operated safely.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors sre routes. [2b] anchors observability assurance. [2c] anchors readiness aggregation. [2d] anchors observability workflow.

**Safe change boundary.** Probe results are ephemeral; incidents, runbook actions, and release decisions become persistent evidence. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Alerts avoid noisy duplicates, probes are bounded and non-mutating, and release gates do not suppress active critical incidents.

**How to verify the change.** Run observability/SRE routes, readiness assurance, alert rule, staging smoke, and operational drill tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Performance, scale, resource budgets, and cost controls

**Description:** Shows measurement and gating of latency, throughput, worker capacity, storage, provider usage, and cost.

**Motivation:**
Scale readiness is not a single load-test number; it is a set of budgets tied to critical learner and operator journeys.

**Details:**

**Execution path**

1. Define workload and service-level budgets.
2. Measure route, database, cache, worker, frontend, and provider performance.
3. Identify saturation and expensive query or token paths.
4. Apply caching, batching, concurrency, and backpressure controls.
5. Re-run representative smoke and scale scenarios.
6. Publish cost and capacity evidence for release decisions.

**State and ownership boundaries**

Performance baselines and cost models are versioned evidence linked to environment and workload.

**Failure, privacy, and control points**

Optimizations preserve correctness, queues have backpressure, caches respect privacy and invalidation, and budget regressions fail visibly.

**Verification signals**

Run performance-scale-cost route/module tests, smoke suites, Lighthouse, and PRD-8 assurance verifiers.

**Trace text diagram:**
```text
1. Define workload and service-level budgets [3a]
   |
   v
2. Measure route, database, cache, worker, frontend, and provider performance [3b]
   |
   v
3. Identify saturation and expensive query or token paths [3c]
   |
   v
4. Apply caching, batching, concurrency, and backpressure controls [3d]
   |
   v
5. Re-run representative smoke and scale scenarios [3d]
   |
   v
6. Publish cost and capacity evidence for release decisions [3d]
```

**Location ID: 3a**
- **Title:** Performance routes
- **Description:** Scale and cost control surface.
- **Path:LineNumber:** app/api_v2_routers/performance_scale_cost.py:15

**Location ID: 3b**
- **Title:** Performance assurance
- **Description:** Budget and evidence evaluation.
- **Path:LineNumber:** app/modules/performance_scale_cost/assurance.py:35

**Location ID: 3c**
- **Title:** Performance readiness
- **Description:** Release-readiness projection.
- **Path:LineNumber:** app/modules/performance_scale_cost/readiness.py:56

**Location ID: 3d**
- **Title:** Frontend performance workflow
- **Description:** Lighthouse budget gate.
- **Path:LineNumber:** .github/workflows/lighthouse.yml:1

### AI Guide: Performance, scale, resource budgets, and cost controls

**Motivation:**
Scale readiness is not a single load-test number; it is a set of budgets tied to critical learner and operator journeys.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors performance routes. [3b] anchors performance assurance. [3c] anchors performance readiness. [3d] anchors frontend performance workflow.

**Safe change boundary.** Performance baselines and cost models are versioned evidence linked to environment and workload. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Optimizations preserve correctness, queues have backpressure, caches respect privacy and invalidation, and budget regressions fail visibly.

**How to verify the change.** Run performance-scale-cost route/module tests, smoke suites, Lighthouse, and PRD-8 assurance verifiers. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
