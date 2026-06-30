"""Phase 5 learner AI tutor routes."""

import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.config import settings
from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.core.rate_limit import limiter
from app.domain.tutor_schemas import (
    TutorCancelResponse,
    TutorQuestion,
    TutorReply,
    TutorSessionCreate,
    TutorSessionView,
)
from app.models.tutor import TutorMessage
from app.security.dependencies import require_active_consent_for_current_user, require_learner_write_for_current_user
from app.services.learner_tutor import LearnerTutorService, serialize_session
from app.services.lesson_authorization import require_lesson_read_access_for_current_user

router = APIRouter(route_class=EnvelopedRoute, prefix="/tutor", tags=["learner-tutor"])


def get_tutor_service(db: AsyncSession = Depends(get_db)) -> LearnerTutorService:
    return LearnerTutorService(db)


async def _require_session_access(db: AsyncSession, auth: AuthContext, service: LearnerTutorService, session_id: uuid.UUID):
    session = await service.get_session(session_id)
    require_learner_write_for_current_user(auth, str(session.learner_id))
    await require_active_consent_for_current_user(db, auth, str(session.learner_id))
    await require_lesson_read_access_for_current_user(db, auth, str(session.lesson_id))
    return session


@router.post("/sessions", response_model=TutorSessionView, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_TUTOR)
async def create_tutor_session(
    request: Request,
    body: TutorSessionCreate,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LearnerTutorService = Depends(get_tutor_service),
):
    require_learner_write_for_current_user(auth, body.learner_id)
    await require_active_consent_for_current_user(db, auth, body.learner_id)
    await require_lesson_read_access_for_current_user(db, auth, body.lesson_id)
    session = await service.create_session(
        learner_id=body.learner_id,
        lesson_id=body.lesson_id,
        actor_id=str(auth.user_id),
        language=body.language,
    )
    return TutorSessionView.model_validate(serialize_session(session))


@router.get("/sessions/{session_id}", response_model=TutorSessionView)
async def get_tutor_session(
    session_id: uuid.UUID,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LearnerTutorService = Depends(get_tutor_service),
):
    session = await _require_session_access(db, auth, service, session_id)
    messages = list(
        (
            await db.scalars(
                select(TutorMessage)
                .where(TutorMessage.session_id == session_id)
                .order_by(TutorMessage.created_at.desc())
                .limit(100)
            )
        ).all()
    )
    messages.reverse()
    return TutorSessionView.model_validate(serialize_session(session, messages))


@router.post("/sessions/{session_id}/messages", response_model=TutorReply)
@limiter.limit(settings.RATE_LIMIT_TUTOR)
async def ask_tutor(
    request: Request,
    session_id: uuid.UUID,
    body: TutorQuestion,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LearnerTutorService = Depends(get_tutor_service),
):
    await _require_session_access(db, auth, service, session_id)
    result = await service.ask(session_id=session_id, question=body.text, client_message_id=body.client_message_id)
    return TutorReply.model_validate({
        "session_id": session_id,
        "learner_message": {
            "message_id": result["learner"].message_id,
            "role": result["learner"].role,
            "content": result["learner"].content,
            "safety_status": result["learner"].safety_status,
            "quality_score": result["learner"].quality_score,
            "provider": result["learner"].provider,
            "created_at": result["learner"].created_at,
        },
        "assistant_message": {
            "message_id": result["assistant"].message_id,
            "role": result["assistant"].role,
            "content": result["assistant"].content,
            "safety_status": result["assistant"].safety_status,
            "quality_score": result["assistant"].quality_score,
            "provider": result["assistant"].provider,
            "created_at": result["assistant"].created_at,
        },
        "fallback": result["fallback"],
        "escalation_created": result["escalation"],
    })


@router.post("/sessions/{session_id}/messages/stream")
@limiter.limit(settings.RATE_LIMIT_TUTOR)
async def stream_tutor_reply(
    request: Request,
    session_id: uuid.UUID,
    body: TutorQuestion,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LearnerTutorService = Depends(get_tutor_service),
):
    await _require_session_access(db, auth, service, session_id)

    async def events():
        yield "event: status\ndata: {\"status\":\"thinking\"}\n\n"
        if await request.is_disconnected():
            return
        try:
            task = asyncio.create_task(
                service.ask(
                    session_id=session_id,
                    question=body.text,
                    client_message_id=body.client_message_id,
                )
            )
            while not task.done():
                if await request.is_disconnected():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    return
                await asyncio.sleep(0.05)
            result = await task
            text = result["assistant"].content
            for start in range(0, len(text), 36):
                if await request.is_disconnected():
                    return
                chunk = text[start:start + 36]
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0)
            yield f"event: done\ndata: {json.dumps({'fallback': result['fallback'], 'escalation_created': result['escalation'], 'message_id': str(result['assistant'].message_id)})}\n\n"
        except HTTPException as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc.detail), 'retryable': exc.status_code >= 500})}\n\n"
        except Exception:
            # Never expose provider or infrastructure exception details to a child.
            yield 'event: error\ndata: {"message":"The tutor is unavailable right now. Please try again later.","retryable":true}\n\n'

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/sessions/{session_id}/cancel", response_model=TutorCancelResponse)
async def cancel_tutor_session(
    session_id: uuid.UUID,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LearnerTutorService = Depends(get_tutor_service),
):
    await _require_session_access(db, auth, service, session_id)
    await service.cancel_session(session_id)
    return TutorCancelResponse(session_id=session_id, status="cancelled")
