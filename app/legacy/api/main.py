"""Archived legacy API entrypoint compatibility shim."""
from __future__ import annotations

from importlib import import_module

app = import_module("app.api_v2").app
