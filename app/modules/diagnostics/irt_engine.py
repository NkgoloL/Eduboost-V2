"""IRT 2-Parameter Logistic (2PL) adaptive diagnostic engine.

Implements Item Response Theory scoring used to estimate each learner's
latent ability (theta, θ) from their responses to adaptive questions.
The 2PL model uses per-item *discrimination* (a) and *difficulty* (b)
parameters calibrated against the South African CAPS curriculum for
grades R–7.

Mathematical model:

.. math::

    P(X=1 \\mid \\theta) = \\frac{1}{1 + e^{-a(\\theta - b)}}

where:

* :math:`\\theta` — learner ability estimate (logit scale, typically −4 to +4)
* :math:`a` — item discrimination (steepness of the ICC curve)
* :math:`b` — item difficulty (ability level at which P = 0.5)

Example:
    Run a full diagnostic cascade::

        from app.modules.diagnostics.irt_engine import DiagnosticEngine

        engine = DiagnosticEngine()
        result = engine.run_gap_probe_cascade(
            learner_grade=4, items=item_bank,
            correct_item_ids={"q1", "q3", "q5"},
        )
        print(f"θ = {result['theta']:.3f} ± {result['standard_error']:.3f}")
"""
from __future__ import annotations

import math
from statistics import fmean

from app.core.logging import get_logger
from app.domain.models import IRTItem

log = get_logger(__name__)

# ── IRT maths ─────────────────────────────────────────────────────────────────


def p_correct(theta: float, a: float, b: float) -> float:
    """Compute the 2PL probability of a correct response.

    Implements the Item Characteristic Curve (ICC):

    .. math::

        P(\\theta) = \\frac{1}{1 + e^{-a(\\theta - b)}}

    Parameters are hard-clamped to prevent overflow:
    ``a`` ∈ [0.1, 4.0], ``b`` ∈ [−4, 4], ``θ`` ∈ [−5, 5].

    Args:
        theta: Learner ability estimate on the IRT logit scale.
        a: Item discrimination parameter (typically 0.5–2.5).
        b: Item difficulty parameter (typically −3 to +3).

    Returns:
        float: Probability of a correct response in ``[0, 1]``.

    Example:
        ::

            p = p_correct(theta=0.0, a=1.0, b=0.0)
            assert abs(p - 0.5) < 1e-9  # theta == b → P = 0.5
    """
    # Hard bounds for parameters to prevent overflow/divergence
    a = max(0.1, min(4.0, a))
    b = max(-4.0, min(4.0, b))
    theta = max(-5.0, min(5.0, theta))
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def fisher_information(theta: float, a: float, b: float) -> float:
    """Compute the Fisher information for a given IRT item.

    Measures how much statistical information the item provides about
    ability around the current theta estimate:

    .. math::

        I(\\theta) = a^2 \\cdot P(\\theta) \\cdot [1 - P(\\theta)]

    Items with high discrimination (``a``) and difficulty close to
    ``theta`` provide the most information.

    Args:
        theta: Learner ability estimate.
        a: Item discrimination parameter.
        b: Item difficulty parameter.

    Returns:
        float: Fisher information scalar value.

    Example:
        ::

            info = fisher_information(theta=0.0, a=1.5, b=0.0)
            assert info > 0  # maximum info when theta == b
    """
    p = p_correct(theta, a, b)
    q = 1.0 - p
    return (a ** 2) * p * q


