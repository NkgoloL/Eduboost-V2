from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi import HTTPException

import app.services.lesson_authorization as lesson_auth
from app.services.lesson_authorization import (
    iter_sync_lesson_ids,
    lesson_owner_learner_id,
    require_lesson_read_access_for_current_user,
    require_lesson_write_access_for_current_user,
)


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class FakeCurrentUser:
    allowed_learner_id: str


@dataclass
class FakeDB:
    owner_learner_id: str


class FakeLessonRepository:
    def __init__(self, db: FakeDB):
        self.db = db

    async def get_by_id(self, lesson_id: str) -> dict[str, Any]:
        return {"lesson_id": lesson_id, "learner_id": self.db.owner_learner_id}


class RepositoryOperationalFailure(Exception):
    pass


class ExplodingLessonRepository:
    def __init__(self, db: FakeDB):
        self.db = db

    async def get_by_id(self, lesson_id: str) -> dict[str, Any]:
        raise RepositoryOperationalFailure(f"database failure while loading {lesson_id}")


async def require_read(current_user: FakeCurrentUser, learner_id: str) -> None:
    if current_user.allowed_learner_id != str(learner_id):
        raise HTTPException(status_code=403, detail="Forbidden learner read")


async def require_write(current_user: FakeCurrentUser, learner_id: str) -> None:
    if current_user.allowed_learner_id != str(learner_id):
        raise HTTPException(status_code=403, detail="Forbidden learner write")


def install_symbol(monkeypatch: pytest.MonkeyPatch, dotted_path: str, symbol: object) -> None:
    module_name, _, attr = dotted_path.rpartition(".")
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        module = types.ModuleType(module_name)
        monkeypatch.setitem(sys.modules, module_name, module)
    setattr(module, attr, symbol)


def configure_candidates(monkeypatch: pytest.MonkeyPatch, repo_cls: type = FakeLessonRepository) -> None:
    install_symbol(monkeypatch, "tests.lesson_fakes.repo.LessonRepository", repo_cls)
    install_symbol(monkeypatch, "tests.lesson_fakes.authz.require_read", require_read)
    install_symbol(monkeypatch, "tests.lesson_fakes.authz.require_write", require_write)
    monkeypatch.setattr(lesson_auth, "LESSON_REPOSITORY_CANDIDATES", ("tests.lesson_fakes.repo.LessonRepository",))
    monkeypatch.setattr(lesson_auth, "LESSON_MODEL_CANDIDATES", ())
    monkeypatch.setattr(lesson_auth, "READ_AUTHZ_CANDIDATES", ("tests.lesson_fakes.authz.require_read",))
    monkeypatch.setattr(lesson_auth, "WRITE_AUTHZ_CANDIDATES", ("tests.lesson_fakes.authz.require_write",))


@pytest.mark.asyncio
async def test_lesson_owner_uses_repository_owner(monkeypatch: pytest.MonkeyPatch):
    configure_candidates(monkeypatch)

    owner = await lesson_owner_learner_id(FakeDB("learner-a"), "lesson-1")

    assert owner == "learner-a"


@pytest.mark.asyncio
async def test_cross_learner_read_is_denied(monkeypatch: pytest.MonkeyPatch):
    configure_candidates(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        await require_lesson_read_access_for_current_user(
            FakeDB("learner-owned-by-other-guardian"),
            FakeCurrentUser("learner-owned-by-current-guardian"),
            "lesson-1",
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cross_learner_write_is_denied(monkeypatch: pytest.MonkeyPatch):
    configure_candidates(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        await require_lesson_write_access_for_current_user(
            FakeDB("learner-owned-by-other-guardian"),
            FakeCurrentUser("learner-owned-by-current-guardian"),
            "lesson-1",
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_repository_operational_failure_is_not_hidden_as_404(monkeypatch: pytest.MonkeyPatch):
    configure_candidates(monkeypatch, repo_cls=ExplodingLessonRepository)

    with pytest.raises(RepositoryOperationalFailure):
        await lesson_owner_learner_id(FakeDB("learner-a"), "lesson-1")


@pytest.mark.asyncio
async def test_missing_lesson_still_returns_404_when_no_lookup_succeeds(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lesson_auth, "LESSON_REPOSITORY_CANDIDATES", ())
    monkeypatch.setattr(lesson_auth, "LESSON_MODEL_CANDIDATES", ())

    with pytest.raises(HTTPException) as exc:
        await lesson_owner_learner_id(FakeDB("learner-a"), "missing-lesson")

    assert exc.value.status_code == 404


def test_iter_sync_lesson_ids_remains_stable_for_nested_payloads():
    assert iter_sync_lesson_ids({"events": [{"lesson_id": "a"}, {"nested": {"lessonId": "b"}}]}) == ["a", "b"]
