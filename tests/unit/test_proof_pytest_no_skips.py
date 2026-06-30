from __future__ import annotations

import pytest

from scripts.proof_pytest import parse_pytest_proof


def test_parse_pytest_proof_detects_skips():
    proof = parse_pytest_proof("3 passed, 2 skipped in 0.12s", 0)

    assert proof.returncode == 0
    assert proof.passed == 3
    assert proof.skipped == 2
    assert proof.ok_without_skips is False


def test_parse_pytest_proof_accepts_no_skips():
    proof = parse_pytest_proof("8 passed in 0.12s", 0)

    assert proof.passed == 8
    assert proof.skipped == 0
    assert proof.ok_without_skips is True


@pytest.mark.parametrize("output", ["1 failed, 1 skipped", "5 skipped"])
def test_parse_pytest_proof_never_treats_skipped_as_strong_proof(output):
    proof = parse_pytest_proof(output, 0)

    assert proof.ok_without_skips is False
