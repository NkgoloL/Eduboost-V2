"""Compatibility shim for legacy LLM gateway imports.

The canonical ExecutiveService and provider-label resolver live in
``app.core.llm``. Some runtime paths still import the historical
``app.core.llm_gateway`` module name, so Phase 16C-1 restores that
import boundary without changing provider behaviour.
"""
from __future__ import annotations

from app.core.llm import ExecutiveService, active_provider_label

__all__ = ["ExecutiveService", "active_provider_label"]
