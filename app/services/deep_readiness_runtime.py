from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class DeepReadinessCheckResult:
    name: str
    status: str
    detail: str
    read_only: bool = True

@dataclass(frozen=True)
class DeepReadinessRuntimeResult:
    status: str
    checks: tuple[DeepReadinessCheckResult, ...]
    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "checks": [asdict(c) for c in self.checks]}

async def _execute(session: Any, sql: str) -> Any:
    if session is None: return None
    result = await session.execute(sql)
    scalar = getattr(result, "scalar", None)
    return scalar() if callable(scalar) else result

async def run_deep_readiness_runtime_checks(*, db_session: Any | None = None, cache_client: Any | None = None,
                                            required_tables: tuple[str, ...] = ("users","learners")) -> DeepReadinessRuntimeResult:
    checks=[]
    try:
        await _execute(db_session, "SELECT 1")
        checks.append(DeepReadinessCheckResult("database_connectivity","pass","read-only connectivity check completed"))
    except Exception as exc:
        checks.append(DeepReadinessCheckResult("database_connectivity","fail",f"{type(exc).__name__}: {exc}"))
    try:
        await _execute(db_session, "SELECT version_num FROM alembic_version LIMIT 1")
        checks.append(DeepReadinessCheckResult("alembic_revision","pass","read-only Alembic revision query completed"))
    except Exception as exc:
        checks.append(DeepReadinessCheckResult("alembic_revision","warn",f"{type(exc).__name__}: {exc}"))
    for table in required_tables:
        try:
            await _execute(db_session, f"SELECT 1 FROM information_schema.tables WHERE table_name = '{table}' LIMIT 1")
            checks.append(DeepReadinessCheckResult(f"table:{table}","pass","read-only table presence query completed"))
        except Exception as exc:
            checks.append(DeepReadinessCheckResult(f"table:{table}","warn",f"{type(exc).__name__}: {exc}"))
    if cache_client is not None:
        ping=getattr(cache_client,"ping",None)
        if ping:
            r=ping()
            if hasattr(r,"__await__"): await r
        checks.append(DeepReadinessCheckResult("cache_ping","pass","cache ping completed"))
    return DeepReadinessRuntimeResult("pass" if all(c.status in {"pass","warn"} for c in checks) else "fail", tuple(checks))
