from __future__ import annotations

import pytest

from app.core.password_policy import validate_password_strength
from app.core.security import hash_password, verify_password


def test_password_policy_accepts_complex_password() -> None:
    assert validate_password_strength("Correct-Horse7") == "Correct-Horse7"


def test_password_policy_accepts_long_passphrase() -> None:
    assert validate_password_strength("three clean river stones") == "three clean river stones"


@pytest.mark.parametrize("password", ["weak123", "short", "NoSymbol123", "nosymbol123!"])
def test_password_policy_rejects_weak_passwords(password: str) -> None:
    with pytest.raises(ValueError):
        validate_password_strength(password)


def test_bcrypt_hash_uses_configured_cost_and_verifies() -> None:
    hashed = hash_password("Correct-Horse7")
    assert hashed.startswith("$2b$12$")
    assert verify_password("Correct-Horse7", hashed) is True
    assert verify_password("wrong", hashed) is False
