from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.services.auth_token_claims import (
    build_access_token_claims,
    contains_raw_email_encrypted_assignment,
    merge_refresh_claims,
)


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class User:
    id: str
    role: str = "guardian"


def _auth_router_source() -> str:
    candidates = [
        ROOT / "app/api_v2_routers/auth.py",
        ROOT / "app/api/v2/auth.py",
        ROOT / "app/routes/auth.py",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise AssertionError("Auth router not found")


def test_build_access_token_claims_preserves_guardian_scope_from_user():
    user = {"id": "guardian-1", "role": "guardian", "guardian_learner_ids": ["learner-1", "learner-2"]}
    claims = build_access_token_claims(user)
    assert claims["sub"] == "guardian-1"
    assert claims["user_id"] == "guardian-1"
    assert claims["role"] == "guardian"
    assert claims["guardian_learner_ids"] == ["learner-1", "learner-2"]


def test_merge_refresh_claims_preserves_guardian_learner_ids_when_model_is_sparse():
    existing = {"sub": "guardian-1", "role": "guardian", "guardian_learner_ids": ["learner-9"]}
    claims = merge_refresh_claims(existing, User(id="guardian-1"))
    assert claims["sub"] == "guardian-1"
    assert claims["guardian_learner_ids"] == ["learner-9"]


def test_build_access_token_claims_does_not_emit_raw_email_claim_by_default():
    user = {"id": "user-1", "email": "learner@example.com", "role": "learner"}
    claims = build_access_token_claims(user)
    assert "email" not in claims
    assert "email_encrypted" not in claims


def test_auth_router_imports_canonical_claim_helper():
    source = _auth_router_source()
    assert "app.services.auth_token_claims" in source
    assert "# code_631_650_auth_token_claims_repair" in source


def test_auth_router_has_no_obvious_raw_email_encrypted_assignment():
    assert contains_raw_email_encrypted_assignment(_auth_router_source()) is False
