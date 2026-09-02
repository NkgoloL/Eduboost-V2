"""Complete branch coverage expansion for AuthApplicationService."""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.auth_application_service import (
    AuthApplicationService,
    AuthApplicationServiceError,
    AuthRepositoryBundle,
    build_auth_application_service,
    construct_repository,
    extract_identifier,
    import_symbol,
)


@pytest.mark.unit
def test_import_symbol_and_construct_repository():
    assert import_symbol("") is None
    assert import_symbol("no_dot_symbol") is None
    assert import_symbol("non_existent.module.Class") is None
    assert import_symbol("app.services.auth_application_service.AuthApplicationService") is AuthApplicationService

    # construct_repository with database kwarg
    class RepoWithDatabase:
        def __init__(self, *, database):
            self.db = database

    repo = construct_repository(RepoWithDatabase, "db-conn")
    assert repo.db == "db-conn"

    # construct_repository failure
    class BrokenRepo:
        def __init__(self, a, b, c):
            pass

    with pytest.raises(AuthApplicationServiceError, match="Cannot construct repository"):
        construct_repository(BrokenRepo, "db-conn")


@pytest.mark.unit
def test_extract_identifier():
    assert extract_identifier(None) is None
    assert extract_identifier({"id": "id-1"}) == "id-1"
    assert extract_identifier({"learner_id": "lid-1"}) == "lid-1"
    assert extract_identifier({"user_id": "uid-1"}) == "uid-1"
    assert extract_identifier({"other": "val"}) == {"other": "val"}

    obj_id = SimpleNamespace(id="id-2")
    assert extract_identifier(obj_id) == "id-2"

    obj_lid = SimpleNamespace(learner_id="lid-2")
    assert extract_identifier(obj_lid) == "lid-2"

    obj_uid = SimpleNamespace(user_id="uid-2")
    assert extract_identifier(obj_uid) == "uid-2"

    assert extract_identifier("raw-string-id") == "raw-string-id"
    assert extract_identifier(12345) == 12345


@pytest.mark.unit
def test_auth_repository_bundle_cache_and_properties():
    mock_db = MagicMock()
    bundle = AuthRepositoryBundle(db=mock_db)

    # Pre-populate cache to test cache hit
    dummy_user_repo = object()
    bundle._cache["user_repo"] = dummy_user_repo
    assert bundle.user_repo is dummy_user_repo

    # Test failure when candidate cannot be found
    with patch.dict("app.services.auth_application_service.REPOSITORY_CANDIDATES", {"user_repo": ()}):
        bundle_empty = AuthRepositoryBundle(db=mock_db)
        with pytest.raises(AuthApplicationServiceError, match="No repository implementation found"):
            _ = bundle_empty.user_repo

    # Test all bundle properties with mocked _repo
    bundle_mocked = AuthRepositoryBundle(db=mock_db)
    bundle_mocked._repo = MagicMock(side_effect=lambda name: f"mocked_{name}")
    assert bundle_mocked.user_repo == "mocked_user_repo"
    assert bundle_mocked.guardian_repo == "mocked_guardian_repo"
    assert bundle_mocked.learner_repo == "mocked_learner_repo"
    assert bundle_mocked.consent_repo == "mocked_consent_repo"
    assert bundle_mocked.audit_repo == "mocked_audit_repo"
    assert bundle_mocked.refresh_token_repo == "mocked_refresh_token_repo"
    assert bundle_mocked.password_reset_repo == "mocked_password_reset_repo"


@pytest.mark.unit
def test_auth_application_service_properties_and_factory():
    mock_db = MagicMock()
    custom_bundle = MagicMock()
    svc = AuthApplicationService(db=mock_db, repositories=custom_bundle)
    assert svc.repositories is custom_bundle

    # Factory function
    svc2 = build_auth_application_service(mock_db)
    assert svc2.db == mock_db
    assert isinstance(svc2.repositories, AuthRepositoryBundle)

    # Service properties forwarding
    svc.repositories.user_repo = "u_repo"
    svc.repositories.guardian_repo = "g_repo"
    svc.repositories.learner_repo = "l_repo"
    svc.repositories.consent_repo = "c_repo"
    svc.repositories.audit_repo = "a_repo"
    svc.repositories.refresh_token_repo = "r_repo"
    svc.repositories.password_reset_repo = "p_repo"

    assert svc.user_repo == "u_repo"
    assert svc.guardian_repo == "g_repo"
    assert svc.learner_repo == "l_repo"
    assert svc.consent_repo == "c_repo"
    assert svc.audit_repo == "a_repo"
    assert svc.refresh_token_repo == "r_repo"
    assert svc.password_reset_repo == "p_repo"


