"""
Item Bank Repository — P2-01 / P3 Refactor
==========================================
Persistence layer for diagnostic items and exposure tracking.
All DB I/O is async; callers must run inside an AsyncSession context.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Optional

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.domain.item_schema import ReviewStatus
from app.models.item_exposure import ItemExposure


class ItemBankRepository:
    """
    Class-based repository for diagnostic items.
    Aligns with Phase 3 integration testing and service patterns.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ─── Read operations ─────────────────────────────────────────────────────

    async def get_item(self, item_id: uuid.UUID) -> Optional[DiagnosticItem]:
        """Return a single DiagnosticItem by primary key, or None."""
        result = await self.db.execute(
            select(DiagnosticItem).where(DiagnosticItem.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_by_caps_ref(
        self,
        caps_ref: str,
        *,
        review_status: Optional[ReviewStatus] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> Sequence[DiagnosticItem]:
        """Return items for a CAPS reference code."""
        stmt = (
            select(DiagnosticItem)
            .where(DiagnosticItem.caps_ref == caps_ref)
            .order_by(DiagnosticItem.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        if review_status is not None:
            # Handle both Domain Enum and Model Enum for robustness
            status_val = review_status.value if hasattr(review_status, "value") else review_status
            stmt = stmt.where(DiagnosticItem.review_status == status_val)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_unexposed_items(
        self,
        learner_id: uuid.UUID,
        caps_ref: str,
        *,
        max_b_param: Optional[float] = None,
        min_b_param: Optional[float] = None,
        review_status: Optional[str | ReviewStatus | ReviewStatusEnum] = None,
        limit: int = 20,
    ) -> Sequence[DiagnosticItem]:
        """
        Return approved items for *caps_ref* that this learner has not yet seen.
        Renamed from list_unexposed to match Phase 3 test expectations.
        """
        seen_subq = (
            select(ItemExposure.item_id)
            .where(ItemExposure.learner_id == learner_id)
            .scalar_subquery()
        )

        status = review_status or ReviewStatusEnum.APPROVED
        status_val = status.value if hasattr(status, "value") else status

        stmt = (
            select(DiagnosticItem)
            .where(
                DiagnosticItem.caps_ref == caps_ref,
                DiagnosticItem.review_status == status_val,
                DiagnosticItem.safety_passed.is_(True),
                DiagnosticItem.exposure_count < DiagnosticItem.max_exposure,
                DiagnosticItem.item_id.not_in(seen_subq),
            )
            .order_by(DiagnosticItem.difficulty_b.asc())
            .limit(limit)
        )

        if min_b_param is not None:
            stmt = stmt.where(DiagnosticItem.difficulty_b >= min_b_param)
        if max_b_param is not None:
            stmt = stmt.where(DiagnosticItem.difficulty_b <= max_b_param)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_exposure_heatmap(self, caps_ref: str) -> list[dict]:
        """Return exposure utilisation per item for a CAPS reference."""
        stmt = (
            select(
                DiagnosticItem.item_id,
                DiagnosticItem.caps_ref,
                DiagnosticItem.review_status,
                DiagnosticItem.exposure_count,
                DiagnosticItem.max_exposure,
            )
            .where(DiagnosticItem.caps_ref == caps_ref)
            .order_by(desc(DiagnosticItem.exposure_count), DiagnosticItem.item_id.asc())
        )
        result = await self.db.execute(stmt)

        heatmap: list[dict] = []
        for item_id, ref, status, exposure_count, max_exposure in result.all():
            max_count = int(max_exposure or 0)
            current = int(exposure_count or 0)
            heatmap.append(
                {
                    "item_id": str(item_id),
                    "caps_ref": ref,
                    "review_status": status.value if hasattr(status, "value") else str(status),
                    "exposure_count": current,
                    "max_exposure": max_count,
                    "utilisation": round(current / max_count, 4) if max_count else 0.0,
                }
            )
        return heatmap

    async def get_coverage_summary(
        self,
        caps_refs: Optional[list[str]] = None,
    ) -> dict[str, dict]:
        """
        Return per-caps_ref item counts. 
        Returns a dict keyed by caps_ref for easier service-layer processing.
        """
        stmt = select(
            DiagnosticItem.caps_ref,
            DiagnosticItem.review_status,
            func.count(DiagnosticItem.item_id).label("cnt"),
        ).group_by(DiagnosticItem.caps_ref, DiagnosticItem.review_status)

        if caps_refs:
            stmt = stmt.where(DiagnosticItem.caps_ref.in_(caps_refs))

        result = await self.db.execute(stmt)
        rows = result.all()

        summary: dict[str, dict] = {}
        for caps_ref, status, cnt in rows:
            if caps_ref not in summary:
                summary[caps_ref] = {
                    "caps_ref": caps_ref,
                    "total": 0,
                    "approved": 0,
                    "draft": 0,
                    "ai_generated": 0,
                    "human_reviewed": 0,
                    "retired": 0,
                }
            
            # Map status enum value to dict key
            status_key = status.value if hasattr(status, "value") else str(status)
            summary[caps_ref]["total"] += cnt
            if status_key in summary[caps_ref]:
                summary[caps_ref][status_key] += cnt

        return summary

    # ─── Write operations ────────────────────────────────────────────────────

    async def record_exposure(
        self,
        item_id: uuid.UUID,
        learner_id: uuid.UUID,
        *,
        session_id: Optional[uuid.UUID] = None,
    ) -> ItemExposure:
        """Persist an exposure event and atomically increment the item's counter."""
        exposure = ItemExposure(
            item_id=item_id,
            learner_id=learner_id,
            session_id=session_id,
            served_at=datetime.now(tz=timezone.utc),
        )
        self.db.add(exposure)

        await self.db.execute(
            update(DiagnosticItem)
            .where(DiagnosticItem.item_id == item_id)
            .values(exposure_count=DiagnosticItem.exposure_count + 1)
        )

        await self.db.flush()
        return exposure

    async def update_review_status(
        self,
        item_id: uuid.UUID,
        new_status: str,
        *,
        reviewer_id: Optional[uuid.UUID] = None,
        quality_score: Optional[float] = None,
        reviewed_at: Optional[datetime] = None,
    ) -> Optional[DiagnosticItem]:
        """Transition an item's review workflow status."""
        item = await self.get_item(item_id)
        if item is None:
            return None

        # Convert string status to enum if needed
        if isinstance(new_status, str):
            item.review_status = ReviewStatusEnum(new_status)
        else:
            item.review_status = new_status

        if reviewer_id is not None:
            item.reviewer_id = reviewer_id
            item.reviewed_at = reviewed_at or datetime.now(tz=timezone.utc)
        if quality_score is not None:
            item.quality_score = quality_score

        await self.db.flush()
        return item

    # ------------------------------------------------------------------
    # Enum normalization maps — convert any casing variant a caller might
    # pass to the exact string stored in the PostgreSQL enum type.
    # ------------------------------------------------------------------
    _SUBJECT_MAP: dict[str, str] = {
        # uppercase key → DB value
        "MATHEMATICS": "Mathematics",
        "ENGLISH": "English",
        "ISIZULU": "isiZulu",
        "AFRIKAANS": "Afrikaans",
        "LIFE_SKILLS": "Life Skills",
        "NATURAL_SCIENCES": "Natural Sciences",
        # already-correct pass-throughs
        "Mathematics": "Mathematics",
        "English": "English",
        "isiZulu": "isiZulu",
        "Afrikaans": "Afrikaans",
        "Life Skills": "Life Skills",
        "Natural Sciences": "Natural Sciences",
    }
    _ITEM_TYPE_MAP: dict[str, str] = {
        "MCQ": "mcq", "SHORT_ANSWER": "short_answer",
        "TRUE_FALSE": "true_false", "FILL_BLANK": "fill_blank",
        "mcq": "mcq", "short_answer": "short_answer",
        "true_false": "true_false", "fill_blank": "fill_blank",
    }
    _REVIEW_STATUS_MAP: dict[str, str] = {
        "DRAFT": "draft", "AI_GENERATED": "ai_generated",
        "HUMAN_REVIEWED": "human_reviewed", "APPROVED": "approved",
        "RETIRED": "retired",
        "draft": "draft", "ai_generated": "ai_generated",
        "human_reviewed": "human_reviewed", "approved": "approved",
        "retired": "retired",
    }
    _SOURCE_MAP: dict[str, str] = {
        "LLM_GENERATED": "llm_generated", "HUMAN_AUTHORED": "human_authored",
        "IMPORTED": "imported",
        "llm_generated": "llm_generated", "human_authored": "human_authored",
        "imported": "imported",
    }
    _LANGUAGE_MAP: dict[str, str] = {
        "EN": "en", "ZU": "zu", "AF": "af", "XH": "xh",
        "en": "en", "zu": "zu", "af": "af", "xh": "xh",
    }

    def _normalise(self, data: dict) -> dict:
        """Return a shallow copy of *data* with enum fields normalised to DB values."""
        d = dict(data)
        if "subject" in d and isinstance(d["subject"], str):
            d["subject"] = self._SUBJECT_MAP.get(d["subject"], d["subject"])
        if "item_type" in d and isinstance(d["item_type"], str):
            d["item_type"] = self._ITEM_TYPE_MAP.get(d["item_type"], d["item_type"].lower())
        if "review_status" in d and isinstance(d["review_status"], str):
            d["review_status"] = self._REVIEW_STATUS_MAP.get(d["review_status"], d["review_status"].lower())
        if "source" in d and isinstance(d["source"], str):
            d["source"] = self._SOURCE_MAP.get(d["source"], d["source"].lower())
        if "language" in d and isinstance(d["language"], str):
            d["language"] = self._LANGUAGE_MAP.get(d["language"], d["language"].lower())
        for key in ("reviewed_at", "created_at", "updated_at"):
            if isinstance(d.get(key), str):
                value = d[key].replace("Z", "+00:00")
                d[key] = datetime.fromisoformat(value)
        return d

    async def upsert(self, data: dict) -> DiagnosticItem:
        data = self._normalise(data)
        item_id = uuid.UUID(data["item_id"]) if isinstance(data["item_id"], str) else data["item_id"]

        existing = await self.get_item(item_id)
        if existing:
            # Update fields
            for key, value in data.items():
                if key in ("item_id", "created_at"):
                    continue
                if hasattr(existing, key):
                    # Handle Enum conversion
                    if key == "review_status" and isinstance(value, str):
                        value = ReviewStatusEnum(value)
                    setattr(existing, key, value)
            await self.db.flush()
            return existing

        # Create new
        new_item = DiagnosticItem(**data)
        # Ensure UUIDs are objects
        if isinstance(new_item.item_id, str):
            new_item.item_id = uuid.UUID(new_item.item_id)
        if data.get("reviewer_id") and isinstance(data["reviewer_id"], str):
            new_item.reviewer_id = uuid.UUID(data["reviewer_id"])

        self.db.add(new_item)
        await self.db.flush()
        return new_item
