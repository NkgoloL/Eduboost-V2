from __future__ import annotations
from app.services.popia_consent_lifecycle_adapter import POPIAConsentLifecycleAdapter

import inspect
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.consent.service import ConsentService
from app.repositories.consent_repository import ConsentRepository


def _load_learner_write_helper():
    candidates = (
        ("app.core.authorization", "require_learner_write_for_current_user"),
        ("app.core.authorization", "require_learner_write"),
        ("app.security.dependencies", "require_learner_write_for_current_user"),
        ("app.security.dependencies", "require_learner_write"),
        ("app.core.dependencies", "require_learner_write_for_current_user"),
        ("app.core.dependencies", "require_learner_write"),
    )
    for module_name, symbol_name in candidates:
        try:
            module = __import__(module_name, fromlist=[symbol_name])
            return getattr(module, symbol_name)
        except Exception:
            continue
    raise RuntimeError("No learner-write authorization helper found")


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def authenticated_actor_id(current_user: Any) -> Any:
    """Return stable authenticated actor identity for POPIA audit events."""
    if isinstance(current_user, dict):
        for key in ("id", "user_id", "sub"):
            value = current_user.get(key)
            if value:
                return value

    for attr in ("id", "user_id", "sub"):
        value = getattr(current_user, attr, None)
        if value:
            return value

    raise HTTPException(status_code=401, detail="Authenticated actor id is unavailable")


async def enforce_popia_learner_write(current_user: Any, learner_id: Any) -> Any:
    """Enforce learner write access for POPIA lifecycle mutations."""
    helper = _load_learner_write_helper()
    attempts = (
        ((current_user, learner_id), {}),
        ((learner_id, current_user), {}),
        ((), {"current_user": current_user, "learner_id": learner_id}),
        ((), {"user": current_user, "learner_id": learner_id}),
    )
    for args, kwargs in attempts:
        try:
            return await _maybe_await(helper(*args, **kwargs))
        except TypeError:
            continue
    raise RuntimeError(f"Could not call learner-write helper {helper!r}")


def get_canonical_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:
    """Construct the canonical SQLAlchemy-compatible consent service for FastAPI v2."""
    params = inspect.signature(ConsentService).parameters

    if "session" in params:
        return POPIAConsentLifecycleAdapter(ConsentService(session=db))
    if "db" in params:
        return POPIAConsentLifecycleAdapter(ConsentService(db=db))

    if "consent_repository" in params or "consent_repo" in params:
        repo = ConsentRepository(db)
        if "consent_repository" in params:
            return POPIAConsentLifecycleAdapter(ConsentService(consent_repository=repo))
        return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))

    try:
        return POPIAConsentLifecycleAdapter(ConsentService(db))
    except TypeError as exc:
        raise RuntimeError(
            "Cannot construct canonical ConsentService from AsyncSession. "
            "Align app.modules.consent.service.ConsentService constructor before using POPIA lifecycle routes."
        ) from exc


def get_canonical_data_rights_service(db: AsyncSession = Depends(get_db)):
    """Construct the canonical POPIA data rights service."""
    from app.services.popia_service import POPIADataRightsService
    return POPIADataRightsService(db)


__all__ = [
    "authenticated_actor_id",
    "enforce_popia_learner_write",
    "get_canonical_consent_service",
    "get_canonical_data_rights_service",
]
