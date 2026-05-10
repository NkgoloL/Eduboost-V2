from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.modules.diagnostics.irt_engine import eap_update_3pl
from app.modules.diagnostics.item_selection_service import ItemSelectionService
from app.modules.diagnostics.session_recovery_service import DiagnosticSessionSnapshot, SessionRecoveryService
from app.modules.diagnostics.termination_service import TerminationService
from app.modules.progress.mastery_model import compute_mastery_score, label_for_score


@dataclass
class DiagnosticResponseResult:
    session_id: str
    theta: float
    se_estimate: float
    items_served: int
    should_complete: bool
    termination_reason: str | None
    gap_topics: list[str]
    misconception_tags: list[str]


class DiagnosticSessionService:
    """Orchestrates diagnostic start, item serving, responses, recovery, and completion."""

    def __init__(self, *, item_bank: Any = None, session_repository: Any = None, mastery_repository: Any = None, recovery_service: SessionRecoveryService | None = None) -> None:
        self.item_bank = item_bank
        self.sessions = session_repository
        self.mastery = mastery_repository
        self.recovery = recovery_service or SessionRecoveryService()
        self.selector = ItemSelectionService()
        self.terminator = TerminationService()

    async def start_session(self, learner_id: str | UUID, caps_ref: str, *, theta: float = 0.0) -> DiagnosticSessionSnapshot:
        if self.sessions:
            row = await self.sessions.create_session(learner_id, theta=theta, se=1.0, caps_ref=caps_ref)
            session_id = str(row.id)
        else:
            session_id = str(uuid4())
        snap = DiagnosticSessionSnapshot(session_id=session_id, learner_id=str(learner_id), caps_ref=caps_ref, session_state="item_serving", theta=theta)
        await self.recovery.write_session_snapshot(session_id, snap)
        return snap

    async def recover_session(self, session_id: str | UUID) -> DiagnosticSessionSnapshot | None:
        snap = await self.recovery.read_session_snapshot(str(session_id))
        if snap:
            snap.session_state = "recovered"
            await self.recovery.write_session_snapshot(str(session_id), snap)
        return snap

    async def get_next_item(self, session_id: str | UUID, items: list[object] | None = None) -> object | None:
        snap = await self.recovery.read_session_snapshot(str(session_id))
        if snap is None:
            return None
        pool = items or []
        selected = self.selector.select_max_information_item(pool, theta=snap.theta, served_ids=set(snap.served_item_ids))
        if selected.item is None:
            snap.session_state = "completing"
            await self.recovery.write_session_snapshot(str(session_id), snap)
            return None
        snap.session_state = "awaiting_response"
        item_id = str(getattr(selected.item, "item_id", getattr(selected.item, "id", "")))
        if item_id not in snap.served_item_ids:
            snap.served_item_ids.append(item_id)
        await self.recovery.write_session_snapshot(str(session_id), snap)
        return selected.item

    async def submit_response(self, session_id: str | UUID, item: object, *, correct: bool, response: str | None = None, pool_size: int = 10) -> DiagnosticResponseResult:
        snap = await self.recovery.read_session_snapshot(str(session_id))
        if snap is None:
            raise ValueError("diagnostic session snapshot not found")
        item_id = str(getattr(item, "item_id", getattr(item, "id", "")))
        snap.responses.append({"item_id": item_id, "correct": correct, "response": response})
        snap.items_served = len(snap.responses)
        responses = [(item, bool(row["correct"])) for row in snap.responses]
        snap.theta, snap.se_estimate = eap_update_3pl(responses, prior_mean=snap.theta)
        if not correct:
            caps_ref = getattr(item, "caps_ref", snap.caps_ref)
            if caps_ref not in snap.gap_topics:
                snap.gap_topics.append(caps_ref)
            for tag in getattr(item, "misconception_tags", []) or []:
                if tag not in snap.misconception_tags:
                    snap.misconception_tags.append(tag)
        decision = self.terminator.evaluate(standard_error=snap.se_estimate, items_served=snap.items_served, pool_size=pool_size)
        snap.session_state = "completing" if decision.should_stop else "item_serving"
        await self.recovery.write_session_snapshot(str(session_id), snap)
        return DiagnosticResponseResult(str(session_id), snap.theta, snap.se_estimate, snap.items_served, decision.should_stop, decision.reason, snap.gap_topics, snap.misconception_tags)

    async def complete_session(self, session_id: str | UUID) -> dict:
        snap = await self.recovery.read_session_snapshot(str(session_id))
        if snap is None:
            raise ValueError("diagnostic session snapshot not found")
        score = compute_mastery_score(snap.theta, snap.se_estimate)
        label = label_for_score(score).value
        if self.sessions:
            await self.sessions.update_session_state(str(session_id), "completed", theta_after=snap.theta, se_estimate=snap.se_estimate, items_served=snap.items_served, gap_topics=snap.gap_topics, misconception_tags=snap.misconception_tags, completed_at=datetime.now(UTC))
        if self.mastery:
            caps_refs = snap.gap_topics or [snap.caps_ref]
            for caps_ref in caps_refs:
                await self.mastery.upsert_topic_mastery(snap.learner_id, caps_ref, mastery_score=score, mastery_label=label, theta=snap.theta, theta_se=snap.se_estimate)
                await self.mastery.create_snapshot(snap.learner_id, caps_ref, mastery_score=score, mastery_label=label, theta_estimate=snap.theta, theta_se=snap.se_estimate, trigger="diagnostic_completed")
        await self.recovery.invalidate_session_snapshot(str(session_id))
        return {"session_id": str(session_id), "theta": snap.theta, "se_estimate": snap.se_estimate, "mastery_score": score, "mastery_label": label, "gap_topics": snap.gap_topics, "misconception_tags": snap.misconception_tags}

    async def abandon_session(self, session_id: str | UUID) -> None:
        if self.sessions:
            await self.sessions.update_session_state(str(session_id), "abandoned")
        await self.recovery.invalidate_session_snapshot(str(session_id))
