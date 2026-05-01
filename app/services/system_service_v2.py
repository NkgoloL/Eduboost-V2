"""V2 system/status service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import inspect

from app.api.core.database import AsyncSessionFactory
from app.services.audit_service import AuditService


class SystemServiceV2:
    async def health(self) -> dict:
        status = {
            "overall": "GREEN",
            "mode": "v2-baseline",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await AuditService().log_event(event_type="SYSTEM_HEALTH_READ", payload={"mode": "v2-baseline"})
        return status

    async def pillars(self) -> dict:
        async with AsyncSessionFactory() as session:
            inspector = inspect(session.sync_session.get_bind())
            tables = inspector.get_table_names()
        return {
            "architecture": "modular-monolith",
            "audit_target": "postgresql-append-only",
            "async_model": "backgroundtasks-first",
            "table_count": len(tables),
        }

    async def schema_status(self) -> dict:
        async with AsyncSessionFactory() as session:
            inspector = inspect(session.sync_session.get_bind())
            tables = sorted(inspector.get_table_names())
        await AuditService().log_event(event_type="SYSTEM_SCHEMA_STATUS_READ", payload={"table_count": len(tables)})
        return {"table_count": len(tables), "tables": tables}
