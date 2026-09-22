"""
batch_runner.py — Eduboost ETL Batch Ingestion Runner
=====================================================
Automated batch execution driver for ingesting, extracting, normalizing,
chunking, validating, and approving CAPS curriculum documents and topic maps.

Usage (CLI):
    python -m tools.etl.batch_runner --input-dir data/caps/topic_maps
    python -m tools.etl.batch_runner --input-dir data/caps/topic_maps --db-url sqlite:///eduboost_etl.db --auto-approve
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.services.etl.etl_pipeline import (
    DocumentType,
    IngestRequest,
    LicenseStatus,
    ProcessingStatus,
    SourceType,
)
from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3

logger = logging.getLogger("eduboost.etl.batch_runner")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class BatchDocumentResult:
    file_path: str
    filename: str
    document_id: Optional[str] = None
    checksum: str = ""
    status: str = "pending"
    quality_score: float = 0.0
    chunks_count: int = 0
    approved: bool = False
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class BatchRunSummary:
    started_at: str
    completed_at: str
    duration_seconds: float
    total_files: int
    successful_ingestions: int
    already_existing: int
    validated_count: int
    approved_count: int
    failed_count: int
    average_quality_score: float
    total_chunks: int
    results: list[BatchDocumentResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ETLBatchRunner:
    def __init__(
        self,
        db_url: str = "sqlite:///eduboost_etl.db",
        storage_root: str = "./data",
        auto_approve: bool = True,
    ) -> None:
        self.db_url = db_url
        self.storage_root = storage_root
        self.auto_approve = auto_approve
        self.etl = EduboostETLv3(db_url=self.db_url, storage_root=self.storage_root)
        self.etl.init_db()
        try:
            self.etl.init_fts()
        except Exception:
            pass

    def _infer_metadata(self, file_path: Path) -> dict[str, Any]:
        """Extract grade, subject, title, and document type from json or filename."""
        grade: Optional[int] = None
        subject: Optional[str] = None
        doc_type = DocumentType.curriculum_statement
        title: Optional[str] = None

        if file_path.suffix.lower() == ".json":
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if "grade" in data:
                        try:
                            grade = int(data["grade"])
                        except (ValueError, TypeError):
                            pass
                    if "subject" in data:
                        subject = str(data["subject"]).strip().lower().replace("&", "and")
                    if "items" in data:
                        doc_type = DocumentType.past_paper
                    elif "lessons" in data:
                        doc_type = DocumentType.lesson_plan
                    elif "terms" in data:
                        doc_type = DocumentType.curriculum_statement
            except Exception:
                pass

        stem = file_path.stem.lower()
        if grade is None:
            if "grader" in stem:
                grade = 0
            else:
                for g in range(1, 13):
                    if f"grade{g}" in stem or f"grade_{g}" in stem:
                        grade = g
                        break

        if subject is None:
            for candidate in (
                "mathematics", "maths", "coding_and_robotics", "home_language",
                "life_skills", "life_orientation", "social_sciences",
                "natural_sciences_and_technology", "natural_sciences",
                "technology", "economic_management_sciences", "creative_arts",
                "sepedi_first_additional_language",
            ):
                if candidate in stem:
                    subject = "mathematics" if candidate == "maths" else candidate
                    break

        if not title:
            grade_str = f"Grade {grade}" if grade is not None else ""
            subj_str = subject.replace("_", " ").title() if subject else ""
            title = f"CAPS {grade_str} {subj_str} Topic Map".strip() or stem.replace("_", " ").title()

        return {
            "grade": grade,
            "subject": subject,
            "document_type": doc_type,
            "title": title,
        }

    def process_file(
        self,
        file_path: Path,
        reprocess: bool = False,
    ) -> BatchDocumentResult:
        start_time = time.time()
        file_str = str(file_path.resolve())
        checksum = _file_sha256(file_path)
        meta = self._infer_metadata(file_path)

        res = BatchDocumentResult(
            file_path=file_str,
            filename=file_path.name,
            checksum=checksum,
        )

        try:
            # Check if document already ingested
            cursor = self.etl._db().execute(
                "SELECT document_id, processing_status, quality_score FROM documents WHERE checksum=?",
                (checksum,),
            )
            existing = cursor.fetchone()

            if existing:
                doc_id = existing["document_id"]
                res.document_id = doc_id
                status_str = existing["processing_status"]
                res.quality_score = float(existing["quality_score"] or 0.0)

                if reprocess or status_str in (ProcessingStatus.raw.value, ProcessingStatus.acquired.value, ProcessingStatus.extracted.value):
                    q_res = self.etl.run_full_pipeline(doc_id)
                    res.status = q_res.status.value if hasattr(q_res.status, "value") else str(q_res.status)
                    res.quality_score = q_res.quality_score
                else:
                    res.status = status_str

                chunks = self.etl.get_document_chunks(doc_id)
                res.chunks_count = len(chunks)

                if self.auto_approve and res.status == ProcessingStatus.validated.value:
                    try:
                        self.etl.approve_document(
                            doc_id,
                            reviewer="batch_runner",
                            notes="Automated CAPS batch ingestion approval",
                        )
                        res.approved = True
                        res.status = ProcessingStatus.approved.value
                    except Exception:
                        pass
                elif res.status == ProcessingStatus.approved.value:
                    res.approved = True

            else:
                # Ingest new document
                req = IngestRequest(
                    file_path=file_str,
                    document_type=meta["document_type"],
                    source_type=SourceType.government_repo,
                    license_status=LicenseStatus.government_open,
                    grade=meta["grade"],
                    subject=meta["subject"],
                    language="en",
                    title=meta["title"],
                    notes="Batch ingested via tools.etl.batch_runner",
                )
                doc = self.etl.ingest(req)
                res.document_id = doc.document_id

                # Run full pipeline stages (extract, normalize, chunk, validate)
                q_res = self.etl.run_full_pipeline(doc.document_id)
                res.status = q_res.status.value if hasattr(q_res.status, "value") else str(q_res.status)
                res.quality_score = q_res.quality_score

                chunks = self.etl.get_document_chunks(doc.document_id)
                res.chunks_count = len(chunks)

                # Auto-approve if quality passed
                if self.auto_approve and res.status == ProcessingStatus.validated.value:
                    self.etl.approve_document(
                        doc.document_id,
                        reviewer="batch_runner",
                        notes="Automated CAPS batch ingestion approval",
                    )
                    res.approved = True
                    res.status = ProcessingStatus.approved.value

        except Exception as e:
            res.status = "failed"
            res.error = str(e)
            logger.exception("Failed processing %s: %s", file_path, e)

        res.duration_ms = round((time.time() - start_time) * 1000, 2)
        return res

    def process_directory(
        self,
        input_dir: Path,
        pattern: str = "*.json",
        reprocess: bool = False,
    ) -> BatchRunSummary:
        start_ts = time.time()
        started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_ts))

        files = sorted(list(input_dir.glob(pattern)))
        results: list[BatchDocumentResult] = []

        for p in files:
            r = self.process_file(p, reprocess=reprocess)
            results.append(r)

        end_ts = time.time()
        completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_ts))

        total_files = len(results)
        failed_count = sum(1 for r in results if r.status == "failed" or r.error)
        approved_count = sum(1 for r in results if r.approved or r.status == ProcessingStatus.approved.value)
        validated_count = sum(
            1 for r in results
            if r.status in (ProcessingStatus.validated.value, ProcessingStatus.approved.value)
        )
        total_chunks = sum(r.chunks_count for r in results)
        valid_scores = [r.quality_score for r in results if r.quality_score > 0]
        avg_score = round(sum(valid_scores) / len(valid_scores), 4) if valid_scores else 0.0

        summary = BatchRunSummary(
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=round(end_ts - start_ts, 2),
            total_files=total_files,
            successful_ingestions=total_files - failed_count,
            already_existing=0,
            validated_count=validated_count,
            approved_count=approved_count,
            failed_count=failed_count,
            average_quality_score=avg_score,
            total_chunks=total_chunks,
            results=results,
        )
        return summary


def run_batch_ingestion(
    input_dir: str = "data/caps/topic_maps",
    db_url: str = "sqlite:///eduboost_etl.db",
    storage_root: str = "./data",
    output_report: Optional[str] = "docs/etl/caps_batch_ingestion_report.json",
    auto_approve: bool = True,
    reprocess: bool = False,
) -> dict[str, Any]:
    in_dir = Path(input_dir)
    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    runner = ETLBatchRunner(
        db_url=db_url,
        storage_root=storage_root,
        auto_approve=auto_approve,
    )
    summary = runner.process_directory(in_dir, pattern="*.json", reprocess=reprocess)
    summary_dict = summary.to_dict()

    if output_report:
        out_p = Path(output_report)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(summary_dict, indent=2) + "\n", encoding="utf-8")

    return summary_dict


def main() -> None:
    parser = argparse.ArgumentParser(description="Eduboost ETL Batch Runner")
    parser.add_argument("--input-dir", default="data/caps/topic_maps",
                        help="Directory containing JSON files to ingest (default: data/caps/topic_maps)")
    parser.add_argument("--db-url", default=os.getenv("ETL_DB_URL", "sqlite:///eduboost_etl.db"),
                        help="Database URL")
    parser.add_argument("--storage-root", default=os.getenv("ETL_STORAGE_ROOT", "./data"),
                        help="Raw file storage directory")
    parser.add_argument("--output-report", default="docs/etl/caps_batch_ingestion_report.json",
                        help="Summary JSON output report path")
    parser.add_argument("--no-auto-approve", action="store_true",
                        help="Do not auto-promote validated documents to approved")
    parser.add_argument("--reprocess", action="store_true",
                        help="Force re-running pipeline even if document exists")

    args = parser.parse_args()
    summary = run_batch_ingestion(
        input_dir=args.input_dir,
        db_url=args.db_url,
        storage_root=args.storage_root,
        output_report=args.output_report,
        auto_approve=not args.no_auto_approve,
        reprocess=args.reprocess,
    )

    print(f"Batch Ingestion Complete: {summary['successful_ingestions']}/{summary['total_files']} succeeded.")
    print(f"Validated: {summary['validated_count']}, Approved: {summary['approved_count']}, Chunks: {summary['total_chunks']}")
    print(f"Average Quality Score: {summary['average_quality_score']}")
    if args.output_report:
        print(f"Report written to: {args.output_report}")


if __name__ == "__main__":
    main()
