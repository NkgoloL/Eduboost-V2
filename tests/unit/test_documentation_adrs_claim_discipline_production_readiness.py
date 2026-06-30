from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.documentation_governance.production_readiness_contracts import (
    DEFAULT_ADRS,
    DEFAULT_CLAIM_RULES,
    DEFAULT_CLAIMS,
    DEFAULT_DOCUMENTATION_DECISION,
    DEFAULT_DOC_INVENTORY,
    DEFAULT_RELEASE_NOTES,
    DEFAULT_REVIEW_GATE,
    DEFAULT_STALE_FINDINGS,
    _SAMPLE_DATE,
    compute_documentation_checksum,
    contains_unbounded_production_claim,
    normalize_doc_title,
    validate_claims_for_release,
)
from scripts.check_documentation_adrs_claim_discipline_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_documentation_adrs_claim_discipline_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_documentation_adrs_claim_discipline_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_documentation_adrs_claim_discipline_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Documentation ADRs claim discipline production readiness check" in result.stdout


@pytest.mark.unit
def test_documentation_governance_contracts_validate() -> None:
    assert DEFAULT_DOCUMENTATION_DECISION.validate() == []
    assert [issue for entry in DEFAULT_DOC_INVENTORY for issue in entry.validate(_SAMPLE_DATE)] == []
    assert [issue for adr in DEFAULT_ADRS for issue in adr.validate()] == []
    assert validate_claims_for_release(DEFAULT_CLAIMS) == []
    assert [issue for rule in DEFAULT_CLAIM_RULES for issue in rule.validate()] == []
    assert [issue for note in DEFAULT_RELEASE_NOTES for issue in note.validate()] == []
    assert [issue for finding in DEFAULT_STALE_FINDINGS for issue in finding.validate()] == []
    assert DEFAULT_REVIEW_GATE.validate() == []


@pytest.mark.unit
def test_unbounded_production_claim_detection() -> None:
    assert contains_unbounded_production_claim("The platform is production ready.")
    assert not contains_unbounded_production_claim("Repository-side production readiness evidence is present; this does not authorize production launch.")


@pytest.mark.unit
def test_documentation_title_normalization() -> None:
    assert normalize_doc_title("Documentation, ADRs, and Claim Discipline") == "documentation-adrs-and-claim-discipline"


@pytest.mark.unit
def test_documentation_checksum_is_sha256_hex() -> None:
    checksum = compute_documentation_checksum("documentation-governance-evidence")
    assert len(checksum) == 64
    assert checksum == compute_documentation_checksum("documentation-governance-evidence")
    assert checksum != compute_documentation_checksum("other-documentation-evidence")


@pytest.mark.unit
def test_makefile_exposes_documentation_adrs_claim_discipline_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "documentation-adrs-claim-discipline-production-readiness-check:" in text
    assert "scripts/check_documentation_adrs_claim_discipline_production_readiness.py" in text
