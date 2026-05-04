"""Redis-backed background job tracking for V2 async operations."""
from __future__ import annotations

import json
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from fastapi import BackgroundTasks

from app.core.logging import get_logger
from app.core.redis import get_redis

log = get_logger(__name__)
JOB_TTL_SECONDS = 24 * 60 * 60
_MEMORY_JOBS: dict[str, dict[str, Any]] = {}


def _job_key(job_id: str) -> str:
    return f"jobs:{job_id}"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (datetime, uuid.UUID)):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="json"))
    return value


async def _write_job(job: dict[str, Any]) -> None:
    payload = json.dumps(_jsonable(job))
    _MEMORY_JOBS[job["job_id"]] = json.loads(payload)
    try:
        await get_redis().set(_job_key(job["job_id"]), payload, ex=JOB_TTL_SECONDS)
    except Exception as exc:  # noqa: BLE001
        log.warning("job_store_redis_write_failed", error=str(exc), job_id=job["job_id"])


async def _read_job(job_id: str) -> dict[str, Any] | None:
    try:
        payload = await get_redis().get(_job_key(job_id))
        if payload:
            return json.loads(payload)
    except Exception as exc:  # noqa: BLE001
        log.warning("job_store_redis_read_failed", error=str(exc), job_id=job_id)
    return _MEMORY_JOBS.get(job_id)


async def create_job(operation: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    job = {
        "job_id": str(uuid.uuid4()),
        "operation": operation,
        "status": "queued",
        "payload": _jsonable(payload or {}),
        "result": None,
        "error": None,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    await _write_job(job)
    return job


async def update_job(
    job_id: str,
    *,
    status: str | None = None,
    result: Any | None = None,
    error: Any | None = None,
) -> dict[str, Any] | None:
    job = await _read_job(job_id)
    if job is None:
        return None
    if status is not None:
        job["status"] = status
    if result is not None:
        job["result"] = _jsonable(result)
    if error is not None:
        job["error"] = _jsonable(error)
    job["updated_at"] = _now_iso()
    await _write_job(job)
    return job


async def get_job(job_id: str) -> dict[str, Any] | None:
    return await _read_job(job_id)


async def enqueue_job(
    background_tasks: BackgroundTasks,
    *,
    operation: str,
    handler: Callable[[], Awaitable[Any]],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    job = await create_job(operation, payload=payload)
    background_tasks.add_task(run_job, job["job_id"], handler)
    return job


async def run_job(job_id: str, handler: Callable[[], Awaitable[Any]]) -> None:
    await update_job(job_id, status="running")
    try:
        result = await handler()
    except Exception as exc:  # noqa: BLE001
        log.exception("background_job_failed", job_id=job_id)
        await update_job(
            job_id,
            status="failed",
            error={"type": exc.__class__.__name__, "message": str(exc)},
        )
        return
    await update_job(job_id, status="completed", result=result)
