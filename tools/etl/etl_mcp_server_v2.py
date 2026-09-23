"""
etl_mcp_server_v2.py — Legacy Eduboost ETL MCP Server Shim
==========================================================
DEPRECATED: Use tools.etl.etl_mcp_server as the canonical entry point instead.
Scheduled for removal in Release 2.1 (2026-10-31).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "tools.etl.etl_mcp_server_v2 is deprecated and will be removed in Release 2.1 (2026-10-31). "
    "Use tools.etl.etl_mcp_server as the canonical entry point instead.",
    DeprecationWarning,
    stacklevel=2,
)

from tools.etl.etl_mcp_server import (  # noqa: F401
    ETL_DB_URL,
    ETL_STORAGE,
    ETL_EXPORTS,
    mcp,
    pipeline,
    _start_mcp_server,
    _run_streamable_http_app,
    main,
    # All tool functions
    etl_ingest_document,
    etl_get_document,
    etl_list_documents,
    etl_run_pipeline,
    etl_run_stage,
    etl_approve_document,
    etl_reject_document,
    etl_reprocess_document,
    etl_get_review_queue,
    etl_get_pipeline_stats,
    etl_get_content_gaps,
    etl_get_quality_report,
    etl_get_document_chunks,
    etl_update_metadata,
    etl_create_document_version,
    etl_search_fulltext,
    etl_generate_training_data,
    etl_list_training_datasets,
    etl_export_dataset,
    etl_submit_feedback,
    etl_get_monitoring_report,
    etl_get_completeness_report,
    etl_get_audit_trail,
    etl_deprecate_document,
    etl_bulk_review,
    etl_assign_reviewer,
    etl_get_reviewer_workload,
    etl_split_dataset,
    etl_check_contamination,
    etl_get_dataset_statistics,
    etl_resolve_feedback,
    etl_get_metric_window,
)

__all__ = [
    "ETL_DB_URL",
    "ETL_STORAGE",
    "ETL_EXPORTS",
    "mcp",
    "pipeline",
    "_start_mcp_server",
    "_run_streamable_http_app",
    "main",
    "etl_ingest_document",
    "etl_get_document",
    "etl_list_documents",
    "etl_run_pipeline",
    "etl_run_stage",
    "etl_approve_document",
    "etl_reject_document",
    "etl_reprocess_document",
    "etl_get_review_queue",
    "etl_get_pipeline_stats",
    "etl_get_content_gaps",
    "etl_get_quality_report",
    "etl_get_document_chunks",
    "etl_update_metadata",
    "etl_create_document_version",
    "etl_search_fulltext",
    "etl_generate_training_data",
    "etl_list_training_datasets",
    "etl_export_dataset",
    "etl_submit_feedback",
    "etl_get_monitoring_report",
    "etl_get_completeness_report",
    "etl_get_audit_trail",
    "etl_deprecate_document",
    "etl_bulk_review",
    "etl_assign_reviewer",
    "etl_get_reviewer_workload",
    "etl_split_dataset",
    "etl_check_contamination",
    "etl_get_dataset_statistics",
    "etl_resolve_feedback",
    "etl_get_metric_window",
]

if __name__ == "__main__":
    main()
