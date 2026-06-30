from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import Base from the project's shared declarative base
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.diagnostic_item import DiagnosticItem

class ItemExposure(Base):
    """
    ORM representation of the item_exposures table.

    Each row records one item being served to one learner in one session.
    The table is append-only by convention — rows are never updated or deleted
    in normal operation.  Erasure is handled by the POPIA erasure workflow
    (anonymise learner_id to NULL, preserve aggregate counts).
    """

    __tablename__ = "item_exposures"
    __table_args__ = (
        CheckConstraint(
            "response_time_ms IS NULL OR response_time_ms >= 0",
            name="ck_item_exposures_response_time_positive",
        ),
        CheckConstraint(
            "answered_at IS NULL OR answered_at >= served_at",
            name="ck_item_exposures_answered_after_served",
        ),
        Index("ix_item_exposures_learner_item", "learner_id", "item_id"),
        Index("ix_item_exposures_learner_served_at", "learner_id", "served_at"),
        Index("ix_item_exposures_session_id", "session_id"),
    )

    # --- Identity --------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # --- Foreign keys ----------------------------------------------------
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_items.item_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # --- Event data ------------------------------------------------------
    served_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    learner_response: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Relationship back to item ---------------------------------------
    item: Mapped["DiagnosticItem"] = relationship(
        "DiagnosticItem",
        back_populates="exposures",
    )

    # --- Helpers ---------------------------------------------------------
    @property
    def was_answered(self) -> bool:
        return self.answered_at is not None

    def __repr__(self) -> str:
        return (
            f"<ItemExposure id={self.id} "
            f"item={self.item_id!s:.8} "
            f"learner={self.learner_id!s:.8} "
            f"correct={self.is_correct}>"
        )
