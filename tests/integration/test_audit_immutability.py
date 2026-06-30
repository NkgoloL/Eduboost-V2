import pytest
import uuid
import json
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models import AuditEvent

@pytest.mark.asyncio
@pytest.mark.integration
async def test_audit_events_are_immutable():
    """
    Verify that audit_events cannot be updated or deleted due to DB rules.
    This is a critical POPIA compliance requirement.
    """
    event_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    async with AsyncSessionLocal() as db:
        # 1. Insert an audit event using ORM (to handle defaults)
        event = AuditEvent(
            id=event_id,
            event_type="TEST_IMMUTABILITY",
            actor_id=actor_id,
            payload={"key": "original"},
            event_hash="0" * 64,  # Dummy hash
            hmac_signature="0" * 64  # Dummy signature
        )
        db.add(event)
        await db.commit()

        # 2. Attempt to UPDATE the event using raw SQL (to bypass ORM checks)
        await db.execute(
            text(
                "UPDATE audit_events SET payload = '{\"key\": \"tampered\"}' "
                "WHERE id = :id"
            ),
            {"id": event_id}
        )
        await db.commit()

        # Verify it remains unchanged
        result = await db.execute(
            text("SELECT payload FROM audit_events WHERE id = :id"),
            {"id": event_id}
        )
        payload = result.scalar()

        payload_data = json.loads(payload) if isinstance(payload, str) else payload

        # The rule 'audit_events_no_update' should make this a no-op
        assert payload_data["key"] == "original", f"Audit event was tampered with! Found: {payload_data}"

        # 3. Attempt to DELETE the event
        await db.execute(
            text("DELETE FROM audit_events WHERE id = :id"),
            {"id": event_id}
        )
        await db.commit()

        # Verify it still exists
        result = await db.execute(
            text("SELECT COUNT(*) FROM audit_events WHERE id = :id"),
            {"id": event_id}
        )
        count = result.scalar()
        assert count == 1, "Audit event was deleted!"
