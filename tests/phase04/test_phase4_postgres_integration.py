from __future__ import annotations

import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DB_URL = os.getenv("PHASE4_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DB_URL, reason="PHASE4_TEST_DATABASE_URL is required")


@pytest.mark.asyncio
async def test_phase4_schema_and_append_only_trigger():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        columns = (await conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='diagnostic_items' AND column_name LIKE 'irt_%'
        """))).scalars().all()
        assert {"irt_quality_state", "irt_strike_count", "irt_last_run_id", "irt_rewrite_artifact_id"} <= set(columns)
        tables = (await conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public' AND table_name IN ('irt_calibration_runs','irt_calibration_events')
        """))).scalars().all()
        assert set(tables) == {"irt_calibration_runs", "irt_calibration_events"}
    await engine.dispose()


@pytest.mark.asyncio
async def test_calibration_run_idempotency_constraint():
    engine = create_async_engine(DB_URL)
    key = f"p4-test-{uuid4()}"
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO irt_calibration_runs
              (idempotency_key,status,dry_run,model_version,policy_version,summary)
            VALUES (:key,'completed',true,'test','test','{}'::jsonb)
        """), {"key": key})
        with pytest.raises(Exception):
            await conn.execute(text("""
                INSERT INTO irt_calibration_runs
                  (idempotency_key,status,dry_run,model_version,policy_version,summary)
                VALUES (:key,'completed',true,'test','test','{}'::jsonb)
            """), {"key": key})
    await engine.dispose()


async def _insert_item(conn, item_id, *, stem, answer_key="A"):
    await conn.execute(text("""
        INSERT INTO diagnostic_items (
          item_id,caps_ref,grade,subject,term,topic,subtopic,skill,stem,answer_key,
          options,explanation,item_type,language,difficulty_b,discrimination_a,
          guessing_c,difficulty_band,review_status,reviewer_id,exposure_count,
          max_exposure,safety_passed,source,irt_quality_state
        ) VALUES (
          :item_id,'4.M.1',4,'Mathematics',1,'Numbers','Whole numbers','Count',:stem,:answer_key,
          '[{"value":"A"},{"value":"B"}]'::jsonb,'Explanation','mcq','en',0.0,1.0,
          0.25,'on_level','approved',:reviewer_id,0,500,true,'human_authored','uncalibrated'
        )
    """), {"item_id": item_id, "stem": stem, "answer_key": answer_key, "reviewer_id": uuid4()})


@pytest.mark.asyncio
async def test_calibration_events_are_append_only():
    from sqlalchemy.exc import DBAPIError

    engine = create_async_engine(DB_URL)
    item_id, run_id, event_id = uuid4(), uuid4(), uuid4()
    async with engine.begin() as conn:
        await _insert_item(conn, item_id, stem="Append-only proof")
        await conn.execute(text("""
            INSERT INTO irt_calibration_runs
              (run_id,idempotency_key,status,dry_run,model_version,policy_version,summary)
            VALUES (:run_id,:key,'completed',false,'test','test','{}'::jsonb)
        """), {"run_id": run_id, "key": f"append-{run_id}"})
        await conn.execute(text("""
            INSERT INTO irt_calibration_events
              (event_id,run_id,item_id,previous_state,next_state,action,reason,metrics,policy_version,model_version)
            VALUES (:event_id,:run_id,:item_id,'uncalibrated','healthy','retain','proof','{}'::jsonb,'test','test')
        """), {"event_id": event_id, "run_id": run_id, "item_id": item_id})

    async with engine.connect() as conn:
        transaction = await conn.begin()
        with pytest.raises(DBAPIError):
            await conn.execute(text("UPDATE irt_calibration_events SET reason='tampered' WHERE event_id=:id"), {"id": event_id})
        await transaction.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_full_calibration_run_keeps_strong_item_eligible():
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from app.models.diagnostic_item import DiagnosticItem
    from app.services.irt_quality_service import IRTQualityService

    engine = create_async_engine(DB_URL)
    target_id = uuid4()
    peer_ids = [uuid4(), uuid4(), uuid4()]
    async with engine.begin() as conn:
        await _insert_item(conn, target_id, stem="Strong target")
        for index, peer_id in enumerate(peer_ids):
            await _insert_item(conn, peer_id, stem=f"Peer {index}")
        for index in range(100):
            learner_id, session_id = uuid4(), uuid4()
            high = index >= 50
            rows = [(target_id, high), *((peer_id, high) for peer_id in peer_ids)]
            for item_id, correct in rows:
                await conn.execute(text("""
                    INSERT INTO item_exposures
                      (item_id,learner_id,session_id,learner_response,is_correct,response_time_ms,answered_at)
                    VALUES (:item_id,:learner_id,:session_id,:response,:correct,1000,now())
                """), {
                    "item_id": item_id, "learner_id": learner_id, "session_id": session_id,
                    "response": "A" if correct else "B", "correct": correct,
                })

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        result = await IRTQualityService().run(
            session, item_ids=[target_id], idempotency_key=f"full-{uuid4()}", actor_id="phase4-test"
        )
        assert result["status"] == "completed"
    async with Session() as session:
        item = await session.get(DiagnosticItem, target_id)
        assert item.irt_quality_state in {"healthy", "monitor"}
        assert item.is_available_for_selection is True
        assert item.stem == "Strong target"
    await engine.dispose()
