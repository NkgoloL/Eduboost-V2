"""
app/services/study_plan_updater.py
─────────────────────────────────────────────────────────────────────────────
Phase 4: Study Plan Weak-Topic Prioritisation (P4-08)

After a diagnostic session completes, the IRT engine produces an ability
estimate (θ) for the diagnosed caps_ref. This service takes that result and
updates the learner's study plan so that:

    1. Topics where θ < 0 (below grade level) are promoted to the top of the
       upcoming study queue.
    2. Topics where θ ≥ 0 are flagged as "on-track" and deprioritised.
    3. Each topic entry in the plan stores the latest ability estimate, the
       standard error, and the timestamp so it can be trended over time.

The study plan is stored in the `study_plans` table via StudyPlanRepository.
This service only updates ability estimates and priority ordering — it does
not regenerate lesson content.

Usage:
    updater = StudyPlanUpdater(study_plan_repo)
    await updater.apply_diagnostic_result(learner_id, session_result)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)

# Threshold below which a topic is considered a priority gap
PRIORITY_GAP_THRESHOLD = 0.0        # θ < 0 → needs remediation
STRONG_GAP_THRESHOLD   = -1.0       # θ < -1 → urgent re-teaching


class StudyPlanUpdater:
    """
    Updates a learner's study plan using IRT diagnostic results.

    Depends on StudyPlanRepository, which is injected at construction time.
    The repository interface is assumed to provide:
        get_plan(learner_id)              → dict | None
        upsert_topic_entry(learner_id, entry: dict) → None
        reorder_topics(learner_id, ordered_refs: list[str]) → None
    """

    def __init__(self, study_plan_repo: Any) -> None:
        self._repo = study_plan_repo

    async def apply_diagnostic_result(
        self,
        learner_id: UUID,
        session_result: dict,
    ) -> dict:
        """
        Ingest a diagnostic session result and update the study plan.

        Args:
            learner_id:     UUID of the learner whose plan is being updated.
            session_result: Output from DiagnosticSessionService.finalise_session().

        Returns:
            Updated topic entry dict (useful for API responses and tests).
        """
        caps_ref       = session_result["caps_ref"]
        theta          = float(session_result["theta"])
        se             = float(session_result["standard_error"])
        below_grade    = bool(session_result["below_grade_level"])
        misconceptions = list(session_result.get("misconception_tags", []))
        completed_at   = session_result.get("completed_at", datetime.now(timezone.utc).isoformat())

        # Build the updated topic entry
        priority = self._compute_priority(theta)
        entry = {
            "caps_ref":           caps_ref,
            "theta":              theta,
            "standard_error":     se,
            "below_grade_level":  below_grade,
            "misconception_tags": misconceptions,
            "priority":           priority,
            "last_diagnosed_at":  completed_at,
            "needs_lesson":       below_grade,
        }

        # Persist the topic entry (upsert — create or update)
        await self._repo.upsert_topic_entry(learner_id, entry)

        logger.info(
            "Study plan updated for learner %s: caps_ref=%s θ=%.3f priority=%s needs_lesson=%s",
            str(learner_id)[:8], caps_ref, theta, priority, below_grade,
        )

        # Reorder the full plan so priority topics surface first
        await self._reorder_plan(learner_id)

        return entry

    async def get_prioritised_topics(self, learner_id: UUID) -> list[dict]:
        """
        Return the learner's study plan topics sorted by priority (urgent first).

        Priority order:
            1. urgent   — θ < -1.0 (severe gap, foundational re-teaching needed)
            2. high     — θ < 0.0  (below grade level, targeted practice needed)
            3. medium   — θ ≥ 0.0  (on track, extension or light review)
            4. low      — no diagnostic data yet (not yet assessed)

        This ordering drives what the study plan dashboard displays to the
        learner and guardian, and what lesson the platform serves next.
        """
        plan = await self._repo.get_plan(learner_id)
        if plan is None:
            return []

        topics: list[dict] = plan.get("topics", [])
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        topics.sort(key=lambda t: priority_order.get(t.get("priority", "low"), 3))
        return topics

    # ─── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _compute_priority(theta: float) -> str:
        """
        Map an ability estimate to a priority label.

        Labels are used for study plan ordering and displayed to guardians.
        """
        if theta < STRONG_GAP_THRESHOLD:
            return "urgent"     # θ < -1.0: significant foundational gap
        elif theta < PRIORITY_GAP_THRESHOLD:
            return "high"       # θ < 0.0:  below grade level
        else:
            return "medium"     # θ ≥ 0.0:  on or above grade level

    async def _reorder_plan(self, learner_id: UUID) -> None:
        """
        After updating a topic entry, reorder the full plan by priority so
        the study plan dashboard always reflects the current urgency ranking.
        """
        topics = await self.get_prioritised_topics(learner_id)
        ordered_refs = [t["caps_ref"] for t in topics]
        if ordered_refs:
            await self._repo.reorder_topics(learner_id, ordered_refs)
            logger.debug(
                "Reordered study plan for learner %s: %s",
                str(learner_id)[:8], ordered_refs,
            )
