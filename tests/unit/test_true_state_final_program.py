"""Unit tests for True-State Remediation Whole-Program Verification and Bundle B07."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.true_state_remediation.core import (
    FALSE_BOUNDARY_KEYS,
    load_json,
    root_from,
    verify_false_release_boundaries,
    verify_previous_bundle,
    verify_register,
)
from scripts.true_state_remediation.verify_final_program import (
    verify_bundle_chain,
    verify_engineering_proofs,
)


@pytest.fixture
def repo_root() -> Path:
    return root_from()


def test_previous_bundle_b06_is_verified(repo_root: Path):
    res = verify_previous_bundle(repo_root, "B07")
    assert res["valid"] is True, f"B06 must be verified before B07 can execute: {res}"


def test_engineering_proof_artifacts_presence(repo_root: Path):
    res = verify_engineering_proofs(repo_root)
    assert res["valid"] is True, f"Missing engineering proof artifacts: {res.get('missing')}"
    assert res["verified_count"] == res["total_required"]


def test_fail_closed_release_boundaries(repo_root: Path):
    res = verify_false_release_boundaries(repo_root)
    assert res["valid"] is True, f"False release boundaries violated: {res.get('failures')}"


def test_remediation_register_structure(repo_root: Path):
    res = verify_register(repo_root)
    assert res["valid"] is True, f"Remediation register invalid: {res.get('errors')}"
    assert res["task_count"] == 174


def test_release_statement_exists_and_binds_commit(repo_root: Path):
    statement = repo_root / "docs/releases/true_state_release_statement.md"
    assert statement.exists()
    content = statement.read_text(encoding="utf-8")
    assert "EduBoost V2: True-State Remediation Authoritative Release Statement" in content
    assert "Fail-Closed" in content or "FAIL_CLOSED" in content
    assert "v2.0.0-tsr.final" in content
