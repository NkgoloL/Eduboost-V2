"""EduBoost V2 — Diagnostic Router"""
from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.envelope_route import EnvelopedRoute
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import check_ai_quota
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import get_current_user  # noqa: F401
from app.domain.schemas import DiagnosticResult, DiagnosticSubmit
from app.security.dependencies import require_learner_read_for_current_user, require_active_consent_for_current_user
from app.security.dependencies import require_learner_write_for_current_user
from app.api_v2_deps import diagnostic_repositories  # noqa: F401 - backward-compatibility test double anchor
from app.services.diagnostic import DiagnosticEngine
from app.services.caps_validator import CAPSAlignmentValidator
from app.core.metrics import ITEM_BANK_COVERAGE_RATIO
from app.modules.diagnostics import bias_review_router
from app.modules.diagnostics.item_bank_service import ItemBankService  # noqa: F401
from app.modules.diagnostics.diagnostic_session_service import DiagnosticSessionService  # noqa: F401
from app.modules.diagnostics.session_recovery_service import SessionRecoveryService  # noqa: F401
from app.services.diagnostic_domain_service import (
    DiagnosticDomainService,
    get_diagnostic_domain_service,
)
from app.services.diagnostic_data_integrity import DiagnosticIntegrityError, validate_diagnostic_submission_payload
from app.services.diagnostic_route_integrity import validate_adaptive_diagnostic_response
from app.services.runtime_kg.route_integration import build_runtime_kg_diagnostic_projection

router = APIRouter(route_class=EnvelopedRoute, prefix="/diagnostics", tags=["diagnostics"])
router.include_router(bias_review_router.router)
_engine = DiagnosticEngine()
_caps_validator = CAPSAlignmentValidator()

_FRONTEND_SUBJECT_CODES = {
    "mathematics": "MATH",
    "math": "MATH",
    "english": "ENG",
    "eng": "ENG",
    "natural sciences": "NS",
    "natural science": "NS",
    "social sciences": "SS",
    "social science": "SS",
    "life skills": "LIFE",
    "life orientation": "LIFE",
}

def _subject_code(value) -> str:
    raw = getattr(value, "value", value)
    text = str(raw or "").strip()
    return _FRONTEND_SUBJECT_CODES.get(text.lower(), text)

def _option_payload(options) -> list[dict[str, str]]:
    if not options:
        return []
    if isinstance(options, dict):
        return [{"key": str(key), "label": str(value)} for key, value in options.items()]
    payload = []
    for index, option in enumerate(options):
        fallback_key = chr(65 + index)
        if isinstance(option, dict):
            key = str(option.get("key") or option.get("id") or fallback_key)
            label = str(option.get("label") or option.get("text") or option.get("value") or key)
            payload.append({"key": key, "label": label})
        else:
            payload.append({"key": fallback_key, "label": str(option)})
    return payload

def _serialise_item_bank_item(item) -> dict:
    options = _option_payload(item.options)
    return {
        "id": str(item.item_id),
        "item_id": str(item.item_id),
        "question": item.stem,
        "question_text": item.stem,
        "options": options,
        "option_keys": [option["key"] for option in options],
        "subject": _subject_code(item.subject),
        "topic": item.topic,
        "skill": item.skill,
        "difficulty": float(item.difficulty_b),
        "discrimination": float(item.discrimination_a),
        "caps_reference": item.caps_ref,
        "caps_ref": item.caps_ref,
        "review_status": getattr(item.review_status, "value", item.review_status),
    }

def _engine_item_from_item_bank(item):
    return SimpleNamespace(
        id=str(item.item_id),
        grade=int(item.grade),
        subject=_subject_code(item.subject),
        topic=str(item.topic),
        a_param=float(item.discrimination_a or 1.0),
        b_param=float(item.difficulty_b or 0.0),
    )

class ReviewItemRequest(BaseModel):
    review_status: str = Field(..., pattern="^(draft|ai_generated|human_reviewed|approved|retired)$")
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)

def _require_item_bank_admin(current_user: AuthContext) -> None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Item bank administration requires admin role",
        )

