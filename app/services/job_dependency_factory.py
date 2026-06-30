from __future__ import annotations

import importlib
import inspect
from contextlib import asynccontextmanager
from typing import Any


def _import_symbol(path: str) -> Any | None:
    module_name, _, attr = path.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    return getattr(module, attr, None)


def _session_factory() -> Any:
    for candidate in (
        "app.core.database.AsyncSessionLocal",
        "app.core.database.async_session_maker",
        "app.core.database.SessionLocal",
        "app.database.AsyncSessionLocal",
    ):
        symbol = _import_symbol(candidate)
        if symbol is not None:
            return symbol
    raise RuntimeError("No async DB session factory found for durable jobs")


@asynccontextmanager
async def durable_job_session():
    session = _session_factory()()
    try:
        yield session
    finally:
        close = getattr(session, "close", None)
        if close is not None:
            result = close()
            if inspect.isawaitable(result):
                await result


def _construct(cls: Any, *preferred_args: Any, **preferred_kwargs: Any) -> Any:
    for args, kwargs in ((preferred_args, preferred_kwargs), (preferred_args, {}), ((), preferred_kwargs), ((), {})):
        try:
            return cls(*args, **kwargs)
        except TypeError:
            continue
    raise RuntimeError(f"Cannot construct {cls!r}")


def build_consent_service_for_job(session: Any) -> Any:
    service_cls = _import_symbol("app.modules.consent.service.ConsentService")
    consent_repo_cls = _import_symbol("app.repositories.consent_repository.ConsentRepository")
    audit_repo_cls = _import_symbol("app.repositories.audit_repository.AuditRepository") or _import_symbol("app.repositories.repositories.AuditRepository")
    if service_cls is None:
        raise RuntimeError("Canonical ConsentService not found")

    consent_repo = _construct(consent_repo_cls, session) if consent_repo_cls is not None else None
    audit_repo = _construct(audit_repo_cls, session) if audit_repo_cls is not None else None
    params = inspect.signature(service_cls).parameters
    kwargs: dict[str, Any] = {}
    if "session" in params:
        kwargs["session"] = session
    if "db" in params:
        kwargs["db"] = session
    if consent_repo is not None:
        if "consent_repository" in params:
            kwargs["consent_repository"] = consent_repo
        if "consent_repo" in params:
            kwargs["consent_repo"] = consent_repo
    if audit_repo is not None:
        if "audit_repository" in params:
            kwargs["audit_repository"] = audit_repo
        if "audit_repo" in params:
            kwargs["audit_repo"] = audit_repo

    if kwargs:
        return service_cls(**kwargs)
    return _construct(service_cls, session)


async def run_consent_reminder_cycle(ctx: dict[str, Any] | None = None) -> None:
    async with durable_job_session() as session:
        service = build_consent_service_for_job(session)
        method = (
            getattr(service, "send_consent_renewal_reminders", None)
            or getattr(service, "send_renewal_reminders", None)
            or getattr(service, "send_consent_reminders", None)
            or getattr(service, "process_renewal_reminders", None)
        )
        if method is None:
            return
        result = method()
        if inspect.isawaitable(result):
            await result
