import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.api_v2_routers import tutor, parents, generation
from app.domain.tutor_schemas import TutorSessionCreate, TutorQuestion
from app.models.content_factory import ContentLayer


@pytest.fixture
def mock_admin_context() -> AuthContext:
    uid = str(uuid4())
    return AuthContext(
        user_id=uid,
        roles=[UserRole.PARENT, UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": uid, "user_id": uid, "roles": ["Parent", "Admin"]},
        jti="jti_admin_402",
    )


# ── TUTOR ROUTER ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tutor_router(monkeypatch, mock_admin_context):
    db = AsyncMock()
    mock_svc = MagicMock()

    sess_id = uuid4()
    lid = uuid4()
    less_id = "less_01"

    mock_session = MagicMock()
    mock_session.session_id = sess_id
    mock_session.learner_id = str(lid)
    mock_session.lesson_id = less_id
    mock_session.actor_id = mock_admin_context.user_id
    mock_session.language = "en"
    mock_session.status = "active"
    mock_session.message_count = 0
    mock_session.escalation_count = 0
    mock_session.created_at = datetime.now(timezone.utc)
    mock_session.last_activity_at = datetime.now(timezone.utc)

    mock_svc.get_session = AsyncMock(return_value=mock_session)
    mock_svc.create_session = AsyncMock(return_value=mock_session)
    mock_svc.cancel_session = AsyncMock()

    monkeypatch.setattr(tutor, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(tutor, "require_active_consent_for_current_user", AsyncMock())
    monkeypatch.setattr(tutor, "require_lesson_read_access_for_current_user", AsyncMock())

    # 1. get_tutor_service
    assert tutor.get_tutor_service(db) is not None

    # 2. _require_session_access
    sess = await tutor._require_session_access(db, mock_admin_context, mock_svc, sess_id)
    assert sess == mock_session

    # 3. create_tutor_session
    mock_req = MagicMock(spec=Request)
    create_body = TutorSessionCreate(learner_id=str(lid), lesson_id=less_id, language="en")
    view1 = await tutor.create_tutor_session(mock_req, create_body, mock_admin_context, db, mock_svc)
    assert view1.session_id == sess_id

    # 4. get_tutor_session
    mock_msg = MagicMock()
    mock_msg.message_id = uuid4()
    mock_msg.role = "learner"
    mock_msg.content = "Help please"
    mock_msg.safety_status = "safe"
    mock_msg.quality_score = 0.95
    mock_msg.provider = "openai"
    mock_msg.created_at = datetime.now(timezone.utc)

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_msg]
    db.scalars = AsyncMock(return_value=mock_scalars)

    view2 = await tutor.get_tutor_session(sess_id, mock_admin_context, db, mock_svc)
    assert view2.session_id == sess_id

    # 5. ask_tutor
    mock_learner_msg = MagicMock(
        message_id=uuid4(),
        role="learner",
        content="2+2?",
        safety_status="safe",
        quality_score=0.9,
        provider="user",
        created_at=datetime.now(timezone.utc),
    )
    mock_assistant_msg = MagicMock(
        message_id=uuid4(),
        role="assistant",
        content="It is 4.",
        safety_status="safe",
        quality_score=0.95,
        provider="openai",
        created_at=datetime.now(timezone.utc),
    )
    mock_svc.ask = AsyncMock(
        return_value={
            "learner": mock_learner_msg,
            "assistant": mock_assistant_msg,
            "fallback": False,
            "escalation": False,
        }
    )
    q_body = TutorQuestion(text="2+2?", client_message_id=str(uuid4()))
    reply = await tutor.ask_tutor(mock_req, sess_id, q_body, mock_admin_context, db, mock_svc)
    assert reply.session_id == sess_id
    assert reply.assistant_message.content == "It is 4."

    # 6. stream_tutor_reply: disconnected case
    mock_req_disc = MagicMock(spec=Request)
    mock_req_disc.is_disconnected = AsyncMock(return_value=True)
    stream_disc = await tutor.stream_tutor_reply(mock_req_disc, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks_disc = [chunk async for chunk in stream_disc.body_iterator]
    assert len(chunks_disc) == 1
    assert "thinking" in chunks_disc[0]

    # 7. stream_tutor_reply: connected success
    mock_req_conn = MagicMock(spec=Request)
    mock_req_conn.is_disconnected = AsyncMock(return_value=False)
    stream_res = await tutor.stream_tutor_reply(mock_req_conn, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks = [chunk async for chunk in stream_res.body_iterator]
    assert any("thinking" in c for c in chunks)
    assert any("token" in c for c in chunks)

    # 7b. stream_tutor_reply: disconnected while task is running
    async def slow_ask(*args, **kwargs):
        await asyncio.sleep(0.1)
        return {
            "learner": mock_learner_msg,
            "assistant": mock_assistant_msg,
            "fallback": False,
            "escalation": False,
        }
    mock_svc.ask = AsyncMock(side_effect=slow_ask)
    mock_req_cancel = MagicMock(spec=Request)
    mock_req_cancel.is_disconnected = AsyncMock(side_effect=[False, True])
    stream_cancel = await tutor.stream_tutor_reply(mock_req_cancel, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks_cancel = [chunk async for chunk in stream_cancel.body_iterator]
    assert len(chunks_cancel) == 1

    # 7c. stream_tutor_reply: disconnected during tokens
    mock_svc.ask = AsyncMock(
        return_value={
            "learner": mock_learner_msg,
            "assistant": mock_assistant_msg,
            "fallback": False,
            "escalation": False,
        }
    )
    mock_req_tok = MagicMock(spec=Request)
    mock_req_tok.is_disconnected = AsyncMock(side_effect=[False, False, True])
    stream_tok = await tutor.stream_tutor_reply(mock_req_tok, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks_tok = [chunk async for chunk in stream_tok.body_iterator]
    assert any("thinking" in c for c in chunks_tok)

    # 8. stream_tutor_reply error cases
    mock_svc.ask = AsyncMock(side_effect=HTTPException(status_code=502, detail="Gateway error"))
    stream_err = await tutor.stream_tutor_reply(mock_req_conn, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks_err = [chunk async for chunk in stream_err.body_iterator]
    assert any("Gateway error" in c for c in chunks_err)

    mock_svc.ask = AsyncMock(side_effect=Exception("Unknown crash"))
    stream_crash = await tutor.stream_tutor_reply(mock_req_conn, sess_id, q_body, mock_admin_context, db, mock_svc)
    chunks_crash = [chunk async for chunk in stream_crash.body_iterator]
    assert any("tutor is unavailable" in c for c in chunks_crash)

    # 9. cancel_tutor_session
    cancel_res = await tutor.cancel_tutor_session(sess_id, mock_admin_context, db, mock_svc)
    assert cancel_res.status == "cancelled"


# ── PARENTS ROUTER ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_parents_router(monkeypatch, mock_admin_context):
    db = AsyncMock()
    mock_req = MagicMock(spec=Request)
    mock_req.state = MagicMock()

    # 1. get_parent_dashboard: guardian not found -> 404
    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_gd:
        await parents.get_parent_dashboard(mock_req, db, mock_admin_context)
    assert exc_gd.value.status_code == 404

    # 2. get_parent_dashboard: success
    guardian_id = uuid4()
    mock_admin_context.user_id = str(guardian_id)
    mock_guardian = MagicMock(id=guardian_id, subscription_tier="pro")
    db.get = AsyncMock(return_value=mock_guardian)

    lid = uuid4()
    mock_learner = MagicMock(
        id=str(lid),
        display_name="Lebo",
        grade=4,
        archetype="Visual",
        theta=0.5,
        streak_days=5,
        pseudonym_id="pseudo_l1",
    )
    # Also a learner that triggers HTTPException to cover the continue branch
    mock_learner_denied = MagicMock(id=str(uuid4()))

    mock_learner_svc = MagicMock()
    mock_learner_svc.list_by_guardian = AsyncMock(return_value=[mock_learner, mock_learner_denied])
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    monkeypatch.setattr(parents, "LearnerService", lambda d: mock_learner_svc)

    def check_learner_read(user, l):
        if l == mock_learner_denied:
            raise HTTPException(status_code=403, detail="denied")

    monkeypatch.setattr(parents, "require_learner_read_for_current_user", check_learner_read)
    monkeypatch.setattr(parents, "require_active_consent_for_current_user", AsyncMock())

    db.scalar = AsyncMock(return_value=3)
    dash = await parents.get_parent_dashboard(mock_req, db, mock_admin_context)
    assert dash.guardian_id == mock_guardian.id
    assert len(dash.learners) == 1

    # 2b. get_parent_dashboard: empty learners branch
    mock_learner_svc.list_by_guardian = AsyncMock(return_value=[])
    dash_empty = await parents.get_parent_dashboard(mock_req, db, mock_admin_context)
    assert len(dash_empty.learners) == 0

    # 3. get_parent_trust_dashboard: forbidden when not self and not admin
    non_admin_ctx = AuthContext(
        user_id="other_user",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "other_user"},
        jti="jti_non_admin",
    )
    with pytest.raises(HTTPException) as exc_forb:
        await parents.get_parent_trust_dashboard("target_guardian", mock_req, db, non_admin_ctx)
    assert exc_forb.value.status_code == 403

    # Guardian not found in trust dashboard
    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_t_404:
        await parents.get_parent_trust_dashboard(mock_admin_context.user_id, mock_req, db, mock_admin_context)
    assert exc_t_404.value.status_code == 404

    # Success in trust dashboard
    db.get = AsyncMock(return_value=mock_guardian)
    mock_learner_svc.list_by_guardian = AsyncMock(return_value=[mock_learner])
    mock_exec = MagicMock()
    mock_exec.generate_progress_summary = AsyncMock(return_value="Great progress in maths.")
    monkeypatch.setattr(parents, "_executive", mock_exec)

    mock_gaps = MagicMock()
    mock_gap_row = MagicMock(topic="Fractions")
    mock_gaps.scalars.return_value.all.return_value = [mock_gap_row]
    db.execute = AsyncMock(return_value=mock_gaps)

    trust_dash = await parents.get_parent_trust_dashboard(mock_admin_context.user_id, mock_req, db, mock_admin_context)
    assert trust_dash.guardian_id == mock_admin_context.user_id
    assert len(trust_dash.learners) == 1

    # 4. export_parent_access_bundle: forbidden, not found, success
    with pytest.raises(HTTPException) as exc_exp_forb:
        await parents.export_parent_access_bundle("target_guardian", db, non_admin_ctx)
    assert exc_exp_forb.value.status_code == 403

    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_exp_404:
        await parents.export_parent_access_bundle(mock_admin_context.user_id, db, mock_admin_context)
    assert exc_exp_404.value.status_code == 404

    db.get = AsyncMock(return_value=mock_guardian)
    mock_learner_svc.list_by_guardian = AsyncMock(return_value=[mock_learner])
    bundle = await parents.export_parent_access_bundle(mock_admin_context.user_id, db, mock_admin_context)
    assert bundle["guardian_id"] == mock_admin_context.user_id
    assert len(bundle["exports"]) == 1

    # 5. get_learner_progress: not found, success
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_p_404:
        await parents.get_learner_progress(str(lid), db, mock_admin_context)
    assert exc_p_404.value.status_code == 404

    mock_learner_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    mock_lessons_rows = [(datetime.now(timezone.utc), "Mathematics")]
    mock_gaps_rows = [("Mathematics", False), ("Mathematics", True)]

    mock_db_res1 = MagicMock()
    mock_db_res1.all.return_value = mock_lessons_rows
    mock_db_res2 = MagicMock()
    mock_db_res2.all.return_value = mock_gaps_rows
    db.execute = AsyncMock(side_effect=[mock_db_res1, mock_db_res2])

    prog = await parents.get_learner_progress(str(lid), db, mock_admin_context)
    assert prog["learner_id"] == str(lid)
    assert len(prog["knowledge_gap_breakdown"]) == 1

    # 6. request_erasure & _log_purge_request
    mock_popia = MagicMock()
    mock_popia.request_erasure = AsyncMock(return_value={"status": "submitted"})
    monkeypatch.setattr(parents, "POPIADataRightsService", lambda d: mock_popia)
    erase_res = await parents.request_erasure(str(lid), db, mock_admin_context)
    assert erase_res["status"] == "submitted"

    await parents._log_purge_request(str(lid), "pseudo_l1")


# ── GENERATION ROUTER ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generation_router(monkeypatch, mock_admin_context):
    db = AsyncMock()

    # 1. helpers
    assert generation._get_engine() is not None

    mock_run = MagicMock()
    mock_run.run_id = uuid4()
    mock_run.scope_id = "scope_g4"
    mock_run.status = "queued"
    mock_run.requested_by = mock_admin_context.user_id
    mock_run.provider = "openai"
    mock_run.run_metadata = {"durable_job_id": "job_123"}
    mock_run.created_at = datetime.now(timezone.utc)
    mock_run.updated_at = datetime.now(timezone.utc)

    resp = generation._run_response(mock_run, "job_123")
    assert resp.run_id == str(mock_run.run_id)

    # 2. start_generation_run: budget exceeded
    mock_guard = MagicMock()
    mock_guard.check_and_reserve_async = AsyncMock(
        side_effect=HTTPException(status_code=429, detail="AI budget limit exceeded")
    )
    monkeypatch.setattr(generation, "get_ai_budget_guard", lambda: mock_guard)

    task_spec1 = generation.TaskSpecRequest(
        caps_ref="4.M.1.1",
        content_type="diagnostic_item",
        count=2,
    )
    # duplicate caps_ref to hit `if spec.caps_ref in sources_by_caps_ref: continue`
    task_spec2 = generation.TaskSpecRequest(
        caps_ref="4.M.1.1",
        content_type="lesson",
        count=1,
    )
    start_body = generation.StartRunRequest(
        scope_id="scope_g4",
        task_specs=[task_spec1, task_spec2],
    )
    with pytest.raises(HTTPException) as exc_b:
        await generation.start_generation_run(start_body, mock_admin_context, db, MagicMock())
    assert exc_b.value.status_code == 429

    # 3. start_generation_run: sources provenance failed (HTTP 422)
    mock_guard.check_and_reserve_async = AsyncMock(return_value=1000)
    mock_context_fail = MagicMock(passed=False, errors=["chunk missing"], chunks=[])
    mock_ctx_svc = MagicMock()
    mock_ctx_svc.build_context = AsyncMock(return_value=mock_context_fail)
    monkeypatch.setattr(generation, "ContentGenerationSourceContextService", lambda: mock_ctx_svc)

    with pytest.raises(HTTPException) as exc_src:
        await generation.start_generation_run(start_body, mock_admin_context, db, MagicMock())
    assert exc_src.value.status_code == 422

    # 4. start_generation_run: success
    mock_chunk = MagicMock(chunk_id="chunk_1", text="Sample chunk text")
    mock_context_ok = MagicMock(passed=True, errors=[], chunks=[mock_chunk])
    mock_ctx_svc.build_context = AsyncMock(return_value=mock_context_ok)
    monkeypatch.setattr(
        generation,
        "source_rows_for_chunks",
        lambda chunks, **kw: [{"chunk_id": "chunk_1", "text": "Sample chunk text"}],
    )

    mock_engine = MagicMock()
    mock_engine.create_run = AsyncMock(return_value=mock_run)

    # Mock db.execute for conditional update
    mock_update_res = MagicMock()
    mock_update_res.scalar_one_or_none.return_value = "queued"
    db.execute = AsyncMock(return_value=mock_update_res)

    monkeypatch.setattr(generation, "enqueue_durable", AsyncMock(return_value="job_gen_durable"))

    res_run = await generation.start_generation_run(start_body, mock_admin_context, db, mock_engine)
    assert res_run.status == "queued"
    assert res_run.durable_job_id == "job_gen_durable"

    # 5. start_generation_run: already processed (HTTP 409)
    mock_update_res.scalar_one_or_none.return_value = None
    db.refresh = AsyncMock()
    with pytest.raises(HTTPException) as exc_conflict:
        await generation.start_generation_run(start_body, mock_admin_context, db, mock_engine)
    assert exc_conflict.value.status_code == 409

    # 6. start_generation_run: enqueue failure (HTTP 503)
    mock_update_res.scalar_one_or_none.return_value = "queued"
    monkeypatch.setattr(generation, "enqueue_durable", AsyncMock(side_effect=RuntimeError("Redis down")))
    with pytest.raises(HTTPException) as exc_503:
        await generation.start_generation_run(start_body, mock_admin_context, db, mock_engine)
    assert exc_503.value.status_code == 503

    # 7. get_generation_run: not found & found
    mock_row_res = MagicMock()
    mock_row_res.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_row_res)
    with pytest.raises(HTTPException) as exc_gr:
        await generation.get_generation_run(uuid4(), mock_admin_context, db)
    assert exc_gr.value.status_code == 404

    mock_row_res.scalar_one_or_none.return_value = mock_run
    db.execute = AsyncMock(return_value=mock_row_res)
    res_get = await generation.get_generation_run(mock_run.run_id, mock_admin_context, db)
    assert res_get.run_id == str(mock_run.run_id)

    # 8. list_run_tasks (with and without status_filter)
    mock_task = MagicMock()
    mock_task.task_id = uuid4()
    mock_task.caps_ref = "4.M.1.1"
    mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
    mock_task.status = "completed"
    mock_task.attempt_number = 1
    mock_task.provider = "openai"
    mock_task.model = "gpt-4"
    mock_task.prompt_version = "v1"
    mock_task.token_usage = {}
    mock_task.cost_metadata = {}
    mock_task.validation_failures = []
    mock_task.output_artifact_ids = []
    mock_task.started_at = datetime.now(timezone.utc)
    mock_task.finished_at = datetime.now(timezone.utc)
    mock_task.created_at = datetime.now(timezone.utc)

    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [mock_task]
    db.execute = AsyncMock(return_value=mock_tasks_res)

    tasks_list = await generation.list_run_tasks(mock_run.run_id, status_filter="completed", _auth=mock_admin_context, db=db)
    assert len(tasks_list) == 1
    assert tasks_list[0].caps_ref == "4.M.1.1"

    tasks_list_no_filter = await generation.list_run_tasks(mock_run.run_id, status_filter=None, _auth=mock_admin_context, db=db)
    assert len(tasks_list_no_filter) == 1

    # 9. cancel_generation_run: not found & found
    mock_cancel_row = MagicMock()
    mock_cancel_row.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_cancel_row)
    with pytest.raises(HTTPException) as exc_can:
        await generation.cancel_generation_run(uuid4(), mock_admin_context, db)
    assert exc_can.value.status_code == 404

    mock_cancel_row.scalar_one_or_none.return_value = mock_run
    mock_update_tasks = MagicMock()
    mock_update_tasks.scalars.return_value.all.return_value = [uuid4()]
    db.execute = AsyncMock(side_effect=[mock_cancel_row, mock_update_tasks, MagicMock()])

    cancel_res = await generation.cancel_generation_run(mock_run.run_id, mock_admin_context, db)
    assert getattr(cancel_res, "data")["status"] == "cancelled"
