"""
EduBoost SA — IRT Engine
Item Response Theory (2PL model) for adaptive diagnostic assessment.
Core educational IP — migrated from app/api/ml/ into modules/diagnostics/.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq  # type: ignore[import-untyped]

from app.core.metrics import irt_computation_seconds

logger = logging.getLogger(__name__)

# 2PL IRT model constants
_D = 1.702          # Scaling constant (logistic approximation to normal ogive)
_MAX_ITEMS = 30     # Maximum items per adaptive session
_MIN_ITEMS = 5      # Minimum before early stopping
_SE_THRESHOLD = 0.3 # Stop when standard error drops below this


@dataclass
class IRTItem:
    item_id: str
    difficulty: float       # b parameter: logit scale, typically -3 to +3
    discrimination: float   # a parameter: typically 0.5 to 2.5
    guessing: float = 0.0   # c parameter (3PL — set 0 for 2PL)


@dataclass
class IRTSession:
    items: list[IRTItem] = field(default_factory=list)
    responses: list[bool] = field(default_factory=list)
    ability_estimates: list[float] = field(default_factory=list)
    standard_errors: list[float] = field(default_factory=list)

    @property
    def current_ability(self) -> float:
        return self.ability_estimates[-1] if self.ability_estimates else 0.0

    @property
    def current_se(self) -> float:
        return self.standard_errors[-1] if self.standard_errors else 99.0

    @property
    def is_complete(self) -> bool:
        n = len(self.responses)
        if n >= _MAX_ITEMS:
            return True
        if n >= _MIN_ITEMS and self.current_se <= _SE_THRESHOLD:
            return True
        return False


class IRTEngine:
    """
    2-Parameter Logistic IRT Model for adaptive diagnostics.
    Implements Maximum Likelihood Estimation (MLE) for ability estimation.
    """

    # ── Probability ──────────────────────────────────────────────────────────

    def probability_correct(self, ability: float, difficulty: float, discrimination: float = 1.0) -> float:
        """P(correct | ability, difficulty, discrimination) — 2PL logistic function."""
        exponent = _D * discrimination * (ability - difficulty)
        return 1.0 / (1.0 + math.exp(-exponent))

    # ── Ability Estimation ────────────────────────────────────────────────────

    def estimate_ability(
        self,
        responses: list[bool],
        difficulties: list[float],
        discriminations: list[float] | None = None,
    ) -> float:
        """
        MLE ability estimation given a response pattern.
        Falls back to 0.0 if all correct or all incorrect (indeterminate).
        """
        if not responses:
            return 0.0
        if all(responses):
            return min(max(d for d in difficulties) + 1.5, 4.0)
        if not any(responses):
            return max(min(d for d in difficulties) - 1.5, -4.0)

        discs = discriminations or [1.0] * len(responses)

        def log_likelihood(theta: float) -> float:
            ll = 0.0
            for resp, b, a in zip(responses, difficulties, discs):
                p = self.probability_correct(theta, b, a)
                p = max(min(p, 1.0 - 1e-10), 1e-10)
                ll += math.log(p) if resp else math.log(1.0 - p)
            return ll

        def score_function(theta: float) -> float:
            """Derivative of log-likelihood (score equation)."""
            total = 0.0
            for resp, b, a in zip(responses, difficulties, discs):
                p = self.probability_correct(theta, b, a)
                w = _D * a * p * (1.0 - p)
                total += w * (int(resp) - p) / max(p * (1.0 - p), 1e-10)
            return total

        try:
            ability = brentq(score_function, -6.0, 6.0, xtol=1e-4, maxiter=100)
        except ValueError:
            # Score function doesn't change sign — use max likelihood search
            abilities = np.linspace(-4.0, 4.0, 160)
            lls = [log_likelihood(float(t)) for t in abilities]
            ability = float(abilities[int(np.argmax(lls))])

        return round(ability, 4)

    def standard_error(
        self,
        ability: float,
        difficulties: list[float],
        discriminations: list[float] | None = None,
    ) -> float:
        """Fisher information-based standard error of ability estimate."""
        discs = discriminations or [1.0] * len(difficulties)
        information = sum(
            (_D * a) ** 2 * p * (1 - p)
            for b, a in zip(difficulties, discs)
            for p in [self.probability_correct(ability, b, a)]
        )
        if information <= 0:
            return 99.0
        return round(1.0 / math.sqrt(information), 4)

    # ── Item Selection ────────────────────────────────────────────────────────

    def select_next_item(
        self,
        current_ability: float,
        item_bank: list[IRTItem],
        administered_ids: set[str],
    ) -> IRTItem | None:
        """
        Maximum Fisher Information item selection.
        Chooses the item providing most information at current ability estimate.
        """
        available = [item for item in item_bank if item.item_id not in administered_ids]
        if not available:
            return None

        def fisher_info(item: IRTItem) -> float:
            p = self.probability_correct(current_ability, item.difficulty, item.discrimination)
            return (_D * item.discrimination) ** 2 * p * (1.0 - p)

        return max(available, key=fisher_info)

    # ── Session Update ────────────────────────────────────────────────────────

    def update_session(
        self,
        session: IRTSession,
        item: IRTItem,
        response: bool,
    ) -> IRTSession:
        """Record a response and update ability estimate."""
        import time
        start = time.perf_counter()

        session.items.append(item)
        session.responses.append(response)

        difficulties = [i.difficulty for i in session.items]
        discriminations = [i.discrimination for i in session.items]
        ability = self.estimate_ability(session.responses, difficulties, discriminations)
        se = self.standard_error(ability, difficulties, discriminations)

        session.ability_estimates.append(ability)
        session.standard_errors.append(se)

        duration = time.perf_counter() - start
        irt_computation_seconds.observe(duration)

        logger.debug(
            "IRT update: items=%d ability=%.3f se=%.3f complete=%s",
            len(session.responses), ability, se, session.is_complete,
        )
        return session

    # ── Ability Interpretation ────────────────────────────────────────────────

    @staticmethod
    def interpret_ability(theta: float) -> dict[str, str]:
        """
        Map IRT theta score to a learner-friendly performance band.
        Used for parent portal and study plan generation.
        """
        if theta >= 2.0:
            return {"band": "advanced", "label": "Advanced", "emoji": "🌟"}
        if theta >= 0.5:
            return {"band": "proficient", "label": "Proficient", "emoji": "✅"}
        if theta >= -0.5:
            return {"band": "developing", "label": "Developing", "emoji": "📈"}
        if theta >= -2.0:
            return {"band": "foundational", "label": "Foundational", "emoji": "🔧"}
        return {"band": "beginning", "label": "Beginning", "emoji": "🌱"}
