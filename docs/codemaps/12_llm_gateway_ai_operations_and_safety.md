# EduBoost V2 LLM Gateway, AI Operations, and Safety

Maps provider routing, JSON contracts, prompt governance, quotas, safety filters, tutor controls, evaluation, and operational AI evidence.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/core/llm*.py`
- `app/services/llm`
- `app/services/llm_provider.py`
- `app/services/safety_filter.py`
- `app/services/ai_safety.py`
- `app/services/ai_operations.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Provider-neutral LLM request and structured completion

**Description:** Follows an approved generation request through prompt construction, provider selection, retries, JSON parsing, and result normalization.

**Motivation:**
Provider abstraction prevents educational workflows from coupling correctness or safety to a single external model.

**Details:**

**Execution path**

1. Build a versioned prompt payload from grounded context.
2. Apply token, cost, and consent eligibility checks.
3. Select the configured provider and model.
4. Issue the external request with bounded timeout and retry.
5. Parse and validate structured JSON output.
6. Normalize usage, latency, provider, and error metadata.

**State and ownership boundaries**

Prompt version, source snapshot, provider response, and normalized artefact are distinct evidence layers.

**Failure, privacy, and control points**

Raw secrets are never logged, provider fallback is explicit, malformed output is rejected, and retries do not bypass budgets.

**Verification signals**

Run gateway, provider, JSON completion, timeout, fallback, and deterministic fixture tests.

**Trace text diagram:**
```text
1. Build a versioned prompt payload from grounded context [1a]
   |
   v
2. Apply token, cost, and consent eligibility checks [1b]
   |
   v
3. Select the configured provider and model [1c]
   |
   v
4. Issue the external request with bounded timeout and retry [1d]
   |
   v
5. Parse and validate structured JSON output [1d]
   |
   v
6. Normalize usage, latency, provider, and error metadata [1d]
```

**Location ID: 1a**
- **Title:** Core LLM gateway
- **Description:** Provider-neutral request boundary.
- **Path:LineNumber:** app/core/llm_gateway.py:1

**Location ID: 1b**
- **Title:** Service gateway
- **Description:** Structured completion orchestration.
- **Path:LineNumber:** app/services/llm/gateway.py:20

**Location ID: 1c**
- **Title:** JSON completion
- **Description:** Parsing and schema validation.
- **Path:LineNumber:** app/services/llm/json_completion.py:18

**Location ID: 1d**
- **Title:** Provider adapter
- **Description:** External provider abstraction.
- **Path:LineNumber:** app/services/llm_provider.py:33

### AI Guide: Provider-neutral LLM request and structured completion

**Motivation:**
Provider abstraction prevents educational workflows from coupling correctness or safety to a single external model.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors core llm gateway. [1b] anchors service gateway. [1c] anchors json completion. [1d] anchors provider adapter.

**Safe change boundary.** Prompt version, source snapshot, provider response, and normalized artefact are distinct evidence layers. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Raw secrets are never logged, provider fallback is explicit, malformed output is rejected, and retries do not bypass budgets.

**How to verify the change.** Run gateway, provider, JSON completion, timeout, fallback, and deterministic fixture tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Prompt safety, content filtering, and tutor guardrails

**Description:** Maps input and output safety checks around lessons, tutor messages, generated content, and learner data.

**Motivation:**
AI safety must be a layered runtime boundary rather than a one-time prompt instruction.

**Details:**

**Execution path**

1. Classify input for unsafe, disallowed, or privacy-sensitive content.
2. Redact or block PII before external transmission.
3. Constrain system prompt, tools, and source context.
4. Validate provider output against schema and educational policy.
5. Apply post-generation safety and age-appropriateness filters.
6. Fallback, refuse, or escalate with auditable reason.

**State and ownership boundaries**

Safety decisions and redacted payloads are evidence; disallowed raw data is not retained unnecessarily.

**Failure, privacy, and control points**

Prompt injection cannot expand tool scope, minors’ data is minimized, unsafe output never reaches learner delivery, and overrides are controlled.

**Verification signals**

Run AI safety, tutor safety, content safety, PII, prompt-injection, and cluster-F workflows.

**Trace text diagram:**
```text
1. Classify input for unsafe, disallowed, or privacy-sensitive content [2a]
   |
   v
2. Redact or block PII before external transmission [2b]
   |
   v
3. Constrain system prompt, tools, and source context [2c]
   |
   v
4. Validate provider output against schema and educational policy [2d]
   |
   v
5. Apply post-generation safety and age-appropriateness filters [2d]
   |
   v
6. Fallback, refuse, or escalate with auditable reason [2d]
```

