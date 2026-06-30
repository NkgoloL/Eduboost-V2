from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_learner_authz_matrix import collect_rows


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "consent_renewal.py"


@pytest.mark.unit
def test_consent_renewal_route_requires_admin_dependency() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def trigger_renewal_reminders", maxsplit=1)[1]

    assert "Depends(require_admin)" in block
    assert "Admin only" in source


@pytest.mark.unit
def test_matrix_recognizes_require_admin_marker_for_consent_renewal() -> None:
    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "consent_renewal.py"
        and row.method == "POST"
        and row.path == "/trigger-renewal-reminders"
    ]

    assert matches
    assert matches[0].authz_marker == "require_admin"
    assert matches[0].status == "covered"
