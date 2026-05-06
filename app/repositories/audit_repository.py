"""Append-only audit repository for EduBoost V2."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import AuditLog


class AuditRepository(BaseRepository[AuditLog]):
    """
    Append-only repository for compliance audit logs.
    Inherits from BaseRepository but restricts mutations to ensure audit integrity.
    """
    model = AuditLog

    async def append(
        self,
        db: AsyncSession,
        event_type: str,
        payload: dict[str, Any],
        actor_id: str | UUID | None = None,
        learner_pseudonym: str | UUID | None = None,
        constitutional_outcome: str | None = None,
    ) -> AuditLog:
        """Create a new append-only audit entry."""
        self._validate_payload_no_pii(payload)
        
        return await self.create(
            db,
            event_type=event_type,
            actor_id=str(actor_id) if actor_id else None,
            learner_pseudonym=str(learner_pseudonym) if learner_pseudonym else None,
            payload=payload,
            constitutional_outcome=constitutional_outcome,
        )

    async def update(self, *args: Any, **kwargs: Any) -> Any:
        """Disabled to maintain append-only integrity."""
        raise NotImplementedError("Audit logs are append-only and cannot be updated.")

    async def delete(self, *args: Any, **kwargs: Any) -> Any:
        """Disabled to maintain append-only integrity."""
        raise NotImplementedError("Audit logs are append-only and cannot be deleted.")

    _PII_FIELD_NAMES = frozenset(
        {
            "email", "email_address", "full_name", "display_name",
            "date_of_birth", "dob", "phone", "phone_number",
            "id_number", "sa_id", "national_id", "address",
            "physical_address", "street_address",
        }
    )

    def _validate_payload_no_pii(self, payload: dict[str, Any]) -> None:
        """Ensure no raw PII is accidentally logged in the clear-text payload."""
        payload_keys = {str(key).lower() for key in payload.keys()}
        pii_found = payload_keys & self._PII_FIELD_NAMES
        if pii_found:
            raise ValueError(f"PII-like fields not allowed in audit payload: {sorted(pii_found)}")
