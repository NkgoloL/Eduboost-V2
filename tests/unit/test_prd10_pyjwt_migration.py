from __future__ import annotations

import json

import pytest

from app.core.jwt_compat import JWTError, jwt
from app.services.jwt_keyring import decode_jwt_with_keyring, encode_jwt_with_keyring


def test_pyjwt_keyring_roundtrip_and_tamper_rejection(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("JWT_KEYRING", json.dumps([
        {"kid": "current", "secret": "test-current-secret-32-characters", "algorithm": "HS256", "status": "current"},
        {"kid": "previous", "secret": "test-previous-secret-32-characters", "algorithm": "HS256", "status": "previous"},
    ]))

    token = encode_jwt_with_keyring({"sub": "learner-1", "type": "access", "aud": "eduboost-test"})
    assert jwt.get_unverified_header(token)["kid"] == "current"
    decoded = decode_jwt_with_keyring(token)
    assert decoded["sub"] == "learner-1"
    assert decoded["aud"] == "eduboost-test"

    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(JWTError):
        decode_jwt_with_keyring(tampered)


def test_previous_kid_still_decodes_during_rotation(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("JWT_KEYRING", json.dumps([
        {"kid": "current", "secret": "test-current-secret-32-characters", "algorithm": "HS256", "status": "current"},
        {"kid": "previous", "secret": "test-previous-secret-32-characters", "algorithm": "HS256", "status": "previous"},
    ]))
    previous = jwt.encode({"sub": "learner-previous", "type": "access"}, "test-previous-secret-32-characters", algorithm="HS256", headers={"kid": "previous"})

    decoded = decode_jwt_with_keyring(previous)
    assert decoded["sub"] == "learner-previous"


def test_python_jose_removed_from_runtime_requirements():
    files = [
        "requirements/base.in",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/constraints.snapshot.txt",
    ]
    for path in files:
        text = open(path, encoding="utf-8").read().lower()
        assert "python-jose" not in text
    assert "pyjwt[crypto]==2.12.1" in open("requirements/base.in", encoding="utf-8").read().lower()
