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
