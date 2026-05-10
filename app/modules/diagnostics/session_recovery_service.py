from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DiagnosticSessionSnapshot:
    session_id: str
    learner_id: str
    caps_ref: str
    session_state: str = "initialising"
    theta: float = 0.0
    se_estimate: float = 1.0
    items_served: int = 0
    responses: list[dict[str, Any]] = field(default_factory=list)
    served_item_ids: list[str] = field(default_factory=list)
    gap_topics: list[str] = field(default_factory=list)
    misconception_tags: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class _MemoryRedis:
    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float]] = {}

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._data[key] = (value, time.time() + ttl)

    async def get(self, key: str) -> str | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            self._data.pop(key, None)
            return None
        return value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)


class SessionRecoveryService:
    """Redis-backed diagnostic session recovery with in-memory fallback."""

    def __init__(self, redis_client: Any = None, ttl_seconds: int = 7200) -> None:
        self.redis = redis_client or _MemoryRedis()
        self.ttl_seconds = ttl_seconds

    def _key(self, session_id: str) -> str:
        return f"diagnostic_session:{session_id}"

    async def write_session_snapshot(self, session_id: str, state: DiagnosticSessionSnapshot | dict[str, Any]) -> None:
        payload = asdict(state) if isinstance(state, DiagnosticSessionSnapshot) else dict(state)
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.redis.setex(self._key(session_id), self.ttl_seconds, json.dumps(payload, default=str))

    async def read_session_snapshot(self, session_id: str) -> DiagnosticSessionSnapshot | None:
        raw = await self.redis.get(self._key(session_id))
        if not raw:
            return None
        data = json.loads(raw)
        return DiagnosticSessionSnapshot(**data)

    async def invalidate_session_snapshot(self, session_id: str) -> None:
        await self.redis.delete(self._key(session_id))
