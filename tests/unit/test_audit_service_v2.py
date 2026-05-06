import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, UTC

from app.services.audit_service import AuditService
from app.models import AuditLog

@pytest.mark.unit
@pytest.mark.asyncio
async def test_audit_service_log_consent_granted():
    # Mock repository
    repo = AsyncMock()
    # service = AuditService(db=MagicMock()) # It takes db in __init__ usually? 
    # Wait, the current app/services/audit_service.py takes 'repository'.
    # But app/core/audit.py (FourthEstate) takes 'db'.
    
    # I'll standardize on taking 'db' and creating the repo internally, 
    # or taking the repo as a dependency.
    
    repo.append.return_value = MagicMock(id=uuid4(), created_at=datetime.now(UTC))
    service = AuditService(repository=repo)
    
    await service.consent_granted(
        guardian_id=str(uuid4()),
        learner_id=str(uuid4()),
        policy_version="1.0"
    )
    
    repo.append.assert_called_once()
    args, kwargs = repo.append.call_args
    assert kwargs["event_type"] == "CONSENT_GRANTED"
    assert kwargs["payload"]["policy_version"] == "1.0"
