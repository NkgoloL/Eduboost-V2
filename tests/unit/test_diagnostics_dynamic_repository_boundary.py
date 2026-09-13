from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS = ROOT / "app/api_v2_routers/diagnostics.py"
BOUNDARY = ROOT / "app/api_v2_deps/diagnostic_repositories.py"
SERVICE = ROOT / "app/services/diagnostic_domain_service.py"


def test_diagnostics_router_does_not_use_dynamic_repository_resolution():
    source = DIAGNOSTICS.read_text(encoding="utf-8")

    assert "importlib.import_module" not in source
    assert "from app.repositories" not in source
    assert "app.repositories." not in source


def test_diagnostics_router_calls_domain_service_not_repositories():
    source = DIAGNOSTICS.read_text(encoding="utf-8")

    assert "from app.services.diagnostic_domain_service import" in source
    assert "DiagnosticDomainService" in source
    assert "get_diagnostic_domain_service" in source

    for token in [
        "LearnerRepository(db)",
        "GuardianRepository(db)",
        "IRTRepository(db)",
        "DiagnosticRepository(db)",
        "KnowledgeGapRepository(db)",
        "ItemBankRepository(db)",
        "DiagnosticSessionRepository(db)",
        "MasteryRepository(db)",
        "_LearnerRepo(db)",
        "_ItemBankRepo(db)",
    ]:
        assert token not in source


def test_dynamic_repository_boundary_shim_is_eliminated():
    assert not BOUNDARY.exists(), "Dynamic reflection boundary app/api_v2_deps/diagnostic_repositories.py must be deleted."


def test_diagnostics_domain_service_syntax_valid():
    for path in [DIAGNOSTICS, SERVICE]:
        ast.parse(path.read_text(encoding="utf-8"))
