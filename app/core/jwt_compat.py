"""PyJWT compatibility boundary for EduBoost JWT handling.

PRD-10.0-10.4 migrates runtime token handling away from ``python-jose``
and onto the already-supported PyJWT package. Application code imports
``jwt`` and ``JWTError`` from this module so future auth-library changes are
isolated to one boundary instead of leaking through FastAPI dependencies,
exception handlers, and token helpers.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jwt as _pyjwt

jwt = _pyjwt
JWTError = _pyjwt.PyJWTError


def decode_options(options: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return PyJWT decode options that preserve EduBoost's claim policy.

    EduBoost validates optional issuer/audience claims in ``AuthContext`` so
    the low-level keyring decode must not reject a token simply because an
    ``aud`` claim is present and no PyJWT ``audience`` argument was passed.
    Expiry and signature verification remain enabled by default.
    """

    merged: dict[str, Any] = {"verify_aud": False}
    if options:
        merged.update(dict(options))
    return merged


__all__ = ["JWTError", "decode_options", "jwt"]
