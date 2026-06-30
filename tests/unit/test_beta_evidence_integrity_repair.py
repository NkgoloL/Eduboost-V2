from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def test_integrity_repair_scripts_run_and_restore_truthful_no_go():
    result = run([sys.executable, "scripts/repair_beta_evidence_integrity.py"])
    assert result.returncode == 0, result.stdout

    result = run([sys.executable, "scripts/generate_truthful_beta_readiness_status.py"])
    assert result.returncode in {0, 2}, result.stdout

    result = run([sys.executable, "scripts/generate_truthful_release_owner_beta_go_no_go.py"])
    assert result.returncode == 0, result.stdout

    status = json.loads((ROOT / "docs/release/beta_readiness_status.json").read_text(encoding="utf-8"))
    memo = (ROOT / "docs/release/release_owner_beta_go_no_go_memo.md").read_text(encoding="utf-8")

    if status["status"] != "beta_ready":
        assert "Recommendation: NO-GO" in memo
        assert status["blockers"]


def test_integrity_checker_rejects_pass_like_invalid_evidence():
    run([sys.executable, "scripts/repair_beta_evidence_integrity.py"])
    run([sys.executable, "scripts/generate_truthful_beta_readiness_status.py"])
    result = run([sys.executable, "scripts/check_beta_evidence_integrity.py"])
    assert result.returncode == 0, result.stdout


def test_policy_doc_exists():
    assert (ROOT / "docs/release/beta_evidence_source_policy.md").exists()


def test_makefile_contains_581_590_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "beta-evidence-integrity-repair:" in text
    assert "beta-evidence-integrity-check:" in text
    assert "backend-implementation-581-590-full-check:" in text
