"""Integration test for Curriculum Graph Migration, Shadow Mode, and Rollback (TSR-9)."""
from __future__ import annotations

import os
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, update

from app.models.runtime_kg import RuntimeKGGraphLoad, RuntimeKGNode

TEST_DB_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres")
if "postgresql://" in TEST_DB_URL and "+asyncpg" not in TEST_DB_URL:
    TEST_DB_URL = TEST_DB_URL.replace("postgresql://", "postgresql+asyncpg://")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_curriculum_graph_version_activation_and_rollback():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        v1_version = f"2026.1-caps-{uuid4().hex[:6]}"
        v2_version = f"2026.2-caps-shadow-{uuid4().hex[:6]}"
        dummy_sha = "a" * 64

        # 1. Stage and Activate Baseline Graph Version (v1)
        load_v1 = RuntimeKGGraphLoad(
            id=uuid4(),
            graph_version=v1_version,
            curriculum_code="CAPS",
            grade=4,
            subject_code="MATH",
            source_ref="caps-math-v1.json",
            source_sha256=dummy_sha,
            node_count=10,
            edge_count=15,
            status="active",
            loaded_by="migration-test",
            activated_at=datetime.now(timezone.utc),
        )
        session.add(load_v1)
        await session.commit()

        # 2. Stage Candidate Graph Version in 'staged' / shadow mode (v2)
        load_v2 = RuntimeKGGraphLoad(
            id=uuid4(),
            graph_version=v2_version,
            curriculum_code="CAPS",
            grade=4,
            subject_code="MATH",
            source_ref="caps-math-v2-candidate.json",
            source_sha256=dummy_sha,
            node_count=12,
            edge_count=18,
            status="staged",
            loaded_by="migration-test",
        )
        session.add(load_v2)
        await session.commit()

        # Assert shadow mode isolation: active graph for this test run is still v1
        stmt_v1_active = select(RuntimeKGGraphLoad).where(
            RuntimeKGGraphLoad.graph_version == v1_version,
            RuntimeKGGraphLoad.status == "active",
        )
        res = await session.execute(stmt_v1_active)
        assert res.scalar_one_or_none() is not None

        # 3. Promote v2 to active, superseding v1
        now_utc = datetime.now(timezone.utc)
        load_v1.status = "superseded"
        load_v1.superseded_at = now_utc

        load_v2.status = "active"
        load_v2.activated_at = now_utc
        await session.commit()

        # Verify promotion: v2 is active, v1 is superseded
        stmt_v2_active = select(RuntimeKGGraphLoad).where(
            RuntimeKGGraphLoad.graph_version == v2_version,
            RuntimeKGGraphLoad.status == "active",
        )
        res = await session.execute(stmt_v2_active)
        assert res.scalar_one_or_none() is not None

        # 4. Rollback v2 -> withdraw v2, reactivate v1
        load_v2.status = "withdrawn"
        load_v1.status = "active"
        load_v1.superseded_at = None
        await session.commit()

        # Verify rollback restores v1 cleanly
        res = await session.execute(stmt_v1_active)
        assert res.scalar_one_or_none() is not None

    await engine.dispose()
