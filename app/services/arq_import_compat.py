from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

try:  # pragma: no cover - depends on optional installed package in local env
    from arq import cron as cron  # type: ignore
    from arq.connections import RedisSettings as RedisSettings  # type: ignore

    ARQ_AVAILABLE = True
    ARQ_IMPORT_ERROR = ""
except Exception as exc:  # pragma: no cover - exercised when arq missing
    ARQ_AVAILABLE = False
    ARQ_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"

    @dataclass
    class RedisSettings:  # type: ignore[no-redef]
        host: str = "localhost"
        port: int = 6379
        database: int = 0
        password: str | None = None

    def cron(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Callable[..., Any]:  # type: ignore[no-redef]
        # Import-safe fallback. Real worker execution still requires arq to be
        # installed; dependency files are patched by this batch.
        setattr(function, "_arq_cron_fallback", {"args": args, "kwargs": kwargs})
        return function


def arq_dependency_status() -> dict[str, Any]:
    return {
        "available": ARQ_AVAILABLE,
        "import_error": ARQ_IMPORT_ERROR,
    }


__all__ = ["ARQ_AVAILABLE", "ARQ_IMPORT_ERROR", "RedisSettings", "arq_dependency_status", "cron"]
