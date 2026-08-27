"""Integration test verifying database-level immutability triggers and rules for audit tables.

This test asserts that:
1. INSERT into `audit_events` succeeds.
2. UPDATE against `audit_events` fails closed (PostgreSQL trigger/rule blocks modification).
3. DELETE against `audit_events` fails closed (PostgreSQL trigger/rule blocks modification).
4. Direct raw SQL DML statements cannot alter historical audit records.
"""
from __future__ import annotations

import os
import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_TEST_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"
)
if DEFAULT_TEST_DB_URL.startswith("postgresql://"):
    DEFAULT_TEST_DB_URL = DEFAULT_TEST_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


@pytest.mark.asyncio
async def test_audit_events_immutability_fail_closed():
    """Verify that audit_events rejects UPDATE and DELETE operations."""
    engine = create_async_engine(DEFAULT_TEST_DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Insert a test audit record
        event_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        test_hash = "0" * 64
        test_sig = "a" * 64

        insert_stmt = text("""
            INSERT INTO audit_events (id, event_type, actor_id, resource_id, payload, event_hash, hmac_signature, created_at)
            VALUES (:id, :event_type, :actor_id, :resource_id, CAST(:payload AS jsonb), :event_hash, :hmac_signature, :created_at)
        """)
        await session.execute(
            insert_stmt,
            {
                "id": event_id,
                "event_type": "security.test.immutability",
                "actor_id": actor_id,
                "resource_id": resource_id,
                "payload": '{"test": true, "reason": "immutability_verification"}',
                "event_hash": test_hash,
                "hmac_signature": test_sig,
                "created_at": datetime.now(timezone.utc),
            }
        )
        await session.commit()

        # 2. Verify record exists
        select_stmt = text("SELECT id, event_type FROM audit_events WHERE id = :id")
        result = await session.execute(select_stmt, {"id": event_id})
        row = result.first()
        assert row is not None, "Audit event must be inserted successfully"
        assert row[1] == "security.test.immutability"

        # 3. Assert UPDATE fails or affects 0 rows (trigger exception or RULE DO INSTEAD NOTHING)
        update_stmt = text("""
            UPDATE audit_events 
            SET event_type = 'tampered.event.type' 
            WHERE id = :id
        """)
        
        # Either the trigger raises an exception OR the PostgreSQL rule converts it to INSTEAD NOTHING
        try:
            update_result = await session.execute(update_stmt, {"id": event_id})
            await session.commit()
            # If no exception, rule suppressed it -> verify data is untampered
            verify_result = await session.execute(select_stmt, {"id": event_id})
            unmodified_row = verify_result.first()
            assert unmodified_row[1] == "security.test.immutability", "Audit record must not be modified by UPDATE"
        except Exception as exc:
            # Trigger raised exception -> verify exception mentions immutability
            await session.rollback()
            assert "append-only" in str(exc).lower() or "forbidden" in str(exc).lower() or "immutable" in str(exc).lower()

        # 4. Assert DELETE fails or affects 0 rows
        delete_stmt = text("DELETE FROM audit_events WHERE id = :id")
        try:
            delete_result = await session.execute(delete_stmt, {"id": event_id})
            await session.commit()
            # If no exception, rule suppressed it -> verify data is STILL present
            verify_result = await session.execute(select_stmt, {"id": event_id})
            persisted_row = verify_result.first()
            assert persisted_row is not None, "Audit record must not be deleted by DELETE"
            assert persisted_row[1] == "security.test.immutability"
        except Exception as exc:
            await session.rollback()
            assert "append-only" in str(exc).lower() or "forbidden" in str(exc).lower() or "immutable" in str(exc).lower()

    await engine.dispose()
