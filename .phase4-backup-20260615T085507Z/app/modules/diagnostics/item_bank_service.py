"""
Item Bank Service — P2-08 / P3 Refactor
=======================================
Application-layer service that mediates between the IRT engine, the repository,
and the diagnostic session flow.
"""

from __future__ import annotations

import math
import uuid
from typing import Sequence, Optional

from app.domain.content_coverage import ContentLayer
from app.models.diagnostic_item import DiagnosticItem
from app.repositories.item_bank_repository import ItemBankRepository
from app.services.content_scope_registry import ContentScopeRegistry


DEFAULT_CONTENT_SCOPE_ID = "grade4_mathematics_en"

# Ability neighbourhood window for IRT-informed selection
_THETA_WINDOW = 1.0


class ItemSelectionError(Exception):
    """Raised when no eligible item can be found for a learner."""


def _3pl_probability(theta: float, a: float, b: float, c: float) -> float:
    """3-parameter logistic IRT probability of a correct response."""
    exponent = -1.7 * float(a) * (theta - float(b))
    exponent = max(-500.0, min(500.0, exponent))
    return float(c) + (1.0 - float(c)) / (1.0 + math.exp(exponent))


def _fisher_information(theta: float, a: float, b: float, c: float) -> float:
    """Fisher information for a 3PL item at ability theta."""
    p = _3pl_probability(theta, a, b, c)
    q = 1.0 - p
    if p < 1e-10 or q < 1e-10:
        return 0.0
    return (1.7 * float(a) * (p - float(c)) / (1.0 - float(c))) ** 2 * q / p


class ItemBankService:
    """
    Application-layer service for the diagnostic item bank.
    Inject an ItemBankRepository instance.
    """

    def __init__(
        self,
        repo: ItemBankRepository,
        coverage_targets: ContentScopeRegistry | None = None,
        scope_id: str = DEFAULT_CONTENT_SCOPE_ID,
    ) -> None:
        self.repo = repo
        self._repo = repo
        self.coverage_targets = coverage_targets or ContentScopeRegistry()
        self.scope_id = scope_id

    # ─── Public API ──────────────────────────────────────────────────────────

    async def select_item_for_learner(
        self,
        caps_ref: str,
        learner_id: uuid.UUID,
        theta: float = 0.0,
        exclude_ids: Optional[set[uuid.UUID]] = None,
        review_status: str = "approved",
    ) -> Optional[DiagnosticItem]:
        """
        Select the single best next item for this learner using IRT-informed,
        exposure-capped selection.
        """
        # Fetch unexposed items in the ability neighbourhood
        candidates = await self.repo.get_unexposed_items(
            learner_id=learner_id,
            caps_ref=caps_ref,
            min_b_param=theta - _THETA_WINDOW,
            max_b_param=theta + _THETA_WINDOW,
            review_status=review_status,
            limit=30,
        )

        if not candidates:
            # Expand to full unexposed pool (ignore ability window)
            candidates = await self.repo.get_unexposed_items(
                learner_id=learner_id,
                caps_ref=caps_ref,
                review_status=review_status,
                limit=40,
            )

        exclude_ids = exclude_ids or set()
        candidates = [item for item in candidates if item.item_id not in exclude_ids]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: _fisher_information(
                theta,
                float(item.discrimination_a or 1.0),
                float(item.difficulty_b or 0.0),
                float(item.guessing_c or 0.25),
            ),
        )

    async def record_item_served(
        self,
        item_id: uuid.UUID,
        learner_id: uuid.UUID,
        *,
        session_id: Optional[uuid.UUID] = None,
    ) -> None:
        """Record that an item was served and increment its counter."""
        await self.repo.record_exposure(item_id, learner_id, session_id=session_id)

    async def get_coverage_summary(
        self,
        caps_refs: Optional[list[str]] = None,
        *,
        scope_id: str | None = None,
    ) -> dict[str, dict]:
        """Return per-caps_ref item counts enriched with registry-backed targets."""
        active_scope_id = scope_id or self.scope_id
        requested_refs = caps_refs or self.coverage_targets.get_scope_caps_refs(active_scope_id)
        summaries = await self.repo.get_coverage_summary(requested_refs)

        for ref in requested_refs:
            s = summaries.setdefault(ref, {"caps_ref": ref, "approved": 0, "total": 0})
            target = self.coverage_targets.get_coverage_target(
                active_scope_id,
                ref,
                ContentLayer.DIAGNOSTIC_ITEMS,
            )
            s["target"] = target
            approved = s.get("approved", 0)
            s["coverage_ratio"] = round(approved / target, 4) if target else 0.0

        return summaries

    async def get_exposure_heatmap(self, caps_ref: str) -> list[dict]:
        """Return per-item exposure utilisation for a CAPS reference."""
        return await self.repo.get_exposure_heatmap(caps_ref)

    async def is_scope_ready(self, scope_id: str | None = None) -> bool:
        """Returns True when all configured diagnostic targets for a scope are met."""
        active_scope_id = scope_id or self.scope_id
        summaries = await self.get_coverage_summary(
            caps_refs=self.coverage_targets.get_scope_caps_refs(active_scope_id),
            scope_id=active_scope_id,
        )
        return all(s["coverage_ratio"] >= 1.0 for s in summaries.values())

    async def is_launch_ready(self) -> bool:
        """Compatibility wrapper for the default Grade 4 Mathematics launch scope."""
        return await self.is_scope_ready(DEFAULT_CONTENT_SCOPE_ID)

    async def mark_item_reviewed(
        self,
        item_id: uuid.UUID,
        new_status: str | uuid.UUID,
        reviewer_id: Optional[uuid.UUID | str] = None,
        quality_score: Optional[float] = None,
    ) -> Optional[DiagnosticItem]:
        """Transition item review status."""
        if isinstance(new_status, uuid.UUID) and isinstance(reviewer_id, str):
            new_status, reviewer_id = reviewer_id, new_status

        # Enforce audit trail requirement
        if new_status in {"human_reviewed", "approved"} and reviewer_id is None:
            raise ValueError(
                f"reviewer_id is required to transition an item to '{new_status}'"
            )

        return await self.repo.update_review_status(
            item_id=item_id,
            new_status=new_status,
            reviewer_id=reviewer_id,
            quality_score=quality_score,
        )


# ---------------------------------------------------------------------------
# IRT Utilities (Module-level for legacy support and standalone use)
# ---------------------------------------------------------------------------

def fisher_information_3pl(
    theta: float,
    a: float,
    b: float,
    c: float,
) -> float:
    """
    Fisher information for the 3-parameter logistic IRT model at ability θ.
    """
    # D = 1.702 (logistic vs normal scaling)
    exp_term = math.exp(-1.702 * a * (theta - b))
    p_theta = c + (1 - c) / (1 + exp_term)
    q_theta = 1 - p_theta

    if p_theta < 1e-10 or q_theta < 1e-10:
        return 0.0

    return (1.702 * a * (p_theta - c) / (1 - c)) ** 2 * q_theta / p_theta


def select_maximum_information_item(
    candidates: Sequence[DiagnosticItem],
    theta: float,
) -> DiagnosticItem:
    """Full maximum Fisher information item selection."""
    if not candidates:
        raise ValueError("Candidate pool is empty.")

    best_item = candidates[0]
    best_info = -1.0

    for item in candidates:
        info = fisher_information_3pl(
            theta=theta,
            a=float(item.discrimination_a or 1.0),
            b=float(item.difficulty_b or 0.0),
            c=float(item.guessing_c or 0.25),
        )
        if info > best_info:
            best_info = info
            best_item = item

    return best_item
