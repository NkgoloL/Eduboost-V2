from __future__ import annotations

import importlib
import inspect
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select


LESSON_MODEL_CANDIDATES = (
    "app.models.lesson.Lesson",
    "app.models.lessons.Lesson",
    "app.modules.lessons.models.Lesson",
)

LESSON_REPOSITORY_CANDIDATES = (
    "app.repositories.lesson_repository.LessonRepository",
    "app.modules.lessons.repository.LessonRepository",
)

READ_AUTHZ_CANDIDATES = (
    "app.core.authorization.require_learner_read_for_current_user",
    "app.core.authorization.require_learner_read",
    "app.security.dependencies.require_learner_read_for_current_user",
    "app.security.dependencies.require_learner_read",
)

WRITE_AUTHZ_CANDIDATES = (
    "app.core.authorization.require_learner_write_for_current_user",
    "app.core.authorization.require_learner_write",
    "app.security.dependencies.require_learner_write_for_current_user",
    "app.security.dependencies.require_learner_write",
)


async def _maybe_await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def _import_dotted(path: str) -> Any | None:
    module_name, _, attr = path.rpartition(".")
    try:
        return getattr(importlib.import_module(module_name), attr)
    except Exception:
        return None


def _first_import(candidates: tuple[str, ...]) -> Any | None:
    for candidate in candidates:
        symbol = _import_dotted(candidate)
        if symbol is not None:
            return symbol
    return None


def _owner_from_result(result: Any) -> Any | None:
    if result is None:
        return None
    if isinstance(result, tuple) and len(result) >= 2:
        return result[1]
    if isinstance(result, dict):
        for key in ("learner_id", "owner_learner_id", "student_id"):
            if result.get(key) is not None:
                return result[key]
        if result.get("lesson") is not None:
            return _owner_from_result(result["lesson"])
    for attr in ("learner_id", "owner_learner_id", "student_id"):
        value = getattr(result, attr, None)
        if value is not None:
            return value
    return None


async def _call_repo_method(repo: Any, method_name: str, lesson_id: Any, db: Any) -> Any:
    method = getattr(repo, method_name, None)
    if method is None:
        return None
    for args, kwargs in (
        ((lesson_id, db), {}),
        ((lesson_id,), {}),
        ((), {"lesson_id": lesson_id, "db": db}),
        ((), {"lesson_id": lesson_id, "session": db}),
        ((), {"id": lesson_id, "db": db}),
        ((), {"id": lesson_id}),
    ):
        try:
            return await _maybe_await(method(*args, **kwargs))
        except TypeError:
            continue
    return None


def _construct_repo(repo_cls: type, db: Any) -> Any:
    for args, kwargs in (((db,), {}), ((), {"db": db}), ((), {"session": db}), ((), {})):
        try:
            return repo_cls(*args, **kwargs)
        except TypeError:
            continue
    raise RuntimeError(f"Cannot construct lesson repository {repo_cls!r}")


async def lesson_owner_learner_id(db: Any, lesson_id: Any) -> Any:
    repo_cls = _first_import(LESSON_REPOSITORY_CANDIDATES)
    if repo_cls is not None:
        try:
            repo = _construct_repo(repo_cls, db)
            for method_name in ("get_by_id_with_learner", "get_with_learner", "get_by_id", "get", "get_lesson"):
                owner = _owner_from_result(await _call_repo_method(repo, method_name, lesson_id, db))
                if owner is not None:
                    return owner
        except Exception:
            pass

    model = _first_import(LESSON_MODEL_CANDIDATES)
    if model is not None and hasattr(db, "execute"):
        result = await db.execute(select(model).where(model.id == lesson_id))
        scalar_one_or_none = getattr(result, "scalar_one_or_none", None)
        lesson = scalar_one_or_none() if callable(scalar_one_or_none) else None
        owner = _owner_from_result(lesson)
        if owner is not None:
            return owner

    raise HTTPException(status_code=404, detail="Lesson not found")


async def _call_authz(fn: Any, current_user: Any, learner_id: Any) -> Any:
    for args, kwargs in (
        ((current_user, learner_id), {}),
        ((learner_id, current_user), {}),
        ((), {"current_user": current_user, "learner_id": learner_id}),
        ((), {"user": current_user, "learner_id": learner_id}),
    ):
        try:
            return await _maybe_await(fn(*args, **kwargs))
        except TypeError:
            continue
    raise RuntimeError(f"Could not call learner authorization helper {fn!r}")


async def require_lesson_read_access_for_current_user(db: Any, current_user: Any, lesson_id: Any) -> Any:
    owner = await lesson_owner_learner_id(db, lesson_id)
    fn = _first_import(READ_AUTHZ_CANDIDATES)
    if fn is None:
        raise RuntimeError("No learner-read authorization helper found")
    return await _call_authz(fn, current_user, owner)


async def require_lesson_write_access_for_current_user(db: Any, current_user: Any, lesson_id: Any) -> Any:
    owner = await lesson_owner_learner_id(db, lesson_id)
    fn = _first_import(WRITE_AUTHZ_CANDIDATES)
    if fn is None:
        raise RuntimeError("No learner-write authorization helper found")
    return await _call_authz(fn, current_user, owner)


def iter_sync_lesson_ids(payload: Any) -> list[Any]:
    found: list[Any] = []
    seen: set[int] = set()

    def walk(value: Any) -> None:
        if value is None or isinstance(value, (str, bytes, bytearray, UUID)):
            return
        marker = id(value)
        if marker in seen:
            return
        seen.add(marker)

        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"lesson_id", "lessonId"} and item is not None:
                    found.append(item)
                else:
                    walk(item)
            return

        if isinstance(value, Iterable):
            for item in value:
                walk(item)
            return

        for attr in ("lesson_id", "lessonId"):
            item = getattr(value, attr, None)
            if item is not None:
                found.append(item)

        for attr in ("events", "items", "lessons", "updates", "payload"):
            child = getattr(value, attr, None)
            if child is not None:
                walk(child)

    walk(payload)
    return found


__all__ = [
    "iter_sync_lesson_ids",
    "lesson_owner_learner_id",
    "require_lesson_read_access_for_current_user",
    "require_lesson_write_access_for_current_user",
]
