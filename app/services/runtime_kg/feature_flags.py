"""Feature flags for the runtime KG read/write path."""
from __future__ import annotations

import os
from dataclasses import dataclass

_TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


@dataclass(frozen=True)
class RuntimeKGFeatureFlags:
    """Runtime KG rollout flags.

    The default is intentionally disabled so PRD-2 can land without changing
    learner-facing behaviour. Operators can enable the graph-backed path with
    ``EDUBOOST_RUNTIME_KG_ENABLED=true`` after migrations and graph loading are
    proven in the target environment.
    """

    enabled: bool = False
    graph_version: str = "caps-grade4-math-runtime-v1"

    @classmethod
    def from_env(cls) -> "RuntimeKGFeatureFlags":
        return cls(
            enabled=os.getenv("EDUBOOST_RUNTIME_KG_ENABLED", "false").strip().lower() in _TRUE_VALUES,
            graph_version=os.getenv("EDUBOOST_RUNTIME_KG_VERSION", "caps-grade4-math-runtime-v1").strip()
            or "caps-grade4-math-runtime-v1",
        )
