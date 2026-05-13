"""Compatibility shim exposing the canonical EduBoost V2 FastAPI app.

Tools and deployment scripts that still import app.api.main:app should get
exactly the same ASGI application as the production app.api_v2:app runtime.
"""
from __future__ import annotations

from app.api_v2 import app

__all__ = ["app"]
