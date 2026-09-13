import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.consent import ConsentRecord, ConsentState
from app.services.popia_consent_lifecycle_adapter import (
    POPIAConsentLifecycleAdapter,
    _coerce_consent_record,
    _dump_candidate,
    _maybe_await,
    _value,
)


@pytest.mark.asyncio
async def test_popia_consent_adapter_helpers():
    # 1. _maybe_await with sync value (line 15)
    assert await _maybe_await("sync_value") == "sync_value"

    # 2. _value helper (lines 18-22)
    assert _value({"k2": "v2"}, "k1", "k2") == "v2"
    assert _value({}, "k1", default="def") == "def"

    # 3. _dump_candidate with primitives and objects (lines 66-101)
    assert _dump_candidate(None) == {}
    assert _dump_candidate(123) == {}
    assert _dump_candidate("string") == {}

    # ConsentRecord instance (line 68 and 113)
    now = datetime.now(timezone.utc)
    rec = ConsentRecord(
        id=uuid.uuid4(),
        learner_id=uuid.uuid4(),
        guardian_id=uuid.uuid4(),
        privacy_notice_version="1.0",
        state=ConsentState.GRANTED,
        created_at=now,
        updated_at=now,
    )
    assert _dump_candidate(rec)["privacy_notice_version"] == "1.0"
    assert _coerce_consent_record(rec, {}, fallback_state=ConsentState.GRANTED) is rec

    # Object with model_dump returning a valid dict (lines 75-76)
    class GoodDumpObj:
        def model_dump(self):
            return {"id": "dump-1", "status": "active"}
    assert _dump_candidate(GoodDumpObj())["id"] == "dump-1"

    # Object with model_dump raising exception (line 77-78)
    class BrokenDumpObj:
        def model_dump(self):
            raise RuntimeError("fail")
        id = "obj-id-1"
    dumped = _dump_candidate(BrokenDumpObj())
    assert dumped["id"] == "obj-id-1"



@pytest.mark.asyncio
async def test_popia_consent_adapter_lifecycle():
    mock_service = MagicMock()

    # 1. grant method (lines 215-218)
    mock_service.grant = AsyncMock(return_value={"id": str(uuid.uuid4()), "status": "active"})
    adapter = POPIAConsentLifecycleAdapter(mock_service)

    res_grant = await adapter.grant(guardian_id="g1", learner_id="l1", privacy_notice_version="2.0")
    assert isinstance(res_grant, ConsentRecord)
    assert res_grant.state == ConsentState.GRANTED

    # 2. deny method: when service has deny vs fallback to revoke (lines 220-227)
    # With deny
    mock_service.deny = AsyncMock(return_value={"status": "denied", "reason": "Parent refusal"})
    res_deny = await adapter.deny(guardian_id="g1", learner_id="l1")
    assert res_deny.state == ConsentState.DENIED

    # Without deny (fallback to revoke)
    mock_service_no_deny = MagicMock(spec=["revoke"])
    mock_service_no_deny.revoke = AsyncMock(return_value=1)  # returns int rowcount
    adapter_no_deny = POPIAConsentLifecycleAdapter(mock_service_no_deny)
    res_deny_fallback = await adapter_no_deny.deny(guardian_id="g1", learner_id="l1")
    assert res_deny_fallback.state == ConsentState.DENIED

    # 3. withdraw and revoke methods (lines 229-237)
    mock_service.withdraw = AsyncMock(return_value={"status": "withdrawn"})
    res_withdraw = await adapter.withdraw("g1", "l1")
    assert res_withdraw.state == ConsentState.WITHDRAWN

    mock_service.revoke = AsyncMock(return_value={"status": "revoked"})
    res_revoke = await adapter.revoke("g1", "l1")
    assert res_revoke.state == ConsentState.WITHDRAWN

    # 4. renew method: when service has renew vs fallback to grant (lines 239-245)
    mock_service.renew = AsyncMock(return_value={"status": "approved"})
    res_renew = await adapter.renew(guardian_id="g1", learner_id="l1")
    assert res_renew.state == ConsentState.GRANTED

    mock_service_no_renew = MagicMock(spec=["grant"])
    mock_service_no_renew.grant = AsyncMock(return_value={"status": "active"})
    adapter_no_renew = POPIAConsentLifecycleAdapter(mock_service_no_renew)
    res_renew_fallback = await adapter_no_renew.renew(guardian_id="g1", learner_id="l1")
    assert res_renew_fallback.state == ConsentState.GRANTED

    # 5. erase and restrict_processing (lines 247-251)
    mock_service.erase = AsyncMock(return_value={"erased": True})
    assert await adapter.erase("g1", "l1") == {"erased": True}

    mock_service.restrict_processing = AsyncMock(return_value={"restricted": True})
    assert await adapter.restrict_processing("g1", "l1") == {"restricted": True}

    # 6. __getattr__ delegation (lines 253-254)
    mock_service.custom_attr = "custom_value"
    assert adapter.custom_attr == "custom_value"

    # 7. _call missing method error (line 205)
    empty_adapter = POPIAConsentLifecycleAdapter(MagicMock(spec=[]))
    with pytest.raises(AttributeError, match="Canonical consent service lacks methods"):
        await empty_adapter._call(("nonexistent_method",))

    # 8. Positional argument binding in _call (lines 187-202)
    class AlternateParamService:
        async def custom_method(self, parent_id, version, user_id):
            return {"status": "ok", "parent_id": parent_id, "version": version, "user_id": user_id}

        async def unmapped_method(self, something_unknown):
            return {"status": "unmapped", "something_unknown": something_unknown}

    adapter_alt = POPIAConsentLifecycleAdapter(AlternateParamService())
    res_alt = await adapter_alt._call(
        ("custom_method",),
        guardian_id="g1",
        consent_version="2.0",
        actor_id="u1",
    )
    assert res_alt["parent_id"] == "g1"
    assert res_alt["version"] == "2.0"
    assert res_alt["user_id"] == "u1"

    # Test learner_id param (line 192)
    class LearnerParamService:
        async def learner_method(self, learner_id):
            return {"learner_id": learner_id}

    adapter_learner = POPIAConsentLifecycleAdapter(LearnerParamService())
    res_learner = await adapter_learner._call(("learner_method",), learner_id="l123")
    assert res_learner["learner_id"] == "l123"

    # Test unmapped param (hits line 198 break)
    with pytest.raises(TypeError):
        await adapter_alt._call(("unmapped_method",), guardian_id="g1")


