from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

from scripts.popia_response_contract_no_skips import (
    adapter_contracts,
    build_status,
    route_contracts,
    write_status,
)

ROOT = Path(__file__).resolve().parents[2]


def test_popia_lifecycle_routes_return_consent_record_contracts():
    contracts = route_contracts()
    assert len(contracts) == 4
    for contract in contracts:
        assert contract.exists, contract
        assert contract.response_model_is_consent_record, contract
        assert contract.passed, contract


def test_popia_lifecycle_adapter_coerces_consent_records():
    contracts = adapter_contracts()
    assert contracts["adapter_exists"]
    assert contracts["contains_consent_record"]
    assert contracts["contains_coerce_consent_record"]
    assert contracts["contains_denied_fallback"]
    assert contracts["contains_withdrawn_fallback"]


def test_popia_no_skip_proof_file_has_no_skip_calls_or_markers():
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    def dotted_name(node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = dotted_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        if isinstance(node, ast.Call):
            return dotted_name(node.func)
        return ""

    forbidden_call_names = {
        ("pytest", "skip"),
        ("skip",),
    }
    forbidden_marker_names = {
        ("pytest", "mark", "skip"),
        ("pytest", "mark", "skipif"),
        ("mark", "skip"),
        ("mark", "skipif"),
    }

    def name_parts(node):
        return tuple(part for part in dotted_name(node).split(".") if part)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            assert name_parts(node.func) not in forbidden_call_names

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                assert name_parts(decorator) not in forbidden_marker_names


def test_popia_no_skip_status_static_contracts_pass_without_pytest():
    status = build_status(run_tests=False)
    assert status.status == "popia-response-contract-no-skip-passing"
    assert status.pytest_return_code is None
    assert not status.skipped_detected
    assert status.blockers == []


def test_popia_no_skip_status_writes_reports_without_pytest():
    status = write_status(run_tests=False)
    assert (ROOT / "docs/release/popia_response_contract_no_skip_status.json").exists()
    assert (ROOT / "docs/release/popia_response_contract_no_skip_status.md").exists()
    assert status.status == "popia-response-contract-no-skip-passing"


def test_popia_no_skip_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_response_contract_no_skips.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_popia_no_skip_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "popia-response-contract-no-skip-status:" in source
    assert "popia-response-contract-no-skip-check:" in source
    assert "backend-implementation-2831-2870-full-check:" in source
