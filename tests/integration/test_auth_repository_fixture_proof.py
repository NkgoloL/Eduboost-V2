from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import decode_token, hash_email, hash_password, verify_password
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest
from app.models import Guardian, Learner, UserRole
from app.services import auth_lifecycle_impl
from app.services.auth_application_service import build_auth_application_service


class NoopAudit:
    def __init__(self, db):
        self.db = db

    async def auth_event(self, *args, **kwargs):
        return None


@pytest.fixture
async def auth_repo_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Guardian.__table__.create, checkfirst=True)
        await conn.run_sync(Learner.__table__.create, checkfirst=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture(autouse=True)
def safe_auth_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("JWT_SECRET", "auth-repository-fixture-secret-123456")


@pytest.fixture
def auth_side_effects(monkeypatch):
    stored_tokens: list[str] = []

    async def store_refresh_token(token: str) -> None:
        stored_tokens.append(token)

    monkeypatch.setattr(auth_lifecycle_impl, "store_refresh_token", store_refresh_token)
    monkeypatch.setattr(auth_lifecycle_impl, "FourthEstateService", NoopAudit)
    return stored_tokens


@pytest.mark.asyncio
async def test_auth_application_service_resolves_session_bound_repositories(auth_repo_session):
    service = build_auth_application_service(auth_repo_session)

    assert service.guardian_repo.__class__.__module__ == "app.repositories.repositories"
    assert service.learner_repo.__class__.__module__ == "app.repositories.repositories"
    assert service.consent_repo.__class__.__module__ == "app.repositories.repositories"


@pytest.mark.asyncio
async def test_register_and_login_use_actual_guardian_repository(auth_repo_session, auth_side_effects):
    service = build_auth_application_service(auth_repo_session)
    email = "repo.proof.guardian@example.com"
    password = "RepoProofPass123!"

    register_response = await service.register(
        request=SimpleNamespace(),
        body=RegisterRequest(email=email, password=password, display_name="Repo Proof Guardian", role="parent"),
        response=Response(),
        db=auth_repo_session,
        auth_runtime=service,
    )

    assert register_response.access_token
    guardian = await service.guardian_repo.get_by_email_hash(hash_email(email))
    assert guardian is not None
    assert guardian.email_encrypted
    assert verify_password(password, guardian.password_hash)
    assert auth_side_effects

    login_response = await service.login(
        request=SimpleNamespace(),
        body=LoginRequest(email=email, password=password),
        response=Response(),
        db=auth_repo_session,
        auth_runtime=service,
    )
    assert login_response.access_token

    with pytest.raises(HTTPException) as wrong_password:
        await service.login(
            request=SimpleNamespace(),
            body=LoginRequest(email=email, password="wrong-password"),
            response=Response(),
            db=auth_repo_session,
            auth_runtime=service,
        )
    assert wrong_password.value.status_code == 401

    with pytest.raises(HTTPException) as duplicate:
        await service.register(
            request=SimpleNamespace(),
            body=RegisterRequest(email=email, password=password, display_name="Duplicate", role="parent"),
            response=Response(),
            db=auth_repo_session,
            auth_runtime=service,
        )
    assert duplicate.value.status_code == 409


@pytest.mark.asyncio
async def test_refresh_preserves_learner_scope_from_actual_learner_repository(auth_repo_session, monkeypatch, auth_side_effects):
    service = build_auth_application_service(auth_repo_session)
    guardian = await service.guardian_repo.create(
        email_hash=hash_email("scope.guardian@example.com"),
        email_encrypted="encrypted-email",
        display_name="Scope Guardian",
        role=UserRole.PARENT,
        password_hash=hash_password("ScopePass123!"),
    )
    learner = await service.learner_repo.create(
        guardian_id=guardian.id,
        display_name="Scope Learner",
        grade=3,
        language="en",
    )

    async def consume_refresh_token(token: str):
        return {"sub": guardian.id, "family": "family-1", "jti": "old-jti", "type": "refresh"}

    monkeypatch.setattr(auth_lifecycle_impl, "consume_refresh_token", consume_refresh_token)

    result = await service.refresh(
        request=SimpleNamespace(),
        response=Response(),
        body=RefreshRequest(refresh_token="opaque-refresh-token"),
        db=auth_repo_session,
        cookie_refresh=None,
        auth_runtime=service,
    )

    claims = decode_token(result.access_token)
    assert str(learner.id) in claims.get("guardian_learner_ids", [])
