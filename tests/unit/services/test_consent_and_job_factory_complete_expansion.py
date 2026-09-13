from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.consent_runtime_compatibility import (
    CONSENT_SERVICE_CANDIDATES,
    POPIA_SERVICE_CANDIDATES,
    ConsentRuntimeOperation,
    ConstructorProbe,
    normalize_consent_runtime_operation,
    probe_constructor,
    probe_known_consent_surfaces,
)
from app.services.consent_runtime_orchestrator import (
    ConsentRuntimeCompatibilitySummary,
    build_consent_runtime_audit_payload,
    summarize_consent_runtime_surfaces,
)
from app.services.job_dependency_factory import (
    _construct,
    _import_symbol,
    _session_factory,
    build_consent_service_for_job,
    durable_job_session,
    run_consent_reminder_cycle,
)


def test_consent_runtime_compatibility_probes():
    # 1. Probe known candidates
    probes = probe_known_consent_surfaces()
    assert len(probes) >= 2
    for p in probes:
        assert isinstance(p, ConstructorProbe)

    # 2. Probe nonexistent module
    p_nonexistent = probe_constructor("app.nonexistent.module.Class")
    assert p_nonexistent.importable is False
    assert "ModuleNotFoundError" in (p_nonexistent.error or "")

    # 3. Probe existing module with missing class
    p_missing_cls = probe_constructor("app.services.consent_runtime_compatibility.MissingClass")
    assert p_missing_cls.importable is True
    assert p_missing_cls.class_found is False


def test_consent_runtime_operations_normalization():
    # 1. Read operation
    op_read = normalize_consent_runtime_operation(
        action="consent.status.read",
        actor_id="actor_1",
        learner_id="learner_1",
    )
    assert op_read.operation_type == "read"
    evt = op_read.to_audit_event()
    assert evt["action"] == "consent.status.read"
    assert evt["metadata"]["operation_type"] == "read"

    # 2. Write operation
    op_write = normalize_consent_runtime_operation(
        action="consent.grant",
        actor_id="actor_1",
        learner_id="learner_1",
    )
    assert op_write.operation_type == "write"

    # 3. Unknown operation
    op_unknown = normalize_consent_runtime_operation(
        action="something.else",
        actor_id="actor_1",
        learner_id="learner_1",
    )
    assert op_unknown.operation_type == "unknown"

    # 4. Validation errors
    with pytest.raises(ValueError, match="action is required"):
        normalize_consent_runtime_operation(action="", actor_id="a", learner_id="l")
    with pytest.raises(ValueError, match="actor_id is required"):
        normalize_consent_runtime_operation(action="act", actor_id="", learner_id="l")
    with pytest.raises(ValueError, match="learner_id is required"):
        normalize_consent_runtime_operation(action="act", actor_id="a", learner_id="")


def test_consent_runtime_orchestrator():
    summary = summarize_consent_runtime_surfaces()
    assert isinstance(summary, ConsentRuntimeCompatibilitySummary)
    assert summary.write_operation_supported is True
    assert summary.read_operation_supported is True

    payload = build_consent_runtime_audit_payload(
        action="consent.granted",
        actor_id="admin_1",
        learner_id="learner_1",
        channel="web",
    )
    assert payload["metadata"]["consent_runtime_orchestrated"] is True
    assert payload["metadata"]["channel"] == "web"


@pytest.mark.asyncio
async def test_job_dependency_factory_components():
    # 1. _import_symbol
    assert _import_symbol("app.services.job_dependency_factory.durable_job_session") is durable_job_session
    assert _import_symbol("nonexistent.module.symbol") is None

    # 2. _construct helper
    class Demo:
        def __init__(self, a=1, b=2):
            self.a = a
            self.b = b
    obj = _construct(Demo, 10, b=20)
    assert obj.a == 10 and obj.b == 20

    class Impossible:
        def __init__(self, required_1, required_2):
            pass
    with pytest.raises(RuntimeError, match="Cannot construct"):
        _construct(Impossible, 1)

    # 3. durable_job_session context manager
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.job_dependency_factory._session_factory", lambda: lambda: mock_session)
        async with durable_job_session() as s:
            assert s is mock_session
        assert mock_session.close.await_count == 1

    # 4. _session_factory failure when none available
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.job_dependency_factory._import_symbol", lambda path: None)
        with pytest.raises(RuntimeError, match="No async DB session factory found"):
            _session_factory()

    # 5. build_consent_service_for_job with explicit parameter signature
    class MockTargetService:
        def __init__(self, session=None, db=None, consent_repository=None, consent_repo=None, audit_repository=None, audit_repo=None):
            self.session = session
            self.db = db
            self.consent_repository = consent_repository
            self.consent_repo = consent_repo
            self.audit_repository = audit_repository
            self.audit_repo = audit_repo

    class DummyConsentRepo:
        def __init__(self, session=None):
            self.session = session

    class DummyAuditRepo:
        def __init__(self, session=None):
            self.session = session

    def import_stub(path):
        if "ConsentService" in path:
            return MockTargetService
        if "consent_repository" in path:
            return DummyConsentRepo
        if "audit_repository" in path:
            return DummyAuditRepo
        return None

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.job_dependency_factory._import_symbol", import_stub)
        svc = build_consent_service_for_job(mock_session)
        assert svc.session is mock_session
        assert svc.db is mock_session
        assert svc.consent_repository is not None
        assert svc.audit_repository is not None


    # Service cls None error
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.job_dependency_factory._import_symbol", lambda path: None)
        with pytest.raises(RuntimeError, match="Canonical ConsentService not found"):
            build_consent_service_for_job(mock_session)

    # 6. run_consent_reminder_cycle
    mock_service_instance = MagicMock()
    mock_service_instance.send_consent_renewal_reminders = AsyncMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.job_dependency_factory.build_consent_service_for_job", lambda s: mock_service_instance)
        mp.setattr("app.services.job_dependency_factory.durable_job_session", lambda: mock_session_ctx(mock_session))
        await run_consent_reminder_cycle()
        assert mock_service_instance.send_consent_renewal_reminders.await_count == 1

        # Service with no reminder method
        mp.setattr("app.services.job_dependency_factory.build_consent_service_for_job", lambda s: object())
        await run_consent_reminder_cycle()



from contextlib import asynccontextmanager

@asynccontextmanager
async def mock_session_ctx(session):
    yield session
