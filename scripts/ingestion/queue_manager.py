"""
EduBoost SA — Redis Queue Manager
====================================
Manages ingestion job lifecycle using Redis:

  • LPUSH / BRPOP for FIFO job queue
  • Hash-based progress snapshots (live updates)
  • Job cancellation via a cancelled-set
  • Optional job TTL for automatic cleanup

Architecture
------------
  ┌───────────────┐   enqueue()    ┌──────────────────┐
  │  API / CLI    │ ─────────────► │  Redis List       │
  │  (producer)   │                │  ingestion:queue  │
  └───────────────┘                └─────────┬────────┘
                                             │ BRPOP (worker picks up)
  ┌───────────────┐   update_progress()      ▼
  │  Worker task  │ ─────────────► ┌──────────────────┐
  │  (consumer)   │                │  Redis Hash       │
  └───────────────┘                │  ingestion:prog:* │
                                   └──────────────────┘

Usage::

    qm = QueueManager("redis://localhost:6379")
    await qm.connect()

    job_id = await qm.enqueue(job)
    job    = await qm.dequeue(timeout=5)   # blocks up to 5 s
    await qm.update_progress(progress)
    snap   = await qm.get_progress(job_id)

    await qm.disconnect()
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from scripts.ingestion.config import REDIS_PROGRESS_KEY, REDIS_QUEUE_KEY
from scripts.ingestion.models import IngestionJob, IngestionProgress, JobStatus
import contextlib

logger = logging.getLogger(__name__)

_CANCELLED_SET = "ingestion:cancelled"
_JOB_HASH_PREFIX = "ingestion:job:"
_PROGRESS_TTL_SECS = 86_400   # keep progress for 24 h after completion


class QueueManager:
    """
    Async Redis-backed job queue.

    Parameters
    ----------
    redis_url:
        Full Redis URL, e.g. ``redis://localhost:6379/0``.
    queue_key:
        Redis list key used as the FIFO queue.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        queue_key: str = REDIS_QUEUE_KEY,
    ) -> None:
        self._url       = redis_url
        self._queue_key = queue_key
        self._redis: Any = None   # redis.asyncio.Redis

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Open the Redis connection pool."""
        try:
            import redis.asyncio as aioredis  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "redis package not installed — run: pip install redis[asyncio]"
            ) from exc

        self._redis = aioredis.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("[QueueManager] Connected to Redis at %s", self._url)

    async def disconnect(self) -> None:
        """Close the Redis connection pool."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
        logger.info("[QueueManager] Disconnected from Redis")

    async def __aenter__(self) -> "QueueManager":
        await self.connect()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.disconnect()

    # ── Job Queue Operations ──────────────────────────────────────────────────

    async def enqueue(self, job: IngestionJob) -> str:
        """
        Push *job* onto the tail of the queue.

        Returns the job ID.  The job is also stored in a Redis Hash
        so it can be inspected without dequeuing.
        """
        self._check_connected()

        payload = job.model_dump_json()
        pipe = self._redis.pipeline()
        pipe.rpush(self._queue_key, payload)
        pipe.hset(
            f"{_JOB_HASH_PREFIX}{job.id}",
            mapping={
                "payload": payload,
                "status":  JobStatus.PENDING.value,
                "queued_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        await pipe.execute()

        logger.info("[QueueManager] Enqueued job %s (source=%s)", job.id, job.source_id)
        return job.id

    async def dequeue(self, timeout: float = 0) -> IngestionJob | None:
        """
        Pop the oldest job from the head of the queue.

        Parameters
        ----------
        timeout:
            Seconds to block waiting for a job (0 = non-blocking).
        """
        self._check_connected()

        result = await self._redis.blpop(self._queue_key, timeout=int(timeout))
        if not result:
            return None

        _, payload = result
        job = IngestionJob.model_validate_json(payload)

        # Mark as running in job hash
        await self._redis.hset(
            f"{_JOB_HASH_PREFIX}{job.id}",
            mapping={
                "status":     JobStatus.RUNNING.value,
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        logger.info("[QueueManager] Dequeued job %s", job.id)
        return job

    async def complete_job(
        self,
        job_id: str,
        status: JobStatus = JobStatus.COMPLETED,
        stats: dict[str, Any] | None = None,
    ) -> None:
        """Mark a job as completed (or failed) in the hash store."""
        self._check_connected()

        mapping: dict[str, str] = {
            "status":       status.value,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        if stats:
            mapping["stats"] = json.dumps(stats)

        pipe = self._redis.pipeline()
        pipe.hset(f"{_JOB_HASH_PREFIX}{job_id}", mapping=mapping)
        pipe.expire(f"{_JOB_HASH_PREFIX}{job_id}", _PROGRESS_TTL_SECS)
        await pipe.execute()

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Fetch the stored job metadata dict."""
        self._check_connected()
        data = await self._redis.hgetall(f"{_JOB_HASH_PREFIX}{job_id}")
        return data if data else None

    # ── Progress ──────────────────────────────────────────────────────────────

    async def update_progress(self, progress: IngestionProgress) -> None:
        """
        Write a progress snapshot to Redis.

        The key expires automatically after ``_PROGRESS_TTL_SECS``.
        """
        self._check_connected()
        key = REDIS_PROGRESS_KEY.format(job_id=progress.job_id)
        pipe = self._redis.pipeline()
        pipe.hset(
            key,
            mapping={
                "source_id": progress.source_id,
                "status":    progress.status.value,
                "pct":       str(progress.pct),
                "scraped":   str(progress.scraped),
                "processed": str(progress.processed),
                "failed":    str(progress.failed),
                "message":   progress.message,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                **({"eta_secs": str(progress.eta_secs)} if progress.eta_secs else {}),
            },
        )
        pipe.expire(key, _PROGRESS_TTL_SECS)
        await pipe.execute()

    async def get_progress(self, job_id: str) -> IngestionProgress | None:
        """Fetch the latest progress snapshot for *job_id*."""
        self._check_connected()
        key = REDIS_PROGRESS_KEY.format(job_id=job_id)
        data = await self._redis.hgetall(key)
        if not data:
            return None

        try:
            return IngestionProgress(
                job_id=job_id,
                source_id=data.get("source_id", ""),
                status=JobStatus(data.get("status", "pending")),
                pct=float(data.get("pct", 0.0)),
                scraped=int(data.get("scraped", 0)),
                processed=int(data.get("processed", 0)),
                failed=int(data.get("failed", 0)),
                message=data.get("message", ""),
                eta_secs=int(data["eta_secs"]) if "eta_secs" in data else None,
            )
        except (KeyError, ValueError) as exc:
            logger.warning("[QueueManager] Corrupt progress data for %s: %s", job_id, exc)
            return None

    # ── Cancellation ─────────────────────────────────────────────────────────

    async def cancel_job(self, job_id: str) -> bool:
        """
        Signal that *job_id* should be cancelled.

        The worker checks :meth:`is_cancelled` before processing each item
        and should honour this flag.  Already-queued jobs cannot be removed
        from the FIFO list atomically, so cancellation is cooperative.

        Returns True if the signal was written.
        """
        self._check_connected()
        result = await self._redis.sadd(_CANCELLED_SET, job_id)
        await self._redis.expire(_CANCELLED_SET, _PROGRESS_TTL_SECS * 7)
        logger.info("[QueueManager] Cancel signal set for job %s", job_id)
        return bool(result)

    async def is_cancelled(self, job_id: str) -> bool:
        """Return True if *job_id* has been marked for cancellation."""
        self._check_connected()
        return bool(await self._redis.sismember(_CANCELLED_SET, job_id))

    async def clear_cancel(self, job_id: str) -> None:
        """Remove *job_id* from the cancelled set after cleanup."""
        self._check_connected()
        await self._redis.srem(_CANCELLED_SET, job_id)

    # ── Queue Inspection ──────────────────────────────────────────────────────

    async def queue_length(self) -> int:
        """Return the number of jobs waiting in the queue."""
        self._check_connected()
        return await self._redis.llen(self._queue_key)

    async def peek_queue(self, n: int = 10) -> list[dict[str, Any]]:
        """Return the first *n* jobs in the queue (without removing them)."""
        self._check_connected()
        payloads = await self._redis.lrange(self._queue_key, 0, n - 1)
        jobs = []
        for payload in payloads:
            with contextlib.suppress(json.JSONDecodeError):
                jobs.append(json.loads(payload))
        return jobs

    async def purge_queue(self) -> int:
        """
        Remove **all** jobs from the queue.

        ⚠️  Destructive — intended for development / testing only.
        """
        self._check_connected()
        length = await self._redis.llen(self._queue_key)
        await self._redis.delete(self._queue_key)
        logger.warning("[QueueManager] Purged %d jobs from queue", length)
        return length

    # ── Internal ─────────────────────────────────────────────────────────────

    def _check_connected(self) -> None:
        if self._redis is None:
            raise RuntimeError(
                "QueueManager not connected — call await qm.connect() first "
                "or use 'async with QueueManager(...) as qm:'"
            )
