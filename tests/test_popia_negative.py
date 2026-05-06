import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.api_v2 import app
from app.core import security as core_security

client = TestClient(app)

class FakeLearner:
    def __init__(self, id, guardian_id, deletion_requested_at=None, is_deleted=False, pseudonym_id="pseudo"):
        self.id = id
        self.guardian_id = guardian_id
        self.deletion_requested_at = deletion_requested_at
        self.is_deleted = is_deleted
        self.pseudonym_id = pseudonym_id
        self.display_name = "Test Learner"
        self.grade = 1
        self.language = "en"
        self.archetype = "default"
        self.theta = None
        self.xp = 0
        self.streak_days = 0
        self.created_at = None
        self.last_active = None

class FakeLearnerRepo:
    def __init__(self, db):
        self._learner = None
    
    async def get_by_id(self, learner_id):
        return self._learner

    async def purge_personal_data(self, learner_id):
        return True

class FakeConsentService:
    def __init__(self, db):
        pass
    async def require_active_consent(self, learner_id, actor_id=None):
        return True

class FakeFourthEstate:
    def __init__(self, db):
        pass
    async def record(self, *args, **kwargs):
        return True


@pytest.fixture(autouse=True)
def patch_repos_and_services(monkeypatch):
    # Patch LearnerRepository, ConsentService, FourthEstateService and current user dependency
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", FakeLearnerRepo)
    monkeypatch.setattr("app.api_v2_routers.popia.ConsentService", FakeConsentService)
    monkeypatch.setattr("app.api_v2_routers.popia.FourthEstateService", FakeFourthEstate)
    yield


def test_export_learner_data_not_found(monkeypatch):
    # current user can be anything; repo returns None
    async def fake_current_user():
        return {"sub": "user-1", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = None
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.get("/v2/popia/data-export/not-found-id")
    assert r.status_code == 404


def test_export_learner_data_forbidden_for_non_guardian(monkeypatch):
    async def fake_current_user():
        return {"sub": "other-user", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = FakeLearner(id="learner-1", guardian_id="guardian-123")
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.get("/v2/popia/data-export/learner-1")
    assert r.status_code == 403


def test_deletion_request_forbidden_non_guardian(monkeypatch):
    async def fake_current_user():
        return {"sub": "other-user", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = FakeLearner(id="learner-1", guardian_id="guardian-123")
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.post("/v2/popia/deletion-request/learner-1")
    assert r.status_code == 403


def test_deletion_request_conflict_if_already_requested(monkeypatch):
    async def fake_current_user():
        return {"sub": "guardian-123", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = FakeLearner(id="learner-1", guardian_id="guardian-123", deletion_requested_at=1)
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.post("/v2/popia/deletion-request/learner-1")
    assert r.status_code == 409


def test_cancel_deletion_conflict_no_request(monkeypatch):
    async def fake_current_user():
        return {"sub": "guardian-123", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = FakeLearner(id="learner-1", guardian_id="guardian-123", deletion_requested_at=None)
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.post("/v2/popia/deletion-cancel/learner-1")
    assert r.status_code == 409


def test_deletion_status_forbidden_for_non_guardian(monkeypatch):
    async def fake_current_user():
        return {"sub": "other-user", "role": "guardian"}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    repo = FakeLearnerRepo(None)
    repo._learner = FakeLearner(id="learner-1", guardian_id="guardian-123", deletion_requested_at=None)
    monkeypatch.setattr("app.api_v2_routers.popia.LearnerRepository", lambda db: repo)

    r = client.get("/v2/popia/deletion-status/learner-1")
    assert r.status_code == 403