**Location ID: 2a**
- **Title:** Safety filter
- **Description:** Shared input/output filtering.
- **Path:LineNumber:** app/services/safety_filter.py:43

**Location ID: 2b**
- **Title:** AI safety service
- **Description:** Policy and evaluation controls.
- **Path:LineNumber:** app/services/ai_safety.py:20

**Location ID: 2c**
- **Title:** Tutor safety
- **Description:** Tutor-specific guardrails.
- **Path:LineNumber:** app/services/tutor_safety.py:31

**Location ID: 2d**
- **Title:** AI safety workflow
- **Description:** Hosted AI safety gate.
- **Path:LineNumber:** .github/workflows/cluster-f-ai-safety.yml:1

### AI Guide: Prompt safety, content filtering, and tutor guardrails

**Motivation:**
AI safety must be a layered runtime boundary rather than a one-time prompt instruction.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors safety filter. [2b] anchors ai safety service. [2c] anchors tutor safety. [2d] anchors ai safety workflow.

**Safe change boundary.** Safety decisions and redacted payloads are evidence; disallowed raw data is not retained unnecessarily. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Prompt injection cannot expand tool scope, minors’ data is minimized, unsafe output never reaches learner delivery, and overrides are controlled.

**How to verify the change.** Run AI safety, tutor safety, content safety, PII, prompt-injection, and cluster-F workflows. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** AI operations, evaluation, quotas, and cost evidence

**Description:** Shows operational control of AI events, model evaluations, usage budgets, feedback, and release evidence.

**Motivation:**
Quality and affordability must be measured over time; a safe prompt path alone does not prove an operable AI system.

**Details:**

**Execution path**

1. Record each eligible AI operation and usage estimate.
2. Apply per-user, feature, and system quotas.
3. Aggregate latency, failure, token, and cost metrics.
4. Run model and fixture evaluations.
5. Review safety or quality exceptions.
6. Publish evidence used by content and release gates.

**State and ownership boundaries**

Operational events, evaluations, quotas, and cost aggregates are retained under separate access and retention policies.

**Failure, privacy, and control points**

Quota decisions are race-safe, evaluation fixtures contain no live PII, cost alerts are actionable, and provider changes require comparison evidence.

**Verification signals**

Run AI operations route/service tests, safety evidence checks, fixture matrix, and cost-monitoring contracts.

**Trace text diagram:**
```text
1. Record each eligible AI operation and usage estimate [3a]
   |
   v
2. Apply per-user, feature, and system quotas [3b]
   |
   v
3. Aggregate latency, failure, token, and cost metrics [3c]
   |
   v
4. Run model and fixture evaluations [3d]
   |
   v
5. Review safety or quality exceptions [3d]
   |
   v
6. Publish evidence used by content and release gates [3d]
```

**Location ID: 3a**
- **Title:** AI operations routes
- **Description:** Operational AI control API.
- **Path:LineNumber:** app/api_v2_routers/ai_operations.py:31

**Location ID: 3b**
- **Title:** AI operations service
- **Description:** Events, evaluation, and governance.
- **Path:LineNumber:** app/services/ai_operations.py:24

**Location ID: 3c**
- **Title:** AI operations models
- **Description:** Persistent AI evidence.
- **Path:LineNumber:** app/models/ai_operations.py:19

**Location ID: 3d**
- **Title:** AI fixture matrix
- **Description:** Evaluation coverage verification.
- **Path:LineNumber:** scripts/check_ai_fixture_coverage_matrix.py:74

### AI Guide: AI operations, evaluation, quotas, and cost evidence

**Motivation:**
Quality and affordability must be measured over time; a safe prompt path alone does not prove an operable AI system.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors ai operations routes. [3b] anchors ai operations service. [3c] anchors ai operations models. [3d] anchors ai fixture matrix.

**Safe change boundary.** Operational events, evaluations, quotas, and cost aggregates are retained under separate access and retention policies. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Quota decisions are race-safe, evaluation fixtures contain no live PII, cost alerts are actionable, and provider changes require comparison evidence.

**How to verify the change.** Run AI operations route/service tests, safety evidence checks, fixture matrix, and cost-monitoring contracts. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
