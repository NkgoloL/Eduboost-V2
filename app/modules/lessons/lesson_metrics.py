# app/modules/lessons/lesson_metrics.py
#
# L5-08 — EduBoost SA Phase 5
# Prometheus metrics for the AI lesson generation pipeline.
#
# Exposes 6 metrics required by the roadmap (§L5-08):
#   1. lesson_generation_latency_seconds
#   2. lesson_validation_pass_rate (via counter pair)
#   3. answer_key_verification_pass_rate (via counter pair)
#   4. review_queue_depth (gauge, updated on queue changes)
#   5. provider_fallback_rate (via counter)
#   6. budget_utilization_ratio (gauge, updated on token accounting)
#
# Usage (in lesson_generator.py and lesson_review_router.py):
#
#   from app.modules.lessons.lesson_metrics import lesson_metrics
#
#   # Time a generation attempt:
#   with lesson_metrics.generation_latency.labels(
#       caps_ref="4.M.1.1", provider="groq"
#   ).time():
#       lesson = await gateway.generate(...)
#
#   # Record a validation outcome:
#   lesson_metrics.record_validation(passed=True, caps_ref="4.M.1.1")
#
#   # Record an answer-key verification outcome:
#   lesson_metrics.record_answer_key_verification(verified=True)
#
#   # Update review queue depth:
#   lesson_metrics.set_review_queue_depth(depth=3)
#
#   # Record a provider fallback event:
#   lesson_metrics.record_provider_fallback(from_provider="groq", to_provider="anthropic")
#
#   # Update budget utilisation ratio:
#   lesson_metrics.set_budget_utilization(ratio=0.62, tenant_id="default")

from __future__ import annotations

import logging
from typing import Literal

from prometheus_client import Counter, Gauge, Histogram

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Label value types
# ---------------------------------------------------------------------------

ProviderName = Literal["groq", "anthropic", "mock", "unknown"]
DifficultyLevel = Literal["foundational", "developing", "on_level", "extending", "unknown"]


# ---------------------------------------------------------------------------
# Metrics registry
# ---------------------------------------------------------------------------


