"""
EduBoost V2 — IRT Diagnostic Engine (Legislature Pillar 1)
2-Parameter Logistic (2PL) Item Response Theory model.
P(correct | θ) = 1 / (1 + exp(-a(θ - b)))
"""
from __future__ import annotations

import math

from app.core.logging import get_logger
from app.domain.models import IRTItem

log = get_logger(__name__)

# ── IRT maths ─────────────────────────────────────────────────────────────────


def p_correct(theta: float, a: float, b: float) -> float:
    """Probability of a correct response given ability theta."""
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def update_theta_mle(theta: float, responses: list[tuple[IRTItem, bool]], max_iter: int = 20) -> float:
    """
    Maximum-Likelihood Estimation of theta via Newton-Raphson.
    responses: [(IRTItem, is_correct), ...]
    """
    current = theta
    for _ in range(max_iter):
        gradient = 0.0
        hessian = 0.0
        for item, correct in responses:
            p = p_correct(current, item.a_param, item.b_param)
            q = 1.0 - p
            residual = (1.0 if correct else 0.0) - p
            gradient += item.a_param * residual
            hessian -= (item.a_param ** 2) * p * q

        if abs(hessian) < 1e-9:
            break
        delta = gradient / hessian
        current -= delta
        if abs(delta) < 1e-4:
            break

    return round(max(-4.0, min(4.0, current)), 4)  # clamp to [-4, 4]


class DiagnosticEngine:
    """
    Runs the Gap-Probe Cascade using real IRT item bank data.
    """

    def compute_theta(
        self,
        starting_theta: float,
        items: list[IRTItem],
        correct_item_ids: set[str],
    ) -> float:
        responses = [(item, item.id in correct_item_ids) for item in items]
        return update_theta_mle(starting_theta, responses)

    def identify_gaps(
        self, items: list[IRTItem], correct_item_ids: set[str], threshold_p: float = 0.50
    ) -> list[dict]:
        """
        Identify knowledge gaps: items missed where expected P(correct|θ) > threshold.
        Returns list of {grade, subject, topic, severity} dicts.
        """
        gaps: dict[str, dict] = {}
        for item in items:
            if item.id not in correct_item_ids:
                key = f"{item.subject}::{item.topic}"
                existing = gaps.get(key)
                if not existing or item.b_param > existing["severity"]:
                    gaps[key] = {
                        "grade": item.grade,
                        "subject": item.subject,
                        "topic": item.topic,
                        "severity": round(min(1.0, max(0.0, (item.b_param + 3) / 6)), 3),
                    }
        return list(gaps.values())

    def select_next_item(
        self, theta: float, administered_ids: set[str], bank: list[IRTItem]
    ) -> IRTItem | None:
        """Maximum Information item selection (adaptive)."""
        best_item = None
        best_info = -1.0
        for item in bank:
            if item.id in administered_ids:
                continue
            p = p_correct(theta, item.a_param, item.b_param)
            q = 1.0 - p
            information = (item.a_param ** 2) * p * q
            if information > best_info:
                best_info = information
                best_item = item
        return best_item
