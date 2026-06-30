from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


AUTHZ_CLAIM_KEYS = (
    "sub",
    "user_id",
    "role",
    "roles",
    "guardian_learner_ids",
    "learner_id",
    "parent_id",
    "email_verified",
)


@dataclass(frozen=True)
class AuthTokenClaims:
    """Canonical authz-relevant access-token claims.

    The object is intentionally small and serializable. It avoids embedding raw
    email as an authorization primitive, while preserving optional identity
    metadata only when explicitly supplied.
    """

    sub: str
    user_id: str
    role: str | None = None
    roles: tuple[str, ...] = ()
    guardian_learner_ids: tuple[str, ...] = ()
    learner_id: str | None = None
    parent_id: str | None = None
    email_verified: bool | None = None
    extra: Mapping[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "sub": self.sub,
            "user_id": self.user_id,
        }
        if self.role is not None:
            payload["role"] = self.role
        if self.roles:
            payload["roles"] = list(self.roles)
        if self.guardian_learner_ids:
            payload["guardian_learner_ids"] = list(self.guardian_learner_ids)
        if self.learner_id is not None:
            payload["learner_id"] = self.learner_id
        if self.parent_id is not None:
            payload["parent_id"] = self.parent_id
        if self.email_verified is not None:
            payload["email_verified"] = self.email_verified
        if self.extra:
            for key, value in self.extra.items():
                if key not in payload and value is not None:
                    payload[key] = value
        return payload


def _as_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _read_value(source: Any, *keys: str) -> Any:
    if source is None:
        return None
    if isinstance(source, Mapping):
        for key in keys:
            if source.get(key) is not None:
                return source.get(key)
    for key in keys:
        if hasattr(source, key):
            value = getattr(source, key)
            if value is not None:
                return value
    return None


def _normalize_str_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if item is not None and str(item))
    return (str(value),)


def build_access_token_claims(
    user: Any,
    *,
    existing_claims: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build canonical access-token claims for register/login/refresh.

    `existing_claims` is used during refresh so authz-relevant claims such as
    guardian_learner_ids survive token rotation even when the User model does not
    carry the relationship eagerly.
    """
    existing_claims = existing_claims or {}
    extra = extra or {}

    user_id = _as_string(_read_value(user, "id", "user_id", "sub") or existing_claims.get("user_id") or existing_claims.get("sub"))
    if not user_id:
        raise ValueError("Cannot build access-token claims without stable user id")

    role = _as_string(_read_value(user, "role", "user_role") or existing_claims.get("role"))
    roles = _normalize_str_tuple(_read_value(user, "roles") or existing_claims.get("roles"))
    guardian_learner_ids = _normalize_str_tuple(
        _read_value(user, "guardian_learner_ids", "authorized_learner_ids", "learner_ids")
        or existing_claims.get("guardian_learner_ids")
        or existing_claims.get("authorized_learner_ids")
    )

    claims = AuthTokenClaims(
        sub=user_id,
        user_id=user_id,
        role=role,
        roles=roles,
        guardian_learner_ids=guardian_learner_ids,
        learner_id=_as_string(_read_value(user, "learner_id") or existing_claims.get("learner_id")),
        parent_id=_as_string(_read_value(user, "parent_id", "guardian_id") or existing_claims.get("parent_id")),
        email_verified=_read_value(user, "email_verified") if _read_value(user, "email_verified") is not None else existing_claims.get("email_verified"),
        extra={key: value for key, value in extra.items() if key not in {"email", "email_encrypted"}},
    )
    return claims.to_payload()


def merge_refresh_claims(existing_claims: Mapping[str, Any], user: Any) -> dict[str, Any]:
    """Build refreshed access-token claims while preserving authorization scope."""
    return build_access_token_claims(user, existing_claims=existing_claims)


def contains_raw_email_encrypted_assignment(text: str) -> bool:
    """Return True when source text contains obvious raw email_encrypted writes."""
    suspicious = (
        "email_encrypted=email",
        "email_encrypted = email",
        "email_encrypted=user.email",
        "email_encrypted = user.email",
        "email_encrypted=request.email",
        "email_encrypted = request.email",
        "email_encrypted=body.email",
        "email_encrypted = body.email",
    )
    return any(item in text for item in suspicious)


__all__ = [
    "AUTHZ_CLAIM_KEYS",
    "AuthTokenClaims",
    "build_access_token_claims",
    "contains_raw_email_encrypted_assignment",
    "merge_refresh_claims",
]
