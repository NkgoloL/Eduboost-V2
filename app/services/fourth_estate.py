"""Compatibility shim for the canonical Fourth Estate audit service.

Phase 16C-1 keeps legacy imports working while the runtime-readiness
diagnostic stack is exercised. The implementation remains owned by
``app.core.audit``; this module is only a stable import boundary.
"""
from __future__ import annotations

from app.core.audit import FourthEstateService

__all__ = ["FourthEstateService"]
