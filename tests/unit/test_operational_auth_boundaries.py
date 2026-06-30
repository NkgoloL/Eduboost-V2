from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_learner_authz_matrix import collect_rows
from scripts.check_learner_authz_coverage import ALLOWLIST


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_operational_auth_boundary_matrix_statuses() -> None:
    rows = collect_rows()
    lookup = {(row.router, row.method, row.path): row for row in rows}

    consent = lookup[("consent_renewal.py", "POST", "/trigger-renewal-reminders")]
    ether = lookup[("ether.py", "GET", "/onboarding/questions")]
    dev_session = lookup[("auth.py", "POST", "/dev-session")]

    assert consent.status == "covered"
    assert consent.authz_marker == "require_admin"
    assert ether.status == "covered"
    assert ether.authz_marker == "require_auth_context"
    assert dev_session.status == "missing"
    assert ("auth.py", "POST", "/dev-session") in ALLOWLIST


@pytest.mark.unit
def test_operational_auth_boundary_source_contracts() -> None:
    auth = (REPO_ROOT / "app" / "api_v2_routers" / "auth.py").read_text(encoding="utf-8")
    consent = (REPO_ROOT / "app" / "api_v2_routers" / "consent_renewal.py").read_text(encoding="utf-8")
    ether = (REPO_ROOT / "app" / "api_v2_routers" / "ether.py").read_text(encoding="utf-8")

    assert "settings.is_production()" in auth
    assert "status.HTTP_404_NOT_FOUND" in auth
    assert "Depends(require_admin)" in consent
    assert "async def get_questions(user: AuthContext = Depends(require_auth_context))" in ether
