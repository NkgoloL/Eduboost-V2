"""IRT 2-Parameter Logistic (2PL) adaptive diagnostic engine.

Implements Item Response Theory scoring used to estimate each learner's
latent ability (theta, θ) from their responses to adaptive questions.
The 2PL model uses per-item *discrimination* (a) and *difficulty* (b)
parameters calibrated against the South African CAPS curriculum.

Mathematical model:

.. math::

    P(X=1 \\mid \\theta) = \\frac{1}{1 + e^{-a(\\theta - b)}}

where:

* :math:`\\theta` — learner ability estimate (logit scale, typically −4 to +4)
* :math:`a` — item discrimination (steepness of the ICC curve)
* :math:`b` — item difficulty (ability level at which P = 0.5)

Example:
    Score a short adaptive session::

        from app.modules.diagnostics.irt_engine import IRTEngine, ItemResponse

        responses = [
            ItemResponse(item_id="q1", a=1.2, b=0.5, correct=True),
            ItemResponse(item_id="q2", a=0.9, b=1.0, correct=False),
        ]
        theta, se = IRTEngine.estimate_theta(responses)
        print(f"θ = {theta:.3f} ± {se:.3f}")
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class IRTItem:
    """A single item in the adaptive question bank.

    Attributes:
        item_id: Unique database identifier for the question.
        grade: South African school grade (``"R"`` through ``"7"``).
        subject: CAPS subject code (e.g. ``"MATH"``, ``"ENG"``, ``"NS"``).
        a: Discrimination parameter — controls how sharply the item
            differentiates between ability levels (typically 0.5–2.5).
        b: Difficulty parameter — the theta level at which a learner has
            a 50% probability of answering correctly (typically −3 to +3).
        content: The question text shown to the learner.
        options: Multiple-choice option strings (A–D).
        correct_index: Zero-based index of the correct option.

    Example:
        ::

            item = IRTItem(
                item_id="math-gr3-001",
                grade="3",
                subject="MATH",
                a=1.1,
                b=0.2,
                content="What is 7 × 8?",
                options=["54", "56", "48", "64"],
                correct_index=1,
            )
    """

    item_id: str
    grade: str
    subject: str
    a: float
    b: float
    content: str = ""
    options: List[str] = field(default_factory=list)
    correct_index: int = 0


@dataclass
class ItemResponse:
    """A learner's response to a single adaptive item.

    Attributes:
        item_id: Identifier linking back to :class:`IRTItem`.
        a: Discrimination parameter (copied from the item for scoring).
        b: Difficulty parameter (copied from the item for scoring).
        correct: ``True`` if the learner answered correctly.
        response_time_ms: Optional response latency in milliseconds.

    Example:
        ::

            resp = ItemResponse(item_id="math-gr3-001", a=1.1, b=0.2, correct=True)
    """

    item_id: str
    a: float
    b: float
    correct: bool
    response_time_ms: Optional[int] = None


class IRTEngine:
    """Stateless IRT 2PL scoring and item-selection engine.

    All public methods are static/class methods — no instantiation needed.
    Theta estimation uses maximum likelihood estimation (MLE) via
    Newton-Raphson iteration.

    Example:
        ::

            responses = [ItemResponse("q1", 1.0, 0.0, True)]
            theta, se = IRTEngine.estimate_theta(responses)
    """

    MAX_ITERATIONS: int = 50
    """Maximum Newton-Raphson iterations before early exit."""

    CONVERGENCE_TOL: float = 1e-6
    """Convergence tolerance for the theta update step."""

    @staticmethod
    def p(theta: float, a: float, b: float) -> float:
        """Compute the 2PL probability of a correct response.

        Implements the Item Characteristic Curve (ICC):

        .. math::

            P(\\theta) = \\frac{1}{1 + e^{-a(\\theta - b)}}

        Args:
            theta: Current ability estimate.
            a: Item discrimination parameter.
            b: Item difficulty parameter.

        Returns:
            float: Probability of a correct response in ``[0, 1]``.

        Example:
            ::

                p = IRTEngine.p(theta=0.0, a=1.0, b=0.0)
                assert abs(p - 0.5) < 1e-9
        """
        return 1.0 / (1.0 + math.exp(-a * (theta - b)))

    @classmethod
    def estimate_theta(
        cls,
        responses: List[ItemResponse],
        initial_theta: float = 0.0,
    ) -> Tuple[float, float]:
        """Estimate learner ability (theta) via MLE using Newton-Raphson.

        Maximises the log-likelihood of the observed response pattern
        given the 2PL model.  Returns both the point estimate and the
        standard error derived from the observed Fisher information.

        Args:
            responses: List of :class:`ItemResponse` objects from the
                current diagnostic session.
            initial_theta: Starting value for the Newton-Raphson search.
                Defaults to 0.0 (average ability).

        Returns:
            Tuple[float, float]: ``(theta_hat, standard_error)`` where
            ``theta_hat`` is the MLE estimate and ``standard_error``
            quantifies estimation precision.

        Raises:
            ValueError: If ``responses`` is empty.

        Example:
            ::

                responses = [
                    ItemResponse("q1", 1.2, 0.5, True),
                    ItemResponse("q2", 0.8, 1.5, False),
                    ItemResponse("q3", 1.0, 0.0, True),
                ]
                theta, se = IRTEngine.estimate_theta(responses)
                assert -4.0 < theta < 4.0
        """
        if not responses:
            raise ValueError("Cannot estimate theta from an empty response list.")

        theta = initial_theta
        for _ in range(cls.MAX_ITERATIONS):
            grad = 0.0
            hess = 0.0
            for r in responses:
                p = cls.p(theta, r.a, r.b)
                u = 1 if r.correct else 0
                grad += r.a * (u - p)
                hess -= r.a ** 2 * p * (1 - p)

            if abs(hess) < 1e-12:
                break
            update = grad / hess
            theta -= update
            if abs(update) < cls.CONVERGENCE_TOL:
                break

        # Standard error from observed information
        info = sum(r.a ** 2 * cls.p(theta, r.a, r.b) * (1 - cls.p(theta, r.a, r.b))
                   for r in responses)
        se = 1.0 / math.sqrt(max(info, 1e-12))
        return round(theta, 6), round(se, 6)

    @staticmethod
    def select_next_item(
        theta: float,
        item_pool: List[IRTItem],
        administered_ids: Optional[List[str]] = None,
    ) -> Optional[IRTItem]:
        """Select the most informative un-administered item for the current theta.

        Uses maximum Fisher information as the item-selection criterion.
        Items already administered (``administered_ids``) are excluded.

        Args:
            theta: Current theta estimate for the learner.
            item_pool: All available items eligible for selection.
            administered_ids: IDs of items already shown in this session.

        Returns:
            Optional[IRTItem]: The item with the highest information at
            ``theta``, or ``None`` if no items remain.

        Example:
            ::

                pool = [
                    IRTItem("q1", "3", "MATH", 1.0, 0.0),
                    IRTItem("q2", "3", "MATH", 1.5, 0.5),
                ]
                item = IRTEngine.select_next_item(0.3, pool, administered_ids=["q1"])
                assert item is not None
                assert item.item_id == "q2"
        """
        seen = set(administered_ids or [])
        candidates = [i for i in item_pool if i.item_id not in seen]
        if not candidates:
            return None

        def fisher_info(item: IRTItem) -> float:
            p = 1.0 / (1.0 + math.exp(-item.a * (theta - item.b)))
            return item.a ** 2 * p * (1 - p)

        return max(candidates, key=fisher_info)
