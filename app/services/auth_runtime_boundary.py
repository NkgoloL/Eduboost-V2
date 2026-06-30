from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from typing import Any


def _import_symbol(path: str) -> Any | None:
    module_name, _, attr = path.rpartition(".")
    if not module_name or not attr:
        return None
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    return getattr(module, attr, None)


def _construct_repository(repository_cls: Any, db: Any) -> Any:
    for args, kwargs in (
        ((db,), {}),
        ((), {"db": db}),
        ((), {"session": db}),
        ((), {}),
    ):
        try:
            return repository_cls(*args, **kwargs)
        except TypeError:
            continue
    raise RuntimeError(f"Cannot construct repository {repository_cls!r} with current database session")


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _extract_id(value: Any) -> Any | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("id", "learner_id", "user_id"):
            if value.get(key) is not None:
                return value[key]
    for attr in ("id", "learner_id", "user_id"):
        item = getattr(value, attr, None)
        if item is not None:
            return item
    return value


@dataclass
class AuthRuntimeContext:
    """Runtime dependencies used by auth routes without direct router repositories."""

    db: Any
    learner_repo: Any | None = None
    consent_repo: Any | None = None
    guardian_repo: Any | None = None

    async def guardian_learner_ids(self, guardian_id: Any) -> list[Any]:
        if self.learner_repo is None:
            return []

        for method_name in ("get_by_guardian", "list_by_guardian", "get_for_guardian", "find_by_guardian"):
            method = getattr(self.learner_repo, method_name, None)
            if method is None:
                continue

            attempts = (
                ((guardian_id,), {}),
                ((), {"guardian_id": guardian_id}),
                ((), {"parent_id": guardian_id}),
            )
            for args, kwargs in attempts:
                try:
                    result = await _maybe_await(method(*args, **kwargs))
                    return [_extract_id(item) for item in (result or []) if _extract_id(item) is not None]
                except TypeError:
                    continue

        return []


def build_auth_runtime_context(db: Any) -> AuthRuntimeContext:
    # code_1271_1310_auth_repository_fixture_candidate_order
    learner_repo_cls = (
        _import_symbol("app.repositories.repositories.LearnerRepository")
        or _import_symbol("app.repositories.learner_repository.LearnerRepository")
    )
    consent_repo_cls = (
        _import_symbol("app.repositories.repositories.ConsentRepository")
        or _import_symbol("app.repositories.consent_repository.ConsentRepository")
    )
    guardian_repo_cls = (
        _import_symbol("app.repositories.repositories.GuardianRepository")
        or _import_symbol("app.repositories.auth_repository.GuardianRepository")
        or _import_symbol("app.repositories.guardian_repository.GuardianRepository")
    )
    learner_repo = _construct_repository(learner_repo_cls, db) if learner_repo_cls is not None else None
    consent_repo = _construct_repository(consent_repo_cls, db) if consent_repo_cls is not None else None
    guardian_repo = _construct_repository(guardian_repo_cls, db) if guardian_repo_cls is not None else None
    return AuthRuntimeContext(db=db, learner_repo=learner_repo, consent_repo=consent_repo, guardian_repo=guardian_repo)


__all__ = ["AuthRuntimeContext", "build_auth_runtime_context"]