@router.get("/items/{learner_id}")
async def get_diagnostic_items(
    learner_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    learner = await service.get_learner(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, str(learner_id))
    request.state.analytics = {
        "event": "diagnostic_started",
        "pseudonym_id": learner.pseudonym_id,
        "properties": {"learner_grade": learner.grade},
    }

    canonical_items = await service.list_approved_items_for_grade(learner.grade, limit=20)
    if canonical_items:
        return [_serialise_item_bank_item(item) for item in canonical_items]

    items = await service.get_irt_items_for_grade(learner.grade, limit=20)
    return [
        {
            "id": i.id,
            "question": i.question_text,
            "options": i.options,
            "subject": i.subject,
            "topic": i.topic,
            "skill": getattr(i, "skill", None) or i.topic,
            "difficulty": i.b_param,
            "discrimination": i.a_param,
            "caps_reference": getattr(i, "caps_reference", None)
            or _caps_validator.validate(i.grade, i.subject, i.topic).caps_reference,
            "review_status": getattr(getattr(i, "review_status", "draft"), "value", getattr(i, "review_status", "draft")),
        }
        for i in items
    ]

@router.post("/submit", response_model=DiagnosticResult)
async def submit_diagnostic(
    body: DiagnosticSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    # code_691_720_diagnostic_submission_integrity
    validate_diagnostic_submission_payload(body, require_items=True)
    learner = await service.get_learner(body.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_write_for_current_user(current_user, body.learner_id)
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    guardian = await service.get_guardian(learner.guardian_id)
    tier = guardian.subscription_tier if guardian else "free"
    await check_ai_quota(learner.guardian_id, tier)

    canonical_items = await service.list_approved_items_for_grade(learner.grade, limit=50)
    canonical_map = {str(item.item_id): item for item in canonical_items}
    answer_ids = {str(answer.item_id) for answer in body.answers}

    if canonical_map and answer_ids.issubset(set(canonical_map)):
        served_items = [canonical_map[str(answer.item_id)] for answer in body.answers]
        items = [_engine_item_from_item_bank(item) for item in served_items]
        correct_ids = {
            str(answer.item_id)
            for answer in body.answers
            if str(answer.selected_option).upper() == str(canonical_map[str(answer.item_id)].answer_key).upper()
        }
    else:
        items = await service.get_irt_items_for_grade(learner.grade)
        item_map = {str(i.id): i for i in items}
        correct_ids = {
            str(answer.item_id)
            for answer in body.answers
            if item_map.get(str(answer.item_id))
            and str(answer.selected_option).upper() == str(item_map[str(answer.item_id)].correct_option).upper()
        }

    responses_dict = {str(a.item_id): str(a.selected_option) for a in body.answers}

    analysis = _engine.run_gap_probe_cascade(
        learner_grade=learner.grade,
        items=items,
        correct_item_ids=correct_ids,
        starting_theta=learner.theta,
    )
    theta_after = analysis["theta"]

    # Persist session
    session = await service.create_session(body.learner_id, learner.theta)
    await service.complete_session(session.id, responses_dict, theta_after)

    # Update learner theta
    await service.update_learner_theta(body.learner_id, theta_after)

    # Identify and persist gaps
    gaps = analysis["ranked_gaps"]
    for g in gaps:
        await service.upsert_knowledge_gap(body.learner_id, g["grade"], g["subject"], g["topic"], g["severity"])

    item_to_stable_code: dict[str, str] = {}
    if canonical_map and answer_ids.issubset(set(canonical_map)):
        item_to_stable_code = {
            str(item_id): str(getattr(item, "caps_ref", None) or getattr(item, "skill", None) or getattr(item, "topic", item_id))
            for item_id, item in canonical_map.items()
        }
    else:
        item_to_stable_code = {
            str(getattr(item, "id", "")): str(getattr(item, "caps_reference", None) or getattr(item, "skill", None) or getattr(item, "topic", getattr(item, "id", "")))
            for item in items
        }
    correct_by_item_id = {str(answer.item_id): str(answer.item_id) in correct_ids for answer in body.answers}
    runtime_kg_projection = await build_runtime_kg_diagnostic_projection(
        db,
        learner_id=str(body.learner_id),
        subject_code=_subject_code(getattr(learner, "subject", None) or (items[0].subject if items else "Mathematics")),
        correct_by_item_id=correct_by_item_id,
        item_to_stable_code=item_to_stable_code,
    )

    gap_labels = [f"{g['subject']}: {g['topic']}" for g in gaps]
    request.state.analytics = {
        "event": "diagnostic_completed",
        "pseudonym_id": learner.pseudonym_id,
        "properties": {"gap_count": len(gaps), "theta_after": theta_after},
    }

    return DiagnosticResult(
        session_id=session.id,
        theta_before=learner.theta,
        theta_after=theta_after,
        gaps_identified=gap_labels,
        standard_error=analysis["standard_error"],
        grade_equivalent=analysis["grade_equivalent"],
        ranked_gaps=gaps,
        runtime_kg_projection=runtime_kg_projection.to_payload(),
    )

@router.get("/coverage")
async def get_item_bank_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    _require_item_bank_admin(current_user)
    summary = await service.get_item_bank_coverage_summary()
    for caps_ref, row in summary.items():
        ITEM_BANK_COVERAGE_RATIO.labels(caps_ref=caps_ref).set(row.get("coverage_ratio", 0.0))
    return summary

@router.get("/item-bank/items/{item_id}")
async def get_item_bank_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    _require_item_bank_admin(current_user)
    item = await service.get_item_bank_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item_id": str(item.item_id),
        "caps_ref": item.caps_ref,
        "grade": item.grade,
        "subject": getattr(item.subject, "value", item.subject),
        "term": item.term,
        "topic": item.topic,
        "subtopic": item.subtopic,
        "skill": item.skill,
        "stem": item.stem,
        "answer_key": item.answer_key,
        "options": item.options,
        "explanation": item.explanation,
        "distractor_rationale": item.distractor_rationale,
        "misconception_tags": item.misconception_tags,
        "difficulty_b": float(item.difficulty_b),
        "discrimination_a": float(item.discrimination_a),
        "guessing_c": float(item.guessing_c),
        "review_status": getattr(item.review_status, "value", item.review_status),
        "reviewer_id": str(item.reviewer_id) if item.reviewer_id else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
        "exposure_count": item.exposure_count,
        "max_exposure": item.max_exposure,
        "quality_score": float(item.quality_score) if item.quality_score is not None else None,
        "safety_passed": item.safety_passed,
    }

@router.post("/item-bank/items/{item_id}/review")
async def review_item_bank_item(
    item_id: UUID,
    body: ReviewItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    _require_item_bank_admin(current_user)
    reviewer_id = UUID(current_user.user_id)
    item = await service.mark_item_reviewed(
        item_id=item_id,
        new_status=body.review_status,
        reviewer_id=reviewer_id,
        quality_score=body.quality_score,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item_id": str(item.item_id),
        "review_status": getattr(item.review_status, "value", item.review_status),
        "reviewer_id": str(item.reviewer_id) if item.reviewer_id else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
    }

class DiagnosticSessionStartRequest(BaseModel):
    learner_id: UUID
    caps_ref: str
    theta: float = 0.0

class DiagnosticSessionResponseRequest(BaseModel):
    item_id: UUID
    correct: bool
    response: str | None = None
    caps_ref: str | None = None

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def start_diagnostic_session(
    body: DiagnosticSessionStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    require_learner_write_for_current_user(current_user, str(body.learner_id))
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    snap = await service.start_session(body.learner_id, body.caps_ref, theta=body.theta)
    return snap.__dict__

@router.get("/sessions/{session_id}/recover")
async def recover_diagnostic_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    snap = await service.recover_session(session_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="No recoverable diagnostic session")
    learner = await service.get_learner(snap.learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, snap.learner_id)
    return snap.__dict__

@router.get("/sessions/{session_id}/next-item")
async def diagnostic_next_item(
    session_id: UUID,
    caps_ref: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    snap = await service.recover_session(session_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="No recoverable diagnostic session")
    learner = await service.get_learner(snap.learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, snap.learner_id)
    session_caps_ref = getattr(snap, "caps_ref", None) or caps_ref
    if session_caps_ref and str(caps_ref) != str(session_caps_ref):
        raise HTTPException(status_code=400, detail="caps_ref does not match recovered diagnostic session")
    items = list(await service.list_items_by_caps_ref(session_caps_ref, limit=200))
    item = await service.get_next_session_item(session_id, items)
    if item is None:
        return {"completed": True}
    return {
        "completed": False,
        "item_id": str(item.item_id),
        "caps_ref": item.caps_ref,
        "stem": item.stem,
        "options": item.options,
    }

@router.post("/sessions/{session_id}/respond")
async def diagnostic_respond(
    session_id: UUID,
    body: DiagnosticSessionResponseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
    service: DiagnosticDomainService = Depends(get_diagnostic_domain_service),
):
    if not isinstance(service, DiagnosticDomainService):
        service = get_diagnostic_domain_service(db)
    snap = await service.recover_session(session_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="No recoverable diagnostic session")
    require_learner_write_for_current_user(current_user, snap.learner_id)
    await require_active_consent_for_current_user(db, current_user, snap.learner_id)
    try:
        validate_adaptive_diagnostic_response(body.model_dump(), snapshot=snap, session_id=session_id)
    except DiagnosticIntegrityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    item = await service.get_item_bank_item(body.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Diagnostic item not found")
    result = await service.submit_session_response(session_id, item, correct=body.correct, response=body.response)
    return result.__dict__
