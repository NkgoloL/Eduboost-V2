"""
app/services/diagnostic_session_service.py
─────────────────────────────────────────────────────────────────────────────
Phase 4: Diagnostic Session Orchestration Service (P4-02, P4-03, P4-09)

Responsibilities:
    P4-02 — Create a new session, binding the learner's caps_ref targets from
             the study plan, then drive adaptive item selection.
    P4-03 — Exposure enforcement: after each item is served the exposure record
             is written to DB; the repository query for candidate items already
             filters out items whose exposure_count ≥ max_exposure.
    P4-09 — Session recovery: if a session is interrupted, the full state is
             restored from Redis on the next request. Sessions that expire from
             Redis (TTL 24 h) are treated as abandoned and marked completed.

Redis key scheme:
    diagnostic:session:{session_id}   → JSON (DiagnosticSessionState.to_redis_dict())
    TTL: 86 400 s (24 h)

Usage (from router):
    svc = DiagnosticSessionService(session, redis, item_bank_svc, irt_engine)
    state = await svc.create_session(learner_id, caps_ref)
    item  = await svc.next_item(state.session_id)
    state = await svc.record_response(state.session_id, item_id, is_correct)
    result = await svc.finalise_session(state.session_id)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
from typing import Optional
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic_item import DiagnosticItem
from app.modules.diagnostics.irt_engine import (
    DiagnosticSessionState,
    IRTEngine,
)
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.repositories.item_bank_repository import ItemBankRepository

logger = logging.getLogger(__name__)

_SESSION_TTL = 86_400          # 24 hours in seconds
_SESSION_KEY  = "diagnostic:session:{}"


def _redis_key(session_id: UUID) -> str:
    return _SESSION_KEY.format(str(session_id))


class DiagnosticSessionNotFoundError(Exception):
    """Raised when a session cannot be found in Redis or DB."""


class DiagnosticSessionService:
    """
    Orchestrates the full lifecycle of a single diagnostic session.

    Dependencies are injected so the service is easily unit-testable.
    """

    def __init__(
        self,
        db: AsyncSession,
        redis: Redis,
        item_bank_service: ItemBankService,
        irt_engine: IRTEngine,
    ) -> None:
        self._db     = db
        self._redis  = redis
        self._svc    = item_bank_service
        self._engine = irt_engine

    # ─── Session creation (P4-02) ─────────────────────────────────────────────

    async def create_session(
        self,
        learner_id: UUID,
        caps_ref: str,
        prior_theta: float = 0.0,
    ) -> DiagnosticSessionState:
        """
        Initialise a new diagnostic session for the given learner and topic.

        The prior_theta is typically sourced from the study plan's last known
        ability estimate for this caps_ref (0.0 = no prior, assume average).

        Steps:
          1. Create a fresh DiagnosticSessionState via IRTEngine.
          2. Persist it to Redis with a 24-hour TTL.
          3. Return the state (caller drives the item loop).
        """
        session_id = uuid4()
        state = self._engine.new_session(
            session_id=session_id,
            learner_id=learner_id,
            caps_ref=caps_ref,
            prior_theta=prior_theta,
        )
        await self._save_state(state)

        logger.info(
            "Created diagnostic session %s for learner %s caps_ref=%s θ₀=%.2f",
            str(session_id)[:8], str(learner_id)[:8], caps_ref, prior_theta,
        )
        return state

    # ─── Item delivery ────────────────────────────────────────────────────────

    async def next_item(self, session_id: UUID) -> Optional[DiagnosticItem]:
        """
        Load session from Redis, select the next item, and return it.

        Returns None when stopping criteria are met (session is marked
        completed and saved before returning).

        The selected item is NOT yet marked as served here — that happens
        in record_response so we only count exposures for items the learner
        actually answered.
        """
        state = await self._load_state(session_id)

        if state.completed:
            logger.info("Session %s already completed — no more items.", str(session_id)[:8])
            return None

        item = await self._engine.next_item(state)

        # next_item sets state.completed = True when stopping — persist that
        await self._save_state(state)
        return item

    # ─── Response recording (P4-02, P4-03) ───────────────────────────────────

    async def record_response(
        self,
        session_id: UUID,
        item_id: UUID,
        is_correct: bool,
    ) -> DiagnosticSessionState:
        """
        Record learner's response to an item.

        Steps (P4-02):
          1. Restore session state from Redis.
          2. Fetch the full DiagnosticItem ORM object (needed for IRT params).
          3. Call IRTEngine.record_response → updates θ, SE, and records DB
             exposure (P4-03).
          4. Save updated state back to Redis.
          5. Return updated state so the router can relay θ and SE to the client.

        Exposure enforcement (P4-03):
          IRTEngine.record_response calls item_bank_service.record_item_served,
          which calls item_bank_repository.record_exposure. That increments
          exposure_count in the DB. The next call to select_item_for_learner
          (via get_unexposed_items) filters items where exposure_count ≥
          max_exposure, enforcing the cap automatically.
        """
        state = await self._load_state(session_id)

        if state.completed:
            logger.warning(
                "record_response called on already-completed session %s — ignoring.",
                str(session_id)[:8],
            )
            return state

        # Fetch ORM item — needed for IRT parameters
        repo = getattr(self._svc, "repo", None) or ItemBankRepository(self._db)
        item = await repo.get_item(item_id)
        if item is None:
            raise ValueError(f"DiagnosticItem {item_id} not found in DB.")

        # Delegate to engine (updates θ + records exposure)
        await self._engine.record_response(
            state=state,
            item=item,
            is_correct=is_correct,
            session_id=session_id,
        )

        await self._save_state(state)

        logger.debug(
            "Session %s response recorded: item=%s correct=%s θ=%.3f SE=%.3f",
            str(session_id)[:8], str(item_id)[:8], is_correct,
            state.theta, state.standard_error,
        )
        return state

    # ─── Session finalisation ─────────────────────────────────────────────────

    async def finalise_session(self, session_id: UUID) -> dict:
        """
        Mark session completed and return the final result dict.

        This is the result consumed by:
          - P4-07: lesson context builder (gap topics + misconception tags)
          - P4-08: study plan updater (θ per caps_ref)
          - Parent report (accuracy, items_attempted)

        The Redis key is NOT deleted — it remains for 24 h so recovery
        (P4-09) can still resolve partial sessions that were finalised early.
        """
        state = await self._load_state(session_id)
        state.completed = True
        await self._save_state(state)
        result = self._engine.session_result(state)

        logger.info(
            "Session %s finalised: θ=%.3f SE=%.3f items=%d below_grade=%s",
            str(session_id)[:8], result["theta"], result["standard_error"],
            result["items_attempted"], result["below_grade_level"],
        )
        return result

    # ─── Session recovery (P4-09) ─────────────────────────────────────────────

    async def recover_session(self, session_id: UUID) -> Optional[DiagnosticSessionState]:
        """
        Attempt to restore an interrupted session from Redis.

        Returns the restored DiagnosticSessionState if found, or None if the
        key has expired (session abandoned) or never existed.

        Callers should check state.completed before resuming the item loop.
        """
        raw = await self._redis.get(_redis_key(session_id))
        if raw is None:
            logger.info(
                "Session %s not found in Redis — may have expired or never existed.",
                str(session_id)[:8],
            )
            return None

        data = json.loads(raw)
        state = DiagnosticSessionState.from_redis_dict(data)

        logger.info(
            "Recovered session %s: θ=%.3f items_answered=%d completed=%s",
            str(session_id)[:8], state.theta, len(state.responses), state.completed,
        )
        return state

    # ─── Internal helpers ─────────────────────────────────────────────────────

    async def _save_state(self, state: DiagnosticSessionState) -> None:
        """Serialise session state to Redis with rolling TTL reset."""
        key     = _redis_key(state.session_id)
        payload = json.dumps(state.to_redis_dict())
        await self._redis.set(key, payload, ex=_SESSION_TTL)

    async def _load_state(self, session_id: UUID) -> DiagnosticSessionState:
        """
        Load session from Redis.

        Raises DiagnosticSessionNotFoundError if the key is missing (expired
        or never created).
        """
        raw = await self._redis.get(_redis_key(session_id))
        if raw is None:
            raise DiagnosticSessionNotFoundError(
                f"Diagnostic session {session_id} not found. "
                "It may have expired (24 h TTL) or was never created."
            )
        return DiagnosticSessionState.from_redis_dict(json.loads(raw))
