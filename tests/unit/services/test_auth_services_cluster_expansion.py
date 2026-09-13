import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.auth_runtime_boundary import (
    AuthRuntimeContext,
    _construct_repository,
    _extract_id,
    _import_symbol,
    _maybe_await,
    build_auth_runtime_context,
)
from app.services.auth_token_claims import (
    AuthTokenClaims,
    _as_string,
    _normalize_str_tuple,
    _read_value,
    build_access_token_claims,
)
from app.services.auth_transactional_registration import (
    AuthRegistrationInput,
    AuthRegistrationTransactionError,
    TransactionalAuthRegistrationService,
)


@pytest.mark.asyncio
async def test_auth_transactional_registration_complete():
    session = AsyncMock()
    # Async context manager for session.begin()
    session.begin = MagicMock(return_value=AsyncMock())

    users_table = MagicMock()
    users_table.insert.return_value.values.return_value = "insert_users"
    guardians_table = MagicMock()
    guardians_table.insert.return_value.values.return_value = "insert_guardians"
    learners_table = MagicMock()
    learners_table.insert.return_value.values.return_value = "insert_learners"

    service = TransactionalAuthRegistrationService(
        session=session,
        users_table=users_table,
        guardians_table=guardians_table,
        learners_table=learners_table,
    )

    # 1. Successful atomic registration
    inp = AuthRegistrationInput(
        email="parent@example.com",
        name="Parent One",
        password_hash="hashed_pw",
        learner_name="Learner One",
    )
    res = await service.register(inp)
    assert res.email == "parent@example.com"
    assert res.user_id is not None
    assert res.guardian_id is not None
    assert res.learner_id is not None
    assert session.execute.await_count == 3

    # 2. Simulated failure after user insert
    inp_user_fail = AuthRegistrationInput(
        email="p2@example.com",
        name="P2",
        password_hash="hpw",
        learner_name="L2",
        fail_after_user=True,
    )
    with pytest.raises(AuthRegistrationTransactionError, match="after user insert"):
        await service.register(inp_user_fail)

    # 3. Simulated failure after guardian insert
    inp_guardian_fail = AuthRegistrationInput(
        email="p3@example.com",
        name="P3",
        password_hash="hpw",
        learner_name="L3",
        fail_after_guardian=True,
    )
    with pytest.raises(AuthRegistrationTransactionError, match="after guardian insert"):
        await service.register(inp_guardian_fail)

    # 4. Simulated failure after learner insert
    inp_learner_fail = AuthRegistrationInput(
        email="p4@example.com",
        name="P4",
        password_hash="hpw",
        learner_name="L4",
        fail_after_learner=True,
    )
    with pytest.raises(AuthRegistrationTransactionError, match="after learner insert"):
        await service.register(inp_learner_fail)


