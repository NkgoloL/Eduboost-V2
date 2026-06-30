"""tests/unit/test_popia_service_authority.py
T111D: Verify POPIADataRightsService is authoritative for FastAPI v2

Ensures that no v2 routers or services import the legacy DataSubjectRightsService,
which is documented as non-authoritative in ADR-004.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.unit
def test_no_v2_routers_import_legacy_data_subject_rights_service():
    """Verify no FastAPI v2 routers import legacy DataSubjectRightsService."""
    repo_root = Path(__file__).resolve().parents[2]
    routers_dir = repo_root / "app" / "api_v2_routers"

    # Find all Python files in api_v2_routers
    router_files = list(routers_dir.glob("*.py"))

    legacy_import_patterns = [
        "from app.services.data_subject_rights_service import",
        "from app.services import data_subject_rights_service",
        "import app.services.data_subject_rights_service",
    ]

    violations = []
    for router_file in router_files:
        content = router_file.read_text(encoding="utf-8")
        for pattern in legacy_import_patterns:
            if pattern in content:
                violations.append((str(router_file.relative_to(repo_root)), pattern))

    assert len(violations) == 0, (
        f"Found {len(violations)} v2 router(s) importing legacy DataSubjectRightsService:\n"
        + "\n".join(f"  - {file}: {pattern}" for file, pattern in violations)
    )


@pytest.mark.unit
def test_no_v2_services_import_legacy_data_subject_rights_service():
    """Verify no FastAPI v2 services import legacy DataSubjectRightsService."""
    repo_root = Path(__file__).resolve().parents[2]
    services_dir = repo_root / "app" / "services"

    # Find all Python files in app/services (excluding the legacy file itself)
    service_files = [f for f in services_dir.glob("*.py") if f.name != "data_subject_rights_service.py"]

    legacy_import_patterns = [
        "from app.services.data_subject_rights_service import",
        "from app.services import data_subject_rights_service",
        "import app.services.data_subject_rights_service",
    ]

    violations = []
    for service_file in service_files:
        content = service_file.read_text(encoding="utf-8")
        for pattern in legacy_import_patterns:
            if pattern in content:
                violations.append((str(service_file.relative_to(repo_root)), pattern))

    assert len(violations) == 0, (
        f"Found {len(violations)} v2 service(s) importing legacy DataSubjectRightsService:\n"
        + "\n".join(f"  - {file}: {pattern}" for file, pattern in violations)
    )


@pytest.mark.unit
def test_popia_service_is_authoritative():
    """Verify POPIADataRightsService exists and is the documented authoritative service."""
    repo_root = Path(__file__).resolve().parents[2]
    popia_service_path = repo_root / "app" / "services" / "popia_service.py"

    assert popia_service_path.exists(), "POPIADataRightsService file must exist"

    content = popia_service_path.read_text(encoding="utf-8")
    assert "class POPIADataRightsService" in content, "POPIADataRightsService class must exist"
    assert "execute_erasure" in content, "POPIADataRightsService must have execute_erasure method"


@pytest.mark.unit
def test_legacy_service_has_deprecation_notice():
    """Verify legacy DataSubjectRightsService has deprecation notice."""
    repo_root = Path(__file__).resolve().parents[2]
    legacy_service_path = repo_root / "app" / "services" / "data_subject_rights_service.py"

    assert legacy_service_path.exists(), "Legacy service file must exist"

    content = legacy_service_path.read_text(encoding="utf-8")
    assert "DEPRECATION NOTICE" in content, "Legacy service must have deprecation notice"
    assert "POPIADataRightsService" in content, "Legacy service must reference authoritative service"
    assert "LEGACY/COMPATIBILITY" in content, "Legacy service must be marked as legacy/compatibility"
