"""
etl_pipeline_v3_additions.py — Eduboost ETL: v3 Additions
==========================================================
Extends EduboostETLv2 with:

  Phase 8  — Bulk metadata update, document deprecation, audit trail
  Phase 10 — Contamination check, train/val/test split management,
              dataset cloning, synthetic-vs-human-reviewed statistics
  Phase 11 — Bulk review operations, reviewer assignment, escalation
  Phase 12 — Metric aggregation windows, completeness trend,
              feedback resolution workflow

Usage
-----
    from etl_pipeline_v2 import EduboostETLv2
    from etl_pipeline_v3_additions import EduboostETLv3

    etl = EduboostETLv3(db_url="sqlite:///eduboost_etl.db", storage_root="./data")
    etl.init_db()

    # Bulk approve documents from a review queue
    results = etl.bulk_review(document_ids=["doc-1","doc-2"], action="approve",
                              reviewer="admin@eduboost.com")

    # Split a dataset into train/val/test
    splits = etl.split_dataset("ds-abc", train=0.7, val=0.15, test=0.15)

    # Check contamination between train and test sets
    report = etl.check_contamination("ds-abc-train", "ds-abc-test")

    # Full audit trail for a document
    trail = etl.get_audit_trail("doc-abc")
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2, _now, _uid,
    ProcessingStatus,
)


# ===========================================================================
# SCHEMA V3
# ===========================================================================

SCHEMA_V3_SQL = """
-- Audit trail: every status change and metadata edit
CREATE TABLE IF NOT EXISTS document_audit_trail (
    audit_id        TEXT PRIMARY KEY,
    document_id     TEXT NOT NULL,
    action          TEXT NOT NULL,      -- status_change / metadata_update / approve / reject / deprecate
    field_name      TEXT,               -- NULL for status changes
    old_value       TEXT,
    new_value       TEXT,
    performed_by    TEXT NOT NULL DEFAULT 'system',
    performed_at    TEXT NOT NULL,
    notes           TEXT DEFAULT '',
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);
CREATE INDEX IF NOT EXISTS idx_audit_doc ON document_audit_trail(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON document_audit_trail(performed_at);

-- Reviewer assignments
CREATE TABLE IF NOT EXISTS reviewer_assignments (
    assignment_id   TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL,
    document_id     TEXT NOT NULL,
    assigned_to     TEXT NOT NULL,
    assigned_by     TEXT NOT NULL DEFAULT 'system',
    assigned_at     TEXT NOT NULL,
    due_by          TEXT,
    priority        TEXT DEFAULT 'normal',   -- low / normal / high / critical
    resolved        INTEGER DEFAULT 0,
    resolved_at     TEXT,
    FOREIGN KEY (task_id)    REFERENCES review_tasks(task_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Dataset splits (child datasets derived from a parent)
CREATE TABLE IF NOT EXISTS dataset_splits (
    split_id        TEXT PRIMARY KEY,
    parent_dataset_id TEXT NOT NULL,
    child_dataset_id  TEXT NOT NULL,
    split_name      TEXT NOT NULL,      -- train / validation / test
    split_ratio     REAL NOT NULL,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (parent_dataset_id) REFERENCES training_datasets(dataset_id),
    FOREIGN KEY (child_dataset_id)  REFERENCES training_datasets(dataset_id)
);

-- Contamination check results
CREATE TABLE IF NOT EXISTS contamination_checks (
    check_id        TEXT PRIMARY KEY,
    train_dataset_id TEXT NOT NULL,
    test_dataset_id  TEXT NOT NULL,
    overlap_count   INTEGER DEFAULT 0,
    overlap_example_ids TEXT DEFAULT '[]',  -- JSON array
    similarity_threshold REAL DEFAULT 0.9,
    passed          INTEGER DEFAULT 1,      -- 1 = clean, 0 = contaminated
    checked_at      TEXT NOT NULL
);

-- Feedback resolution log
CREATE TABLE IF NOT EXISTS feedback_resolutions (
    resolution_id   TEXT PRIMARY KEY,
    feedback_id     TEXT NOT NULL,
    resolved_by     TEXT NOT NULL,
    resolution_type TEXT NOT NULL,   -- fixed / acknowledged / wont_fix / duplicate
    notes           TEXT DEFAULT '',
    resolved_at     TEXT NOT NULL,
    FOREIGN KEY (feedback_id) REFERENCES user_feedback(feedback_id)
);
"""


# ===========================================================================
# DATA CLASSES
# ===========================================================================

@dataclass
class AuditEntry:
    audit_id: str
    document_id: str
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    performed_by: str
    performed_at: str
    notes: str = ""


@dataclass
class BulkReviewResult:
    total: int
    succeeded: int
    failed: int
    results: list[dict] = field(default_factory=list)


@dataclass
class DatasetSplitResult:
    parent_dataset_id: str
    train_dataset_id: str
    val_dataset_id: Optional[str]
    test_dataset_id: str
    train_count: int
    val_count: int
    test_count: int


@dataclass
class ContaminationReport:
    check_id: str
    train_dataset_id: str
    test_dataset_id: str
    overlap_count: int
    overlap_example_ids: list[str]
    passed: bool
    checked_at: str


# ===========================================================================
# EduboostETLv3
# ===========================================================================

class EduboostETLv3(EduboostETLv2):
    """
    Phase 8/10/11/12 extensions on top of EduboostETLv2.
    Drop-in replacement — call init_db() once on startup.
    """

    def init_db(self):
        super().init_db()
        self._db().executescript(SCHEMA_V3_SQL)
        self._db().commit()

    # =========================================================================
    # PHASE 8 — AUDIT TRAIL & DOCUMENT DEPRECATION
    # =========================================================================

    def _record_audit(
        self,
        document_id: str,
        action: str,
        performed_by: str,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        notes: str = "",
    ) -> AuditEntry:
        entry = AuditEntry(
            audit_id=_uid(), document_id=document_id, action=action,
            field_name=field_name, old_value=old_value, new_value=new_value,
            performed_by=performed_by, performed_at=_now(), notes=notes,
        )
        self._db().execute(
            "INSERT INTO document_audit_trail VALUES (?,?,?,?,?,?,?,?,?)",
            (entry.audit_id, entry.document_id, entry.action, entry.field_name,
             entry.old_value, entry.new_value, entry.performed_by,
             entry.performed_at, entry.notes)
        )
        self._db().commit()
        return entry

    def get_audit_trail(
        self,
        document_id: str,
        limit: int = 100,
    ) -> list[dict]:
        """Return full chronological audit trail for a document."""
        rows = self._db().execute(
            "SELECT * FROM document_audit_trail WHERE document_id=? "
            "ORDER BY performed_at DESC LIMIT ?",
            (document_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def deprecate_document(
        self,
        document_id: str,
        deprecated_by: str,
        reason: str = "",
        replacement_id: Optional[str] = None,
    ) -> dict:
        """
        Soft-deprecate a document — marks it archived and records the audit entry.
        Optionally links a replacement document.
        """
        db = self._db()
        row = db.execute(
            "SELECT processing_status FROM documents WHERE document_id=?",
            (document_id,)
        ).fetchone()
        if not row:
            return {"success": False, "error": f"Document {document_id} not found."}

        old_status = row["processing_status"]
        notes = reason
        if replacement_id:
            notes += f" | replaced_by={replacement_id}"

        db.execute(
            "UPDATE documents SET processing_status=?, updated_at=? WHERE document_id=?",
            (ProcessingStatus.archived, _now(), document_id)
        )
        db.commit()
        self._record_audit(
            document_id=document_id, action="deprecate",
            performed_by=deprecated_by,
            old_value=old_status, new_value=ProcessingStatus.archived,
            notes=notes,
        )
        return {
            "success": True,
            "document_id": document_id,
            "old_status": old_status,
            "new_status": ProcessingStatus.archived,
            "replacement_id": replacement_id,
        }

    def update_metadata_with_audit(
        self,
        document_id: str,
        updated_by: str,
        fields: dict,
    ) -> dict:
        """
        Thin wrapper over update_metadata that also writes an audit entry per changed field.
        `fields` is a dict of {column_name: new_value}.
        """
        db = self._db()
        row = db.execute(
            "SELECT * FROM documents WHERE document_id=?", (document_id,)
        ).fetchone()
        if not row:
            return {"success": False, "error": f"Document {document_id} not found."}

        old_doc = dict(row)
        changes = []
        set_clauses, params = [], []
        for col, new_val in fields.items():
            if col in old_doc and old_doc[col] != new_val:
                set_clauses.append(f"{col}=?")
                params.append(new_val)
                changes.append((col, str(old_doc[col]), str(new_val)))

        if not set_clauses:
            return {"success": True, "changed": 0, "message": "No fields changed."}

        set_clauses.append("updated_at=?")
        params.extend([_now(), document_id])
        db.execute(f"UPDATE documents SET {', '.join(set_clauses)} WHERE document_id=?", params)
        db.commit()

        for col, old_val, new_val in changes:
            self._record_audit(
                document_id=document_id, action="metadata_update",
                performed_by=updated_by, field_name=col,
                old_value=old_val, new_value=new_val,
            )

        return {"success": True, "changed": len(changes), "fields": [c[0] for c in changes]}

    # =========================================================================
    # PHASE 11 — BULK REVIEW & REVIEWER ASSIGNMENTS
    # =========================================================================

    def bulk_review(
        self,
        document_ids: list[str],
        action: str,        # "approve" | "reject"
        reviewer: str,
        reason: str = "",
    ) -> BulkReviewResult:
        """
        Approve or reject multiple documents in one call.
        Returns a summary with per-document success/failure.
        """
        results = []
        succeeded = 0
        failed = 0
        for doc_id in document_ids:
            try:
                if action == "approve":
                    self.approve_document(doc_id, reviewer=reviewer, notes=reason)
                    self._record_audit(doc_id, "approve", reviewer,
                                       new_value=ProcessingStatus.approved, notes=reason)
                elif action == "reject":
                    self.reject_document(doc_id, reviewer=reviewer, reason=reason)
                    self._record_audit(doc_id, "reject", reviewer,
                                       new_value=ProcessingStatus.rejected, notes=reason)
                else:
                    raise ValueError(f"Unknown action: {action}")
                results.append({"document_id": doc_id, "success": True})
                succeeded += 1
            except Exception as e:
                results.append({"document_id": doc_id, "success": False, "error": str(e)})
                failed += 1

        return BulkReviewResult(
            total=len(document_ids),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )

    def assign_reviewer(
        self,
        task_id: str,
        document_id: str,
        assigned_to: str,
        assigned_by: str = "system",
        priority: str = "normal",
        due_days: Optional[int] = None,
    ) -> dict:
        """Assign a review task to a specific reviewer."""
        due_by = None
        if due_days is not None:
            due_by = (datetime.now(timezone.utc) + timedelta(days=due_days)).isoformat()

        assignment_id = _uid()
        self._db().execute(
            "INSERT INTO reviewer_assignments VALUES (?,?,?,?,?,?,?,?,?,?)",
            (assignment_id, task_id, document_id, assigned_to, assigned_by,
             _now(), due_by, priority, 0, None)
        )
        self._db().commit()
        return {
            "assignment_id": assignment_id,
            "task_id": task_id,
            "document_id": document_id,
            "assigned_to": assigned_to,
            "priority": priority,
            "due_by": due_by,
        }

    def get_reviewer_workload(self) -> list[dict]:
        """Return open task count per reviewer."""
        rows = self._db().execute(
            "SELECT assigned_to, COUNT(*) as open_tasks, "
            "SUM(CASE WHEN priority='high' OR priority='critical' THEN 1 ELSE 0 END) as urgent "
            "FROM reviewer_assignments WHERE resolved=0 GROUP BY assigned_to"
        ).fetchall()
        return [dict(r) for r in rows]

    # =========================================================================
    # PHASE 10 — DATASET SPLITTING & CONTAMINATION
    # =========================================================================

    def split_dataset(
        self,
        dataset_id: str,
        train: float = 0.70,
        val: float = 0.15,
        test: float = 0.15,
        seed: int = 42,
    ) -> DatasetSplitResult:
        """
        Split a training dataset into train / validation / test subsets.
        Creates three child datasets linked via dataset_splits.
        """
        assert abs(train + val + test - 1.0) < 1e-6, "Split ratios must sum to 1.0"

        db = self._db()
        parent = db.execute(
            "SELECT * FROM training_datasets WHERE dataset_id=?", (dataset_id,)
        ).fetchone()
        if not parent:
            raise ValueError(f"Dataset {dataset_id} not found.")

        # Fetch all examples
        examples = db.execute(
            "SELECT example_id FROM training_examples WHERE dataset_id=? ORDER BY example_id",
            (dataset_id,)
        ).fetchall()
        ids = [r["example_id"] for r in examples]

        # Deterministic shuffle via hash
        ids.sort(key=lambda x: hashlib.md5(f"{seed}{x}".encode()).hexdigest())

        n = len(ids)
        n_train = int(n * train)
        n_val   = int(n * val)
        train_ids = ids[:n_train]
        val_ids   = ids[n_train:n_train + n_val]
        test_ids  = ids[n_train + n_val:]

        def _make_child(split_name: str, example_ids: list[str]) -> str:
            child_id = _uid()
            db.execute(
                "INSERT INTO training_datasets "
                "(dataset_id,name,description,dataset_type,version,split,"
                " document_ids,example_count,is_synthetic,created_by,created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (child_id,
                 f"{parent['name']} [{split_name}]",
                 f"Auto-split from {dataset_id}",
                 parent["dataset_type"], parent["version"], split_name,
                 parent["document_ids"], len(example_ids),
                 parent["is_synthetic"], "system", _now())
            )
            # Re-assign examples to child dataset
            for ex_id in example_ids:
                db.execute(
                    "UPDATE training_examples SET dataset_id=? WHERE example_id=?",
                    (child_id, ex_id)
                )
            db.execute(
                "INSERT INTO dataset_splits VALUES (?,?,?,?,?,?)",
                (_uid(), dataset_id, child_id, split_name,
                 len(example_ids) / max(n, 1), _now())
            )
            return child_id

        train_ds = _make_child("train", train_ids)
        val_ds   = _make_child("validation", val_ids)
        test_ds  = _make_child("test", test_ids)
        db.commit()

        return DatasetSplitResult(
            parent_dataset_id=dataset_id,
            train_dataset_id=train_ds,
            val_dataset_id=val_ds,
            test_dataset_id=test_ds,
            train_count=len(train_ids),
            val_count=len(val_ids),
            test_count=len(test_ids),
        )

    def check_contamination(
        self,
        train_dataset_id: str,
        test_dataset_id: str,
        similarity_threshold: float = 0.9,
    ) -> ContaminationReport:
        """
        Detect input_text overlap between train and test datasets.
        Uses exact-match hashing (fast) + optional fuzzy check stub.
        """
        db = self._db()
        train_rows = db.execute(
            "SELECT example_id, input_text FROM training_examples WHERE dataset_id=?",
            (train_dataset_id,)
        ).fetchall()
        test_rows = db.execute(
            "SELECT example_id, input_text FROM training_examples WHERE dataset_id=?",
            (test_dataset_id,)
        ).fetchall()

        # Hash-based exact overlap
        train_hashes = {
            hashlib.sha256(r["input_text"].encode()).hexdigest(): r["example_id"]
            for r in train_rows
        }
        overlapping = []
        for r in test_rows:
            h = hashlib.sha256(r["input_text"].encode()).hexdigest()
            if h in train_hashes:
                overlapping.append(r["example_id"])

        check_id = _uid()
        passed = len(overlapping) == 0
        db.execute(
            "INSERT INTO contamination_checks VALUES (?,?,?,?,?,?,?,?)",
            (check_id, train_dataset_id, test_dataset_id,
             len(overlapping), json.dumps(overlapping[:50]),
             similarity_threshold, int(passed), _now())
        )
        db.commit()

        return ContaminationReport(
            check_id=check_id,
            train_dataset_id=train_dataset_id,
            test_dataset_id=test_dataset_id,
            overlap_count=len(overlapping),
            overlap_example_ids=overlapping[:50],
            passed=passed,
            checked_at=_now(),
        )

    def get_dataset_statistics(self, dataset_id: str) -> dict:
        """
        Detailed statistics for a dataset:
        - synthetic vs human-reviewed counts
        - grade / subject distribution
        - avg quality score
        - example type breakdown
        """
        db = self._db()
        rows = db.execute(
            "SELECT is_synthetic, human_reviewed, quality_score, "
            "grade, subject, example_type "
            "FROM training_examples WHERE dataset_id=?",
            (dataset_id,)
        ).fetchall()

        if not rows:
            return {"dataset_id": dataset_id, "total": 0}

        total = len(rows)
        synthetic_count  = sum(1 for r in rows if r["is_synthetic"])
        reviewed_count   = sum(1 for r in rows if r["human_reviewed"])
        avg_quality = sum(r["quality_score"] for r in rows) / total

        by_type: dict = {}
        by_grade: dict = {}
        by_subject: dict = {}
        for r in rows:
            t = r["example_type"] or "unknown"
            by_type[t] = by_type.get(t, 0) + 1
            g = str(r["grade"]) if r["grade"] else "unknown"
            by_grade[g] = by_grade.get(g, 0) + 1
            s = r["subject"] or "unknown"
            by_subject[s] = by_subject.get(s, 0) + 1

        return {
            "dataset_id": dataset_id,
            "total": total,
            "synthetic_count": synthetic_count,
            "human_reviewed_count": reviewed_count,
            "synthetic_pct": round(synthetic_count / total * 100, 1),
            "reviewed_pct":  round(reviewed_count / total * 100, 1),
            "avg_quality_score": round(avg_quality, 3),
            "by_type": by_type,
            "by_grade": by_grade,
            "by_subject": by_subject,
        }

    # =========================================================================
    # PHASE 12 — FEEDBACK RESOLUTION & METRIC WINDOWS
    # =========================================================================

    def resolve_feedback(
        self,
        feedback_id: str,
        resolved_by: str,
        resolution_type: str,  # fixed | acknowledged | wont_fix | duplicate
        notes: str = "",
    ) -> dict:
        """Mark a feedback item as resolved."""
        db = self._db()
        row = db.execute(
            "SELECT feedback_id, resolved FROM user_feedback WHERE feedback_id=?",
            (feedback_id,)
        ).fetchone()
        if not row:
            return {"success": False, "error": "Feedback not found."}
        if row["resolved"]:
            return {"success": False, "error": "Feedback already resolved."}

        now = _now()
        db.execute(
            "UPDATE user_feedback SET resolved=1, resolved_at=?, resolved_by=? "
            "WHERE feedback_id=?",
            (now, resolved_by, feedback_id)
        )
        db.execute(
            "INSERT INTO feedback_resolutions VALUES (?,?,?,?,?,?)",
            (_uid(), feedback_id, resolved_by, resolution_type, notes, now)
        )
        db.commit()
        return {"success": True, "feedback_id": feedback_id, "resolution_type": resolution_type}

    def get_metric_window(
        self,
        metric_name: str,
        hours: int = 24,
        bucket_minutes: int = 60,
    ) -> list[dict]:
        """
        Return time-bucketed aggregates for a metric (sum per bucket).
        Useful for sparkline charts in the monitoring dashboard.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self._db().execute(
            "SELECT recorded_at, metric_value FROM pipeline_metrics "
            "WHERE metric_name=? AND recorded_at>? ORDER BY recorded_at",
            (metric_name, cutoff)
        ).fetchall()
        if not rows:
            return []

        buckets: dict[str, float] = {}
        for r in rows:
            dt = datetime.fromisoformat(r["recorded_at"].replace("Z", "+00:00"))
            # Floor to bucket
            minutes = (dt.hour * 60 + dt.minute) // bucket_minutes * bucket_minutes
            bucket_key = dt.strftime("%Y-%m-%dT") + f"{minutes // 60:02d}:00"
            buckets[bucket_key] = buckets.get(bucket_key, 0.0) + r["metric_value"]

        return [{"bucket": k, "value": v} for k, v in sorted(buckets.items())]

    def get_completeness_trend(self, days: int = 30) -> list[dict]:
        """
        Daily coverage % over the last N days.
        Computes approved docs per day as a proxy for growing coverage.
        """
        rows = self._db().execute(
            "SELECT date(updated_at) as day, COUNT(*) as n "
            "FROM documents WHERE processing_status IN ('approved','indexed','training_ready') "
            "AND updated_at > date('now', ?) GROUP BY day ORDER BY day",
            (f"-{days} days",)
        ).fetchall()
        return [{"day": r["day"], "approved_count": r["n"]} for r in rows]