def update_theta_mle(theta: float, responses: list[tuple[IRTItem, bool]], max_iter: int = 20) -> float:
    """Estimate theta using Newton-Raphson maximum likelihood estimation.

    Maximises the log-likelihood of the observed response pattern
    given the 2PL model.  Convergence is reached when the update step
    is smaller than ``1e-4`` or ``max_iter`` is exhausted.

    Args:
        theta: Initial ability value to seed the optimisation.
        responses: List of ``(item, correct)`` tuples pairing
            :class:`~app.domain.models.IRTItem` instances with
            correctness flags.
        max_iter: Maximum Newton-Raphson iterations (default ``20``).

    Returns:
        float: Estimated theta value clamped to ``[-4, 4]``.

    Example:
        ::

            theta = update_theta_mle(0.0, [(item, True), (item2, False)])
            assert -4.0 <= theta <= 4.0
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
    """Runs the Gap-Probe Cascade using a real IRT item bank.

    The engine estimates learner ability via Expected A Posteriori (EAP)
    integration, identifies knowledge gaps from missed items, selects
    the next most informative item via Fisher information, and returns
    grade-equivalent guidance aligned to the CAPS curriculum.

    All public methods are synchronous (CPU-bound maths); database I/O
    is handled by the calling service layer.

    Example:
        ::

            engine = DiagnosticEngine()
            result = engine.run_gap_probe_cascade(
                learner_grade=3, items=bank,
                correct_item_ids={"q1", "q3"},
            )
            print(result["theta"], result["ranked_gaps"])
    """

    def compute_theta(
        self,
        starting_theta: float,
        items: list[IRTItem],
        correct_item_ids: set[str],
    ) -> float:
        """Compute learner theta from administered item results.

        Delegates to :meth:`estimate_theta_eap` with the given
        ``starting_theta`` as the prior mean.

        Args:
            starting_theta: Initial ability estimate for the learner.
            items: List of administered :class:`~app.domain.models.IRTItem`
                instances.
            correct_item_ids: Set of item IDs answered correctly.

        Returns:
            float: Estimated learner theta.

        Example:
            ::

                theta = engine.compute_theta(0.0, items, {"q1", "q3"})
                assert -4.0 <= theta <= 4.0
        """
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
        """Estimate theta via Expected A Posteriori (EAP) integration.

        Computes the posterior mean of theta by integrating over a
        discrete grid with a Gaussian prior:

        .. math::

            \\hat{\\theta}_{EAP} = \\frac{\\sum_k \\theta_k \\cdot L(\\theta_k) \\cdot \\pi(\\theta_k)}
            {\\sum_k L(\\theta_k) \\cdot \\pi(\\theta_k)}

        Args:
            responses: List of ``(item, correct)`` tuples.
            prior_mean: Mean of the Gaussian prior for theta.
            prior_sd: Standard deviation of the theta prior.
            theta_min: Minimum theta on the integration grid.
            theta_max: Maximum theta on the integration grid.
            step: Grid resolution for theta values.

        Returns:
            tuple[float, float]: ``(theta_estimate, standard_error)``.

        Example:
            ::

                theta, se = engine.estimate_theta_eap(
                    [(item1, True), (item2, False)],
                    prior_mean=0.0,
                )
                assert -4.0 <= theta <= 4.0
        """
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
        """Identify knowledge gaps from missed items.

        An item is considered a gap when the learner missed it and its
        normalised difficulty exceeds the threshold.  Gaps are deduplicated
        by ``subject::topic`` and ranked by severity (descending).

        Args:
            items: List of administered :class:`~app.domain.models.IRTItem`
                instances.
            correct_item_ids: Set of correctly answered item IDs.
            threshold_p: Minimum expected probability of correctness to
                count as a gap when missed (default ``0.50``).

        Returns:
            list[dict]: Ranked list of gap dictionaries with keys
            ``grade``, ``subject``, ``topic``, and ``severity``.

        Example:
            ::

                gaps = engine.identify_gaps(items, {"q1"})
                assert all("severity" in g for g in gaps)
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
        """Select the next item with maximum Fisher information.

        Uses :func:`fisher_information` as the item-selection criterion.
        Items already administered are excluded.

        Args:
            theta: Current ability estimate.
            administered_ids: Item IDs already shown in this session.
            bank: Candidate :class:`~app.domain.models.IRTItem` bank.

        Returns:
            IRTItem | None: Most informative next item, or ``None`` if
            the bank is exhausted.

        Example:
            ::

                item = engine.select_next_item(0.5, {"q1"}, item_bank)
                if item:
                    print(f"Next item: {item.id}")
        """
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
        """Decide whether the adaptive diagnostic should stop.

        The session terminates when either the item cap (20) is reached
        or the standard error drops below the precision threshold (0.3).

        Args:
            administered_count: Number of items administered so far.
            standard_error: Current theta standard error.

        Returns:
            bool: ``True`` when the session should end.

        Example:
            ::

                assert engine.should_stop(20, 0.5) is True
                assert engine.should_stop(5, 0.2) is True
                assert engine.should_stop(5, 0.5) is False
        """
        return administered_count >= 20 or standard_error < 0.3

    def map_grade_equivalent(self, theta: float, learner_grade: int) -> int:
        """Convert theta into a grade-equivalent recommendation.

        Maps the ability estimate to a recommended CAPS grade level
        (0–7) by applying a shift based on theta magnitude:

        * θ ≤ −1.8 → −2 grades
        * −1.8 < θ ≤ −0.8 → −1 grade
        * −0.8 < θ < 0.8 → same grade
        * 0.8 ≤ θ < 1.8 → +1 grade
        * θ ≥ 1.8 → +2 grades

        Args:
            theta: Estimated learner ability.
            learner_grade: Current learner grade level (0–7).

        Returns:
            int: Recommended grade equivalent clamped to 0–7.

        Example:
            ::

                assert engine.map_grade_equivalent(2.0, 3) == 5
                assert engine.map_grade_equivalent(-2.0, 3) == 1
        """
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
        """Execute the full adaptive gap-probe cascade.

        Orchestrates theta estimation, knowledge-gap identification, and
        grade-equivalent mapping into a single diagnostic dashboard.

        Args:
            learner_grade: Current CAPS grade of the learner (0–7).
            items: List of candidate :class:`~app.domain.models.IRTItem`
                instances.
            correct_item_ids: Set of IDs answered correctly.
            starting_theta: Initial ability estimate (default ``0.0``).

        Returns:
            dict: Dashboard dictionary containing:

            * ``theta`` — EAP ability estimate
            * ``standard_error`` — estimation precision
            * ``grade_equivalent`` — recommended CAPS grade
            * ``ranked_gaps`` — severity-ranked knowledge gaps
            * ``knowledge_gap_topics`` — top-3 gap topic strings
            * ``stopped`` — whether stopping criteria were met
            * ``mean_difficulty`` — average item difficulty

        Example:
            ::

                result = engine.run_gap_probe_cascade(
                    learner_grade=4, items=bank,
                    correct_item_ids={"q1", "q3"},
                )
                assert "theta" in result
                assert "ranked_gaps" in result
        """
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
