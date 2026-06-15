"""
EduBoost SA — Prometheus Metrics
Counters and histograms for SLO tracking.
Shipped to Grafana Cloud via remote_write in production.
"""
from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, make_asgi_app

REGISTRY = CollectorRegistry(auto_describe=True)

# ── HTTP ──────────────────────────────────────────────────────────────────────
http_requests_total = Counter(
    "eduboost_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    "eduboost_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=REGISTRY,
)

# ── LLM Provider ──────────────────────────────────────────────────────────────
llm_requests_total = Counter(
    "eduboost_llm_requests_total",
    "Total LLM API calls",
    ["provider", "status"],  # provider: groq|anthropic, status: success|fallback|error
    registry=REGISTRY,
)

llm_latency_seconds = Histogram(
    "eduboost_llm_latency_seconds",
    "LLM response latency by provider",
    ["provider"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
    registry=REGISTRY,
)

LLM_TOKENS_TOTAL = Counter(
    "eduboost_llm_tokens_total",
    "Total tokens consumed",
    ["provider", "model", "operation"],
    registry=REGISTRY,
)

LLM_COST_USD = Gauge(
    "eduboost_llm_estimated_cost_usd_daily",
    "Estimated daily LLM cost in USD",
    ["provider"],
    registry=REGISTRY,
)

llm_tokens_total = LLM_TOKENS_TOTAL
llm_estimated_cost_usd_daily = LLM_COST_USD

LLM_PRICING_USD_PER_TOKEN: dict[str, dict[str, float]] = {
    "groq": {"input": 0.59 / 1_000_000, "output": 0.79 / 1_000_000},
    "anthropic": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
}

_llm_daily_cost_accumulator: dict[str, float] = {"groq": 0.0, "anthropic": 0.0}

# ── IRT Engine ────────────────────────────────────────────────────────────────
irt_sessions_total = Counter(
    "eduboost_irt_sessions_total",
    "Total IRT diagnostic sessions",
    ["grade", "subject"],
    registry=REGISTRY,
)

irt_computation_seconds = Histogram(
    "eduboost_irt_computation_seconds",
    "IRT ability estimation latency",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=REGISTRY,
)

item_bank_coverage_ratio = Gauge(
    "eduboost_item_bank_coverage_ratio",
    "Fraction of target approved item count per CAPS reference",
    ["caps_ref"],
    registry=REGISTRY,
)

diagnostic_sessions_total = Counter(
    "eduboost_diagnostic_sessions_total",
    "Diagnostic sessions by CAPS reference and outcome",
    ["caps_ref", "outcome"],
    registry=REGISTRY,
)

item_selection_latency_seconds = Histogram(
    "eduboost_item_selection_latency_seconds",
    "Item-bank selection latency",
    ["caps_ref"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25],
    registry=REGISTRY,
)

ITEM_BANK_COVERAGE_RATIO = item_bank_coverage_ratio
DIAGNOSTIC_SESSIONS_TOTAL = diagnostic_sessions_total
ITEM_SELECTION_LATENCY_SECONDS = item_selection_latency_seconds

# ── Learner Activity ──────────────────────────────────────────────────────────
active_learners_gauge = Gauge(
    "eduboost_active_learners",
    "Learners with an active session in the last 5 minutes",
    registry=REGISTRY,
)

lessons_generated_total = Counter(
    "eduboost_lessons_generated_total",
    "Total lessons generated",
    ["grade", "subject", "language"],
    registry=REGISTRY,
)

# ── POPIA / Consent ────────────────────────────────────────────────────────────
consent_events_total = Counter(
    "eduboost_consent_events_total",
    "POPIA consent lifecycle events",
    ["event"],  # granted|revoked|expired|renewed
    registry=REGISTRY,
)

consent_gate_blocks_total = Counter(
    "eduboost_consent_gate_blocks_total",
    "Requests blocked by consent gate",
    ["endpoint"],
    registry=REGISTRY,
)

# ── Infrastructure ───────────────────────────────────────────────────────────
db_pool_size = Gauge(
    "eduboost_db_pool_size_total",
    "Total database connections in the pool",
    registry=REGISTRY,
)

db_pool_checkedout = Gauge(
    "eduboost_db_pool_checkedout_total",
    "Database connections currently in use",
    registry=REGISTRY,
)

db_pool_overflow = Gauge(
    "eduboost_db_pool_overflow_total",
    "Database connections beyond the pool_size",
    registry=REGISTRY,
)

redis_connected_clients = Gauge(
    "eduboost_redis_connected_clients",
    "Number of clients connected to Redis",
    registry=REGISTRY,
)



# ── Readiness / Release Operations ──────────────────────────────────────────
readiness_component_status = Gauge(
    "eduboost_readiness_component_status",
    "Dependency readiness status by component; 1=ok, 0=unavailable/degraded",
    ["component", "criticality"],
    registry=REGISTRY,
)

audit_write_failures_total = Counter(
    "eduboost_audit_write_failures_total",
    "Audit write failures observed by the application",
    ["operation"],
    registry=REGISTRY,
)

backup_last_success_timestamp = Gauge(
    "eduboost_backup_last_success_timestamp",
    "Unix timestamp of the last successful PostgreSQL backup reported by backup automation",
    registry=REGISTRY,
)

backup_failures_total = Counter(
    "eduboost_backup_failures_total",
    "PostgreSQL backup failures reported by backup automation",
    ["stage"],
    registry=REGISTRY,
)

# ── ARQ Background Jobs ───────────────────────────────────────────────────────
arq_jobs_total = Counter(
    "eduboost_arq_jobs_total",
    "ARQ background job results",
    ["job_name", "status"],  # status: success|failed|retried
    registry=REGISTRY,
)

arq_job_duration_seconds = Histogram(
    "eduboost_arq_job_duration_seconds",
    "ARQ job execution time",
    ["job_name"],
    buckets=[0.1, 0.5, 1.0, 5.0, 30.0, 120.0],
    registry=REGISTRY,
)


def record_llm_tokens(
    provider: str,
    model: str,
    operation: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """Record token usage and update estimated daily provider cost telemetry."""
    LLM_TOKENS_TOTAL.labels(provider=provider, model=model, operation=operation).inc(
        input_tokens + output_tokens
    )

    pricing = LLM_PRICING_USD_PER_TOKEN.get(provider, {"input": 0.0, "output": 0.0})
    cost = input_tokens * pricing["input"] + output_tokens * pricing["output"]
    _llm_daily_cost_accumulator[provider] = _llm_daily_cost_accumulator.get(provider, 0.0) + cost
    LLM_COST_USD.labels(provider=provider).set(
        _llm_daily_cost_accumulator[provider]
    )


def make_metrics_app() -> object:
    """Returns an ASGI app that serves /metrics for Prometheus scraping."""
    return make_asgi_app(registry=REGISTRY)

# ── Phase 3 Content Review Governance ───────────────────────────────────────
content_review_decisions_total = Counter(
    "eduboost_content_review_decisions_total",
    "Educator content-review decisions",
    ["action", "result"],
    registry=REGISTRY,
)

content_review_state_transitions_total = Counter(
    "eduboost_content_review_state_transitions_total",
    "Content-governance state transitions",
    ["from_status", "to_status"],
    registry=REGISTRY,
)

content_review_stale_assignments = Gauge(
    "eduboost_content_review_stale_assignments",
    "Current number of stale content-review assignments",
    registry=REGISTRY,
)

content_review_reminders_total = Counter(
    "eduboost_content_review_reminders_total",
    "Stale content-review reminder and escalation actions",
    ["action"],
    registry=REGISTRY,
)

content_review_authorization_failures_total = Counter(
    "eduboost_content_review_authorization_failures_total",
    "Authorization failures on content-review operations",
    ["permission"],
    registry=REGISTRY,
)


# ── Phase 4 IRT Quality Governance ─────────────────────────────────────────
irt_calibration_runs_total = Counter(
    "eduboost_irt_calibration_runs_total",
    "IRT calibration run outcomes",
    ["status"],
    registry=REGISTRY,
)

irt_item_interventions_total = Counter(
    "eduboost_irt_item_interventions_total",
    "IRT item intervention decisions",
    ["action"],
    registry=REGISTRY,
)

irt_rewrite_requests_total = Counter(
    "eduboost_irt_rewrite_requests_total",
    "Governed item rewrite requests created by the IRT watchdog",
    registry=REGISTRY,
)

irt_answer_position_bias = Gauge(
    "eduboost_irt_answer_position_max_share",
    "Maximum share of the correct answer in one option position",
    registry=REGISTRY,
)


# ── Phase 5 Learner Tutor ─────────────────────────────────────────────────
tutor_messages_total = Counter(
    "eduboost_tutor_messages_total",
    "Learner tutor message outcomes",
    ["status", "provider"],
    registry=REGISTRY,
)

tutor_fallback_total = Counter(
    "eduboost_tutor_fallback_total",
    "Learner tutor safe fallbacks",
    ["reason"],
    registry=REGISTRY,
)

tutor_escalations_total = Counter(
    "eduboost_tutor_escalations_total",
    "Learner tutor educator/safeguarding escalations",
    ["reason", "severity"],
    registry=REGISTRY,
)

tutor_quality_score = Histogram(
    "eduboost_tutor_quality_score",
    "Validated learner tutor quality score",
    buckets=[0.0, 0.4, 0.6, 0.7, 0.8, 0.9, 1.0],
    registry=REGISTRY,
)


# ── Phase 6 Durable AI Operations ───────────────────────────────────────────
ai_usage_tokens_total = Counter(
    "eduboost_ai_usage_tokens_total",
    "Durably accounted AI tokens",
    ["provider", "model", "purpose", "outcome"],
    registry=REGISTRY,
)

ai_usage_cost_usd_total = Counter(
    "eduboost_ai_usage_estimated_cost_usd_total",
    "Estimated AI provider cost in USD; operational telemetry, not billing",
    ["provider", "model", "purpose"],
    registry=REGISTRY,
)

ai_budget_blocks_total = Counter(
    "eduboost_ai_budget_blocks_total",
    "AI operations blocked by durable budget authority",
    ["scope", "purpose"],
    registry=REGISTRY,
)

ai_budget_reserved_tokens = Counter(
    "eduboost_ai_budget_reserved_tokens_total",
    "Tokens reserved before governed AI calls",
    ["scope", "purpose"],
    registry=REGISTRY,
)

ai_budget_usage_ratio = Gauge(
    "eduboost_ai_budget_usage_ratio",
    "Current used-token ratio for durable budget scopes",
    ["scope"],
    registry=REGISTRY,
)
