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


def test_diagnostics_router_uses_domain_service_layer():
    source = DIAGNOSTICS.read_text(encoding="utf-8")

    assert "DiagnosticDomainService" in source
    assert "get_diagnostic_domain_service" in source
    assert "service: DiagnosticDomainService" in source

    # Router must not directly call repository boundary methods
    assert "diagnostic_repositories.learner(db)" not in source
    assert "diagnostic_repositories.item_bank(db)" not in source

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


def test_diagnostic_repository_boundary_owns_dynamic_resolution():
    source = BOUNDARY.read_text(encoding="utf-8")

    assert "from importlib import import_module" in source
    assert "app.repositories.repositories.LearnerRepository" in source
    assert "def learner(db:" in source
    assert "def item_bank(db:" in source
    assert "DiagnosticRepositoryBoundaryError" in source


def test_diagnostics_boundary_files_are_syntax_valid():
    for path in [DIAGNOSTICS, BOUNDARY, SERVICE]:
        ast.parse(path.read_text(encoding="utf-8"))
