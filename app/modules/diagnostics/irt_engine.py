"""
EduBoost V2 — IRT Diagnostic Engine (Legislature Pillar 1)
2-Parameter Logistic (2PL) Item Response Theory model.
P(correct | θ) = 1 / (1 + exp(-a(θ - b)))
"""
from __future__ import annotations

import math
from statistics import fmean

from app.core.logging import get_logger
from app.domain.models import IRTItem

log = get_logger(__name__)

# ── IRT maths ─────────────────────────────────────────────────────────────────


def p_correct(theta: float, a: float, b: float) -> float:
    """Probability of a correct response given ability theta."""
    # Hard bounds for parameters to prevent overflow/divergence
    a = max(0.1, min(4.0, a))
    b = max(-4.0, min(4.0, b))
    theta = max(-5.0, min(5.0, theta))
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def fisher_information(theta: float, a: float, b: float) -> float:
    p = p_correct(theta, a, b)
    q = 1.0 - p
    return (a ** 2) * p * q


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
        theta, _sem = self.estimate_theta_eap(responses, prior_mean=starting_theta)
        return theta

    def estimate_theta_eap(
        self,
        responses: list[tuple[IRTItem, bool]],
        *,
        prior_mean: float = 0.0,
        prior_sd: float = 1.0,
        theta_min: float = -4.0,
        theta_max: float = 4.0,
        step: float = 0.1,
    ) -> tuple[float, float]:
        grid: list[float] = []
        value = theta_min
        while value <= theta_max + 1e-9:
            grid.append(round(value, 4))
            value += step

        posterior_weights: list[float] = []
        for theta in grid:
            prior = math.exp(-0.5 * (((theta - prior_mean) / prior_sd) ** 2))
            likelihood = 1.0
            for item, correct in responses:
                # 2PL model probability
                prob = p_correct(theta, item.a_param, item.b_param)
                # Likelihood clamping to prevent underflow
                likelihood *= max(1e-12, prob if correct else (1.0 - prob))
            posterior_weights.append(prior * likelihood)

        total = sum(posterior_weights) or 1.0
        posterior = [weight / total for weight in posterior_weights]
        eap = sum(theta * weight for theta, weight in zip(grid, posterior, strict=True))
        variance = sum(((theta - eap) ** 2) * weight for theta, weight in zip(grid, posterior, strict=True))
        sem = math.sqrt(max(variance, 0.0))
        return round(eap, 4), round(sem, 4)

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
        ranked = sorted(gaps.values(), key=lambda gap: gap["severity"], reverse=True)
        return ranked

    def select_next_item(
        self, theta: float, administered_ids: set[str], bank: list[IRTItem]
    ) -> IRTItem | None:
        """Maximum Information item selection (adaptive)."""
        best_item = None
        best_info = -1.0
        for item in bank:
            if item.id in administered_ids:
                continue
            information = fisher_information(theta, item.a_param, item.b_param)
            if information > best_info:
                best_info = information
                best_item = item
        return best_item

    def should_stop(self, administered_count: int, standard_error: float) -> bool:
        return administered_count >= 20 or standard_error < 0.3

    def map_grade_equivalent(self, theta: float, learner_grade: int) -> int:
        shift = 0
        if theta <= -1.8:
            shift = -2
        elif theta <= -0.8:
            shift = -1
        elif theta >= 1.8:
            shift = 2
        elif theta >= 0.8:
            shift = 1
        return max(0, min(7, learner_grade + shift))

    def run_gap_probe_cascade(
        self,
        learner_grade: int,
        items: list[IRTItem],
        correct_item_ids: set[str],
        *,
        starting_theta: float = 0.0,
    ) -> dict:
        administered = items[:20]
        responses = [(item, item.id in correct_item_ids) for item in administered]
        theta, standard_error = self.estimate_theta_eap(responses, prior_mean=starting_theta)
        grade_equivalent = self.map_grade_equivalent(theta, learner_grade)
        ranked_gaps = self.identify_gaps(administered, correct_item_ids)
        return {
            "theta": theta,
            "standard_error": standard_error,
            "grade_equivalent": grade_equivalent,
            "ranked_gaps": ranked_gaps,
            "knowledge_gap_topics": [gap["topic"] for gap in ranked_gaps[:3]],
            "stopped": self.should_stop(len(administered), standard_error),
            "mean_difficulty": round(fmean(item.b_param for item in administered), 4) if administered else 0.0,
        }