class LessonMetrics:
    """
    Centralised Prometheus metrics for the AI lesson generation pipeline.

    Instantiated once as a module-level singleton (``lesson_metrics``) so that
    all metrics share the same registry and label cardinality is predictable.
    """

    def __init__(self) -> None:
        # ------------------------------------------------------------------
        # 1. lesson_generation_latency_seconds
        #    Histogram of end-to-end lesson generation time (gateway call +
        #    validation + answer-key verification + DB persist).
        # ------------------------------------------------------------------
        self.generation_latency: Histogram = Histogram(
            name="lesson_generation_latency_seconds",
            documentation=(
                "End-to-end lesson generation latency in seconds "
                "(from request to validated LessonResponse returned)."
            ),
            labelnames=["caps_ref", "provider", "difficulty"],
            buckets=(0.5, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 30.0),
        )

        # ------------------------------------------------------------------
        # 2. lesson_validation_pass / fail counters → pass_rate computable
        #    via rate(pass) / (rate(pass) + rate(fail)) in Grafana.
        # ------------------------------------------------------------------
        self._validation_pass: Counter = Counter(
            name="lesson_validation_pass_total",
            documentation="Number of lessons that passed all 8 validator rules.",
            labelnames=["caps_ref"],
        )
        self._validation_fail: Counter = Counter(
            name="lesson_validation_fail_total",
            documentation="Number of lessons that failed one or more validator rules.",
            labelnames=["caps_ref", "failed_rule"],
        )

        # ------------------------------------------------------------------
        # 3. answer_key_verification pass / fail counters → verification rate
        # ------------------------------------------------------------------
        self._akv_pass: Counter = Counter(
            name="answer_key_verification_pass_total",
            documentation="Lessons where the second independent LLM call agreed with the answer key.",
            labelnames=["caps_ref"],
        )
        self._akv_fail: Counter = Counter(
            name="answer_key_verification_fail_total",
            documentation=(
                "Lessons where the second LLM call disagreed with the answer key "
                "— lesson auto-queued for human review."
            ),
            labelnames=["caps_ref"],
        )

        # ------------------------------------------------------------------
        # 4. review_queue_depth — Gauge; updated whenever the queue changes.
        # ------------------------------------------------------------------
        self.review_queue_depth: Gauge = Gauge(
            name="lesson_review_queue_depth",
            documentation=(
                "Current number of lessons awaiting human review "
                "(review_status = ai_generated AND quality_score < 0.7 OR answer_key_verified=false)."
            ),
        )

        # ------------------------------------------------------------------
        # 5. provider_fallback_total — Counter; incremented on each fallback.
        # ------------------------------------------------------------------
        self._provider_fallback: Counter = Counter(
            name="lesson_provider_fallback_total",
            documentation="Number of times the LLM gateway fell back from the primary provider.",
            labelnames=["from_provider", "to_provider", "reason"],
        )

        # ------------------------------------------------------------------
        # 6. budget_utilization_ratio — Gauge; updated on token accounting.
        # ------------------------------------------------------------------
        self.budget_utilization: Gauge = Gauge(
            name="lesson_budget_utilization_ratio",
            documentation=(
                "Fraction of the monthly token budget consumed (0.0–1.0). "
                "Alert fires at 0.8."
            ),
            labelnames=["tenant_id"],
        )

        # ------------------------------------------------------------------
        # Supplementary: circuit breaker state (0=closed, 1=half_open, 2=open)
        # ------------------------------------------------------------------
        self.circuit_breaker_state: Gauge = Gauge(
            name="llm_gateway_circuit_breaker_state",
            documentation=(
                "Circuit breaker state per provider: 0=closed, 1=half_open, 2=open."
            ),
            labelnames=["provider"],
        )

        # ------------------------------------------------------------------
        # Supplementary: generation attempts (total, including retries)
        # ------------------------------------------------------------------
        self.generation_attempts: Counter = Counter(
            name="lesson_generation_attempts_total",
            documentation="Total lesson generation attempts including retries.",
            labelnames=["caps_ref", "provider", "outcome"],
        )

        log.debug("LessonMetrics: Prometheus metrics registered.")

    # ------------------------------------------------------------------
    # Convenience recording methods
    # ------------------------------------------------------------------

    def record_validation(self, *, passed: bool, caps_ref: str, failed_rule: str = "") -> None:
        """Record one validation outcome."""
        if passed:
            self._validation_pass.labels(caps_ref=caps_ref).inc()
        else:
            self._validation_fail.labels(
                caps_ref=caps_ref,
                failed_rule=failed_rule or "unknown",
            ).inc()

    def record_answer_key_verification(self, *, verified: bool, caps_ref: str) -> None:
        """Record one answer-key verification outcome."""
        if verified:
            self._akv_pass.labels(caps_ref=caps_ref).inc()
        else:
            self._akv_fail.labels(caps_ref=caps_ref).inc()

    def set_review_queue_depth(self, depth: int) -> None:
        """Set the current review queue depth (call after any queue mutation)."""
        self.review_queue_depth.set(depth)

    def record_provider_fallback(
        self,
        *,
        from_provider: str,
        to_provider: str,
        reason: str = "primary_failure",
    ) -> None:
        """Increment provider fallback counter."""
        self._provider_fallback.labels(
            from_provider=from_provider,
            to_provider=to_provider,
            reason=reason,
        ).inc()

    def set_budget_utilization(self, *, ratio: float, tenant_id: str = "default") -> None:
        """
        Update budget utilisation gauge.
        ratio must be in [0.0, 1.0].
        """
        clamped = max(0.0, min(1.0, ratio))
        self.budget_utilization.labels(tenant_id=tenant_id).set(clamped)

    def set_circuit_breaker_state(
        self,
        *,
        provider: str,
        state: Literal["closed", "half_open", "open"],
    ) -> None:
        """Update the circuit breaker state gauge for a provider."""
        state_value = {"closed": 0, "half_open": 1, "open": 2}.get(state, 0)
        self.circuit_breaker_state.labels(provider=provider).set(state_value)

    def record_generation_attempt(
        self,
        *,
        caps_ref: str,
        provider: str,
        outcome: Literal["success", "validation_fail", "provider_error", "circuit_open"],
    ) -> None:
        """Record a single generation attempt with outcome label."""
        self.generation_attempts.labels(
            caps_ref=caps_ref,
            provider=provider,
            outcome=outcome,
        ).inc()


# ---------------------------------------------------------------------------
# Module-level singleton — import and use directly
# ---------------------------------------------------------------------------

lesson_metrics = LessonMetrics()
