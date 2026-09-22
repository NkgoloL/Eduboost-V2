"""
etl_mcp_server.py — Eduboost ETL MCP Server (Canonical Entry Point)
===================================================================
Re-exports the unified 32-tool FastMCP server from etl_mcp_server_v2,
powered by EduboostETLv3.
"""
from __future__ import annotations

import argparse
import sys

from tools.etl.etl_mcp_server_v2 import (
    ETL_DB_URL,
    ETL_STORAGE,
    ETL_EXPORTS,
    mcp,
    pipeline,
    _start_mcp_server,
    _run_streamable_http_app,
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
    parser = argparse.ArgumentParser(description="Eduboost ETL MCP Server")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"],
                        default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    print(f"Starting Eduboost ETL MCP Server (transport={args.transport})", file=sys.stderr)
    print(f"  DB:      {ETL_DB_URL}",  file=sys.stderr)
    print(f"  Storage: {ETL_STORAGE}", file=sys.stderr)
    print(f"  Exports: {ETL_EXPORTS}", file=sys.stderr)

    _start_mcp_server(mcp, transport=args.transport, host=args.host, port=args.port)
