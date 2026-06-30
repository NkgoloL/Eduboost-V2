"""Lazy ETL pipeline factories for Content Factory integration.

This module intentionally imports only pipeline classes. MCP server wrappers
live under ``tools/etl`` and are not imported by application startup.
"""
from __future__ import annotations

from typing import Literal

from app.services.etl.etl_pipeline import EduboostETL
from app.services.etl.etl_pipeline_v2 import EduboostETLv2
from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3

ETLVersion = Literal["v1", "v2", "v3"]


def create_etl_pipeline(
    *,
    db_url: str,
    storage_root: str,
    version: ETLVersion = "v3",
) -> EduboostETL:
    pipeline_cls = {
        "v1": EduboostETL,
        "v2": EduboostETLv2,
        "v3": EduboostETLv3,
    }[version]
    return pipeline_cls(db_url=db_url, storage_root=storage_root)