@pytest.mark.asyncio
async def test_guardian_learner_ids_variations():
    mock_db = MagicMock()
    svc = AuthApplicationService(db=mock_db)

    # 1. Sync get_by_guardian with positional arg
    class Repo1:
        def get_by_guardian(self, g_id):
            return [{"id": "l-1"}, {"learner_id": "l-2"}]

    svc.repositories._cache["learner_repo"] = Repo1()
    res = await svc.guardian_learner_ids("g-1")
    assert res == ["l-1", "l-2"]

    # 2. Async list_by_guardian with keyword guardian_id
    class Repo2:
        async def list_by_guardian(self, *, guardian_id):
            return [SimpleNamespace(id="l-3"), "l-4"]

    svc.repositories._cache["learner_repo"] = Repo2()
    res = await svc.guardian_learner_ids("g-2")
    assert res == ["l-3", "l-4"]

    # 3. get_for_guardian with keyword parent_id
    class Repo3:
        def get_for_guardian(self, *, parent_id):
            return [{"user_id": "l-5"}]

    svc.repositories._cache["learner_repo"] = Repo3()
    res = await svc.guardian_learner_ids("g-3")
    assert res == ["l-5"]

    # 4. find_by_guardian returning None
    class Repo4:
        def find_by_guardian(self, g_id):
            return None

    svc.repositories._cache["learner_repo"] = Repo4()
    res = await svc.guardian_learner_ids("g-4")
    assert res == []

    # 5. Repo with no matching methods
    class RepoEmpty:
        pass

    svc.repositories._cache["learner_repo"] = RepoEmpty()
    res = await svc.guardian_learner_ids("g-5")
    assert res == []


@pytest.mark.asyncio
async def test_auth_service_methods_execution():
    svc = AuthApplicationService(db=MagicMock())

    # 1. create_dev_session
    mock_dev_impl = AsyncMock(return_value={"session": "dev"})
    res = await svc.create_dev_session(legacy_impl=mock_dev_impl, test_user="test")
    assert res == {"session": "dev"}

    # 2. login (sync impl return)
    mock_login_impl = MagicMock(return_value={"token": "tok"})
    res = await svc.login(legacy_impl=mock_login_impl, email="e@test.com")
    assert res == {"token": "tok"}

    # 3. refresh
    mock_ref_impl = AsyncMock(return_value={"refreshed": True})
    res = await svc.refresh(legacy_impl=mock_ref_impl, token="old")
    assert res == {"refreshed": True}

    # 4. register
    mock_reg_impl = AsyncMock(return_value={"user_id": "new-u"})
    res = await svc.register(legacy_impl=mock_reg_impl, email="reg@test.com")
    assert res == {"user_id": "new-u"}


@pytest.mark.asyncio
async def test_auth_repository_bundle_candidate_resolution():
    mock_db = MagicMock()
    # Test real candidate loop with a custom repository candidate
    with patch.dict("app.services.auth_application_service.REPOSITORY_CANDIDATES", {
        "custom_repo": ("non_existent.Repo", "app.services.auth_application_service.AuthRepositoryBundle")
    }):
        bundle = AuthRepositoryBundle(db=mock_db)
        repo = bundle._repo("custom_repo")
        assert isinstance(repo, AuthRepositoryBundle)


@pytest.mark.asyncio
async def test_auth_application_service_sync_returns():
    svc = AuthApplicationService(db=MagicMock())

    # Test sync results for methods
    sync_mock = MagicMock(return_value="sync-result")
    assert await svc._auth_service_call_impl("dummy", legacy_impl=sync_mock) == "sync-result"
    assert await svc.create_dev_session(legacy_impl=sync_mock) == "sync-result"
    assert await svc.login(legacy_impl=sync_mock) == "sync-result"
    assert await svc.refresh(legacy_impl=sync_mock) == "sync-result"
    assert await svc.register(legacy_impl=sync_mock) == "sync-result"


@pytest.mark.asyncio
async def test_logout_and_revoke_all_tokens():
    import app.services.auth_lifecycle_impl as impl_mod
    svc = AuthApplicationService(db=MagicMock())
    response_mock = MagicMock()

    # 1. When auth_lifecycle_impl has logout_impl (async) and revoke_all_tokens_impl (sync)
    async def custom_logout(service, *args, **kwargs):
        return {"logged_out": "custom"}

    def custom_revoke(service, *args, **kwargs):
        return {"revoked": "custom"}

    setattr(impl_mod, "logout_impl", custom_logout)
    setattr(impl_mod, "revoke_all_tokens_impl", custom_revoke)
    try:
        assert await svc.logout(user_id="u1") == {"logged_out": "custom"}
        assert await svc.revoke_all_tokens(user_id="u1") == {"revoked": "custom"}
    finally:
        delattr(impl_mod, "logout_impl")
        delattr(impl_mod, "revoke_all_tokens_impl")

    # 2. Fallback when methods return message
    res = await svc.logout(response=response_mock)
    assert res == {"message": "logout completed"}
    response_mock.delete_cookie.assert_called_with("refresh_token")

    res_rev = await svc.revoke_all_tokens(response=response_mock)
    assert res_rev == {"message": "revoke all tokens completed"}





