from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from app.services.jwt_keyring import current_jwt_key, decode_jwt_with_keyring, encode_jwt_with_keyring, parse_jwt_keyring

ROOT = Path(__file__).resolve().parents[2]


def test_jwt_keyring_parses_json_and_semicolon_formats():
    raw_json = json.dumps([
        {"kid": "new", "secret": "s1", "algorithm": "HS256", "status": "current"},
        {"kid": "old", "secret": "s0", "algorithm": "HS256", "status": "previous"},
    ])
    assert current_jwt_key(parse_jwt_keyring(raw_json)).kid == "new"
    raw_semicolon = "new:s1:HS256:current;old:s0:HS256:previous"
    assert current_jwt_key(parse_jwt_keyring(raw_semicolon)).secret == "s1"


def test_jwt_keyring_encode_decode_round_trip(monkeypatch):
    monkeypatch.setenv(
        "JWT_KEYRING",
        '[{"kid":"new","secret":"secret-new","algorithm":"HS256","status":"current"},{"kid":"old","secret":"secret-old","algorithm":"HS256","status":"previous"}]',
    )
    token = encode_jwt_with_keyring({"sub": "user-1"})
    decoded = decode_jwt_with_keyring(token)
    assert decoded["sub"] == "user-1"


def test_security_scripts_run():
    for command in [
        [sys.executable, "scripts/inspect_jwt_rotation.py"],
        [sys.executable, "scripts/repair_jwt_rotation.py"],
        [sys.executable, "scripts/check_jwt_rotation.py"],
        [sys.executable, "scripts/generate_dependency_pin_report.py"],
        [sys.executable, "scripts/generate_auth_extraction_followup.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode in {0, 2}, result.stdout


def test_makefile_contains_security_hardening_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "jwt-rotation-inspect:" in text
    assert "dependency-pin-report:" in text
    assert "backend-implementation-751-780-full-check:" in text
