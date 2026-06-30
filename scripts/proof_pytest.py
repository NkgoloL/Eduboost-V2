from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PytestProofResult:
    returncode: int
    output: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warnings: int = 0

    @property
    def ok_without_skips(self) -> bool:
        return self.returncode == 0 and self.skipped == 0


_SUMMARY_PATTERNS = {
    "passed": r"(\d+)\s+passed",
    "failed": r"(\d+)\s+failed",
    "skipped": r"(\d+)\s+skipped",
    "warnings": r"(\d+)\s+warnings?",
}


def _last_count(output: str, pattern: str) -> int:
    matches = re.findall(pattern, output)
    return int(matches[-1]) if matches else 0


def parse_pytest_proof(output: str, returncode: int = 0) -> PytestProofResult:
    return PytestProofResult(
        returncode=returncode,
        output=output,
        passed=_last_count(output, _SUMMARY_PATTERNS["passed"]),
        failed=_last_count(output, _SUMMARY_PATTERNS["failed"]),
        skipped=_last_count(output, _SUMMARY_PATTERNS["skipped"]),
        warnings=_last_count(output, _SUMMARY_PATTERNS["warnings"]),
    )


def run_pytest_proof(
    args: Iterable[str],
    *,
    root: Path,
    require_no_skips: bool = True,
    extra_env: dict[str, str] | None = None,
) -> PytestProofResult:
    env = {**os.environ, "PYTHONPATH": str(root)}
    if extra_env:
        env.update(extra_env)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )
    proof = parse_pytest_proof(result.stdout, result.returncode)
    print(proof.output)

    if proof.returncode != 0:
        raise RuntimeError(f"pytest proof command failed with exit code {proof.returncode}")
    if require_no_skips and proof.skipped > 0:
        raise RuntimeError(
            f"pytest proof command reported {proof.skipped} skipped test(s); skipped tests are not-proven"
        )
    return proof


__all__ = ["PytestProofResult", "parse_pytest_proof", "run_pytest_proof"]