@pytest.mark.asyncio
async def test_auth_runtime_boundary_complete():
    # 1. _import_symbol edge cases (lines 10-17)
    assert _import_symbol("invalidpath") is None
    assert _import_symbol(".invalid") is None
    assert _import_symbol("nonexistent.module.Symbol") is None
    assert _import_symbol("math.sqrt") is not None

    # 2. _construct_repository permutations and failure (lines 20-31)
    class PositionalRepo:
        def __init__(self, db):
            self.db = db

    class KeywordDbRepo:
        def __init__(self, *, db):
            self.db = db

    class KeywordSessionRepo:
        def __init__(self, *, session):
            self.session = session

    class EmptyRepo:
        def __init__(self):
            pass

    class UnconstructableRepo:
        def __init__(self, a, b, c):
            pass

    mock_db = MagicMock()
    assert isinstance(_construct_repository(PositionalRepo, mock_db), PositionalRepo)
    assert isinstance(_construct_repository(KeywordDbRepo, mock_db), KeywordDbRepo)
    assert isinstance(_construct_repository(KeywordSessionRepo, mock_db), KeywordSessionRepo)
    assert isinstance(_construct_repository(EmptyRepo, mock_db), EmptyRepo)

    with pytest.raises(RuntimeError, match="Cannot construct repository"):
        _construct_repository(UnconstructableRepo, mock_db)

    # 3. _maybe_await with sync value (line 37)
    assert await _maybe_await(42) == 42

    # 4. _extract_id permutations (lines 40-52)
    assert _extract_id(None) is None
    assert _extract_id({"learner_id": "l-1"}) == "l-1"
    assert _extract_id({"user_id": "u-1"}) == "u-1"
    assert _extract_id({"other": "val"}) == {"other": "val"}
    assert _extract_id(SimpleNamespace(user_id="u-2")) == "u-2"
    assert _extract_id("raw-id") == "raw-id"

    # 5. AuthRuntimeContext.guardian_learner_ids (lines 63-85)
    ctx_no_repo = AuthRuntimeContext(db=mock_db, learner_repo=None)
    assert await ctx_no_repo.guardian_learner_ids("g1") == []

    # Learner repo with type error on first call, success on second
    learner_repo = MagicMock()
    async def mock_list(guardian_id=None):
        if guardian_id == "error":
            raise TypeError("unexpected")
        return [{"id": "l-10"}, SimpleNamespace(learner_id="l-11"), None]

    learner_repo.get_by_guardian = mock_list
    ctx = AuthRuntimeContext(db=mock_db, learner_repo=learner_repo)
    assert await ctx.guardian_learner_ids("g1") == ["l-10", "l-11"]

    # When method raises TypeError on all attempts
    async def mock_fail(*args, **kwargs):
        raise TypeError("fail")
    learner_repo.get_by_guardian = mock_fail
    assert await ctx.guardian_learner_ids("g1") == []

    # 6. build_auth_runtime_context (lines 87-106)
    with patch("app.services.auth_runtime_boundary._import_symbol") as mock_imp:
        mock_imp.return_value = PositionalRepo
        built_ctx = build_auth_runtime_context(mock_db)
        assert built_ctx.learner_repo is not None


def test_auth_token_claims_complete():
    # 1. AuthTokenClaims.to_payload with all branches (lines 40-60)
    claims = AuthTokenClaims(
        sub="sub-1",
        user_id="u-1",
        role="learner",
        roles=("learner", "beta_tester"),
        guardian_learner_ids=("l-1", "l-2"),
        learner_id="l-1",
        parent_id="p-1",
        email_verified=True,
        extra={"custom_attr": "value", "none_attr": None, "sub": "ignored_override"},
    )
    payload = claims.to_payload()
    assert payload["sub"] == "sub-1"
    assert payload["role"] == "learner"
    assert payload["roles"] == ["learner", "beta_tester"]
    assert payload["guardian_learner_ids"] == ["l-1", "l-2"]
    assert payload["learner_id"] == "l-1"
    assert payload["parent_id"] == "p-1"
    assert payload["email_verified"] is True
    assert payload["custom_attr"] == "value"
    assert "none_attr" not in payload

    # 2. _as_string (lines 63-71)
    assert _as_string(None) is None
    assert _as_string("") is None
    assert _as_string(SimpleNamespace(value="parent")) == "parent"
    assert _as_string("regular_str") == "regular_str"

    # 3. _read_value (lines 74-86)
    assert _read_value(None, "id") is None
    assert _read_value({"k1": None, "k2": "val2"}, "k1", "k2") == "val2"
    assert _read_value(SimpleNamespace(attr1=None, attr2="val3"), "attr1", "attr2") == "val3"
    assert _read_value(SimpleNamespace(), "nonexistent") is None

    # 4. _normalize_str_tuple (lines 89-96)
    assert _normalize_str_tuple(None) == ()
    assert _normalize_str_tuple("") == ()
    assert _normalize_str_tuple("single") == ("single",)
    assert _normalize_str_tuple(["a", None, "", "b"]) == ("a", "b")
    assert _normalize_str_tuple(123) == ("123",)

    # 5. build_access_token_claims (lines 99-150)
    # Missing user id raises ValueError
    with pytest.raises(ValueError, match="Cannot build access-token claims without stable user id"):
        build_access_token_claims({})

    # Complete user dict
    user = {
        "id": "u-123",
        "role": "parent",
        "roles": ["parent"],
        "learner_ids": ["l-1"],
        "email_verified": True,
    }
    built = build_access_token_claims(user, extra={"tenant_id": "tenant-1"})
    assert built["user_id"] == "u-123"
    assert built["role"] == "parent"
    assert built["roles"] == ["parent"]
    assert built["guardian_learner_ids"] == ["l-1"]
    assert built["email_verified"] is True
    assert built["tenant_id"] == "tenant-1"
