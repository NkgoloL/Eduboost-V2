"""
etl_mcp_server_v3_additions.py — Eduboost ETL MCP Server: v3 Tool Additions
============================================================================
8 new tools wrapping EduboostETLv3 capabilities:

  etl_get_audit_trail         Phase 8  — chronological document audit trail
  etl_deprecate_document      Phase 8  — soft-deprecate with replacement link
  etl_bulk_review             Phase 11 — approve/reject multiple docs at once
  etl_assign_reviewer         Phase 11 — assign review task to a person
  etl_get_reviewer_workload   Phase 11 — open tasks per reviewer
  etl_split_dataset           Phase 10 — train/val/test split a dataset
  etl_check_contamination     Phase 10 — detect train/test overlap
  etl_get_dataset_statistics  Phase 10 — synthetic/reviewed/grade breakdown
  etl_resolve_feedback        Phase 12 — mark feedback as resolved
  etl_get_metric_window       Phase 12 — time-bucketed metric sparkline data

Merging into the v2 server
--------------------------
Paste these tool registrations at the bottom of etl_mcp_server_v2.py
(before the `if __name__ == "__main__":` block) and change the
pipeline() factory to return EduboostETLv3 instead of EduboostETLv2.

    from etl_pipeline_v3_additions import EduboostETLv3
    ...
    def pipeline() -> EduboostETLv3:
        global _pipeline
        if _pipeline is None:
            _pipeline = EduboostETLv3(db_url=ETL_DB_URL, storage_root=ETL_STORAGE)
            _pipeline.init_db()
            try:
                _pipeline.init_fts()
            except Exception:
                pass
        return _pipeline
"""

from __future__ import annotations

import dataclasses
import json
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# ── Re-use the server singleton from v2 ───────────────────────────────────
# In production: import `mcp` and `pipeline` from etl_mcp_server_v2
# Here shown as standalone for clarity.
from tools.etl.etl_mcp_server_v2 import mcp, pipeline   # type: ignore


# ===========================================================================
# INPUT MODELS
# ===========================================================================

class GetAuditTrailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document.")
    limit: int = Field(default=50, ge=1, le=500)


class DeprecateDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to deprecate.")
    deprecated_by: str = Field(..., description="Reviewer / admin user ID.")
    reason: str = Field(default="", description="Human-readable deprecation reason.")
    replacement_id: Optional[str] = Field(
        default=None,
        description="document_id of the replacement document, if one exists."
    )


class BulkReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_ids: list[str] = Field(
        ..., min_length=1, max_length=200,
        description="List of document UUIDs to approve or reject."
    )
    action: str = Field(
        ..., description="One of: approve | reject"
    )
    reviewer: str = Field(..., description="Reviewer user ID / email.")
    reason: str = Field(default="", description="Optional shared note for all decisions.")


class AssignReviewerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str = Field(..., description="UUID of the review task.")
    document_id: str = Field(..., description="UUID of the document under review.")
    assigned_to: str = Field(..., description="User ID / email of the assignee.")
    assigned_by: str = Field(default="system")
    priority: str = Field(
        default="normal",
        description="One of: low | normal | high | critical"
    )
    due_days: Optional[int] = Field(
        default=None, ge=1, le=90,
        description="Days from now until the review is due."
    )


class GetReviewerWorkloadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SplitDatasetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str = Field(..., description="UUID of the parent dataset to split.")
    train: float = Field(default=0.70, ge=0.1, le=0.9,
                         description="Fraction of examples for the train split.")
    val: float = Field(default=0.15, ge=0.0, le=0.5,
                       description="Fraction for the validation split (0 to skip).")
    test: float = Field(default=0.15, ge=0.05, le=0.5,
                        description="Fraction for the test split.")
    seed: int = Field(default=42, description="Random seed for reproducibility.")


class CheckContaminationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    train_dataset_id: str = Field(..., description="UUID of the training dataset.")
    test_dataset_id: str  = Field(..., description="UUID of the test dataset.")
    similarity_threshold: float = Field(
        default=0.90, ge=0.5, le=1.0,
        description="Exact-match hash threshold. 0.9 = flag 90%+ similar inputs."
    )


class GetDatasetStatisticsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str = Field(..., description="UUID of the dataset.")


class ResolveFeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feedback_id: str = Field(..., description="UUID of the feedback item.")
    resolved_by: str = Field(..., description="Reviewer / admin user ID.")
    resolution_type: str = Field(
        ...,
        description="One of: fixed | acknowledged | wont_fix | duplicate"
    )
    notes: str = Field(default="", description="Optional notes about the resolution.")


class GetMetricWindowInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metric_name: str = Field(
        ...,
        description=(
            "Metric counter name. Common values: ingestion_count, extraction_failures, "
            "validation_failures, approval_count, rejection_count, feedback_count."
        )
    )
    hours: int = Field(default=24, ge=1, le=720,
                       description="Lookback window in hours (max 30 days).")
    bucket_minutes: int = Field(
        default=60, ge=5, le=1440,
        description="Bucket size in minutes for aggregation."
    )


# ===========================================================================
# TOOL REGISTRATIONS
# ===========================================================================

@mcp.tool(name="etl_get_audit_trail", annotations={
    "title": "Get Document Audit Trail",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_audit_trail(params: GetAuditTrailInput) -> str:
    """
    Phase 8 — Return the chronological audit trail for a document.

    Every status change, metadata edit, approval, rejection, and deprecation
    is recorded. Use this to investigate how a document reached its current
    state or to satisfy audit requirements.

    Returns: list of {audit_id, action, field_name, old_value, new_value,
                       performed_by, performed_at, notes}
    """
    trail = pipeline().get_audit_trail(params.document_id, limit=params.limit)
    return json.dumps({"document_id": params.document_id, "count": len(trail), "trail": trail},
                      indent=2)


@mcp.tool(name="etl_deprecate_document", annotations={
    "title": "Deprecate Document",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_deprecate_document(params: DeprecateDocumentInput) -> str:
    """
    Phase 8 — Soft-deprecate a document (status → archived).

    Deprecated documents remain in the database for audit purposes but are
    excluded from search indexes, training sets, and the production content store.
    If a replacement document exists, pass its ID to create a traceability link.

    Use this when:
    - A newer edition of a document has been ingested
    - A document was found to be incorrectly licensed
    - Content is permanently outdated
    """
    try:
        result = pipeline().deprecate_document(
            document_id=params.document_id,
            deprecated_by=params.deprecated_by,
            reason=params.reason,
            replacement_id=params.replacement_id,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_bulk_review", annotations={
    "title": "Bulk Approve or Reject Documents",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_bulk_review(params: BulkReviewInput) -> str:
    """
    Phase 11 — Approve or reject up to 200 documents in one call.

    Useful for processing large review queues after a batch ingestion run.
    Each document result is reported individually — partial failures are normal
    (e.g., documents already approved or in an incompatible state).

    Returns: {total, succeeded, failed, results: [{document_id, success, ?error}]}
    """
    try:
        result = pipeline().bulk_review(
            document_ids=params.document_ids,
            action=params.action,
            reviewer=params.reviewer,
            reason=params.reason,
        )
        return json.dumps(dataclasses.asdict(result), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_assign_reviewer", annotations={
    "title": "Assign Review Task to Reviewer",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_assign_reviewer(params: AssignReviewerInput) -> str:
    """
    Phase 11 — Assign an open review task to a specific team member.

    Sets priority (low / normal / high / critical) and an optional due date.
    Use etl_get_reviewer_workload to balance assignments across reviewers.
    """
    try:
        result = pipeline().assign_reviewer(
            task_id=params.task_id,
            document_id=params.document_id,
            assigned_to=params.assigned_to,
            assigned_by=params.assigned_by,
            priority=params.priority,
            due_days=params.due_days,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_reviewer_workload", annotations={
    "title": "Get Reviewer Workload",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_reviewer_workload(params: GetReviewerWorkloadInput) -> str:
    """
    Phase 11 — Return open task counts per reviewer.

    Includes urgent (high/critical priority) task counts separately.
    Use before etl_assign_reviewer to avoid overloading any one reviewer.

    Returns: [{assigned_to, open_tasks, urgent}]
    """
    try:
        workload = pipeline().get_reviewer_workload()
        return json.dumps({"reviewers": workload}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_split_dataset", annotations={
    "title": "Split Training Dataset into Train/Val/Test",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_split_dataset(params: SplitDatasetInput) -> str:
    """
    Phase 10 — Split a training dataset into train / validation / test subsets.

    Uses deterministic hash-based shuffling for reproducibility. Creates three
    child datasets, moves examples into them, and records the split in
    dataset_splits. Run etl_check_contamination afterwards to verify no leakage.

    Returns: {parent_dataset_id, train_dataset_id, val_dataset_id,
              test_dataset_id, train_count, val_count, test_count}
    """
    try:
        assert abs(params.train + params.val + params.test - 1.0) < 1e-6, \
            "train + val + test must equal 1.0"
        result = pipeline().split_dataset(
            dataset_id=params.dataset_id,
            train=params.train, val=params.val, test=params.test,
            seed=params.seed,
        )
        return json.dumps(dataclasses.asdict(result), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_check_contamination", annotations={
    "title": "Check Train/Test Contamination",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_check_contamination(params: CheckContaminationInput) -> str:
    """
    Phase 10 — Detect input_text overlap between train and test datasets.

    Uses SHA-256 hashing for exact-match detection. Records results in
    contamination_checks for audit. A clean dataset returns passed=true
    and overlap_count=0.

    Run this after etl_split_dataset and before exporting training data.

    Returns: {check_id, overlap_count, overlap_example_ids, passed}
    """
    try:
        report = pipeline().check_contamination(
            train_dataset_id=params.train_dataset_id,
            test_dataset_id=params.test_dataset_id,
            similarity_threshold=params.similarity_threshold,
        )
        return json.dumps(dataclasses.asdict(report), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_dataset_statistics", annotations={
    "title": "Get Training Dataset Statistics",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_dataset_statistics(params: GetDatasetStatisticsInput) -> str:
    """
    Phase 10 — Detailed statistics for a training dataset.

    Includes:
    - synthetic vs human-reviewed example counts (and percentages)
    - average quality score
    - example type breakdown (qa / summary / concept / rubric / ...)
    - grade distribution
    - subject distribution

    Use before exporting to verify dataset composition meets quality criteria.
    """
    try:
        stats = pipeline().get_dataset_statistics(params.dataset_id)
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_resolve_feedback", annotations={
    "title": "Resolve User Feedback",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_resolve_feedback(params: ResolveFeedbackInput) -> str:
    """
    Phase 12 — Mark a user feedback item as resolved.

    resolution_type options:
      fixed         — Issue confirmed and corrected in the pipeline
      acknowledged  — Known issue, will be addressed in next cycle
      wont_fix      — Intentional design decision, no action needed
      duplicate     — Already tracked via another feedback item

    Resolving feedback closes any associated review task.
    """
    try:
        result = pipeline().resolve_feedback(
            feedback_id=params.feedback_id,
            resolved_by=params.resolved_by,
            resolution_type=params.resolution_type,
            notes=params.notes,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_metric_window", annotations={
    "title": "Get Pipeline Metric Time Window",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_metric_window(params: GetMetricWindowInput) -> str:
    """
    Phase 12 — Return time-bucketed metric aggregates for sparkline charts.

    Queries pipeline_metrics for a named counter and returns sum-per-bucket
    over the requested window.

    Common metric_name values:
      ingestion_count      — documents successfully ingested per hour
      extraction_failures  — extraction stage failures
      validation_failures  — quality gate failures
      approval_count       — documents approved per day
      rejection_count      — documents rejected per day
      feedback_count       — user feedback submissions

    Returns: [{bucket: "2025-05-20T14:00", value: 12.0}, ...]
    """
    try:
        buckets = pipeline().get_metric_window(
            metric_name=params.metric_name,
            hours=params.hours,
            bucket_minutes=params.bucket_minutes,
        )
        return json.dumps({
            "metric_name": params.metric_name,
            "hours": params.hours,
            "bucket_minutes": params.bucket_minutes,
            "buckets": buckets,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
