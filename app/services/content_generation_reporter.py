"""Report writer for full generation runs."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GenerationReportData:
    """Data for generation report."""
    run_id: str
    scope_id: str
    status: str
    planned_tasks: int
    executed_tasks: int
    generated_artifacts: int
    pending_review: int
    validation_failed: int
    source_blockers: int
    staging_seed_results: int
    staging_verification_passed: bool | None
    errors: list[str] = field(default_factory=list)
    scope_readiness_before: dict[str, Any] = field(default_factory=dict)
    scope_readiness_after: dict[str, Any] = field(default_factory=dict)
    planned_tasks_list: list[dict[str, Any]] = field(default_factory=list)
    executed_tasks_list: list[dict[str, Any]] = field(default_factory=list)
    generated_artifacts_list: list[dict[str, Any]] = field(default_factory=list)
    pending_review_list: list[dict[str, Any]] = field(default_factory=list)
    validation_failed_list: list[dict[str, Any]] = field(default_factory=list)
    source_blockers_list: list[dict[str, Any]] = field(default_factory=list)
    staging_seed_results_list: list[dict[str, Any]] = field(default_factory=list)


class ContentGenerationReporter:
    """Write reports for full generation runs."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or "reports/content_factory/full_generation")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, data: GenerationReportData) -> Path:
        """Write a full generation report.

        Args:
            data: Generation report data

        Returns:
            Path to the report directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.base_dir / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)

        # Write summary.md
        self._write_summary_md(report_dir, data)

        # Write summary.json
        self._write_summary_json(report_dir, data)

        # Write scope readiness
        self._write_json(report_dir / "scope_readiness_before.json", data.scope_readiness_before)
        self._write_json(report_dir / "scope_readiness_after.json", data.scope_readiness_after)

        # Write CSV files
        self._write_csv(report_dir / "planned_tasks.csv", data.planned_tasks_list)
        self._write_csv(report_dir / "executed_tasks.csv", data.executed_tasks_list)
        self._write_csv(report_dir / "generated_artifacts.csv", data.generated_artifacts_list)
        self._write_csv(report_dir / "pending_review.csv", data.pending_review_list)
        self._write_csv(report_dir / "validation_failed.csv", data.validation_failed_list)
        self._write_csv(report_dir / "source_blockers.csv", data.source_blockers_list)
        self._write_csv(report_dir / "staging_seed_results.csv", data.staging_seed_results_list)

        # Write staging verification
        self._write_json(
            report_dir / "staging_verification.json",
            {"passed": data.staging_verification_passed},
        )

        # Write errors log
        if data.errors:
            self._write_errors_log(report_dir / "errors.log", data.errors)

        return report_dir

    def _write_summary_md(self, report_dir: Path, data: GenerationReportData) -> None:
        """Write summary markdown file."""
        summary_path = report_dir / "summary.md"
        with open(summary_path, "w") as f:
            f.write("# Full Generation Run Report\n\n")
            f.write(f"**Run ID:** {data.run_id}\n")
            f.write(f"**Scope:** {data.scope_id}\n")
            f.write(f"**Status:** {data.status}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Planned Tasks:** {data.planned_tasks}\n")
            f.write(f"- **Executed Tasks:** {data.executed_tasks}\n")
            f.write(f"- **Generated Artifacts:** {data.generated_artifacts}\n")
            f.write(f"- **Pending Review:** {data.pending_review}\n")
            f.write(f"- **Validation Failed:** {data.validation_failed}\n")
            f.write(f"- **Source Blockers:** {data.source_blockers}\n")
            f.write(f"- **Staging Seed Results:** {data.staging_seed_results}\n")
            f.write(f"- **Staging Verification:** {'Passed' if data.staging_verification_passed else 'Failed'}\n\n")

            if data.errors:
                f.write("## Errors\n\n")
                for error in data.errors:
                    f.write(f"- {error}\n")
                f.write("\n")

            f.write("## Files\n\n")
            f.write("- `summary.json` - Machine-readable summary\n")
            f.write("- `scope_readiness_before.json` - Scope readiness before run\n")
            f.write("- `scope_readiness_after.json` - Scope readiness after run\n")
            f.write("- `planned_tasks.csv` - Planned generation tasks\n")
            f.write("- `executed_tasks.csv` - Executed tasks\n")
            f.write("- `generated_artifacts.csv` - Generated artifacts\n")
            f.write("- `pending_review.csv` - Artifacts pending review\n")
            f.write("- `validation_failed.csv` - Artifacts that failed validation\n")
            f.write("- `source_blockers.csv` - Source context blockers\n")
            f.write("- `staging_seed_results.csv` - Staging seed results\n")
            f.write("- `staging_verification.json` - Staging verification result\n")
            if data.errors:
                f.write("- `errors.log` - Error log\n")

    def _write_summary_json(self, report_dir: Path, data: GenerationReportData) -> None:
        """Write summary JSON file."""
        summary_path = report_dir / "summary.json"
        summary = {
            "run_id": data.run_id,
            "scope_id": data.scope_id,
            "status": data.status,
            "planned_tasks": data.planned_tasks,
            "executed_tasks": data.executed_tasks,
            "generated_artifacts": data.generated_artifacts,
            "pending_review": data.pending_review,
            "validation_failed": data.validation_failed,
            "source_blockers": data.source_blockers,
            "staging_seed_results": data.staging_seed_results,
            "staging_verification_passed": data.staging_verification_passed,
            "errors": data.errors,
        }
        self._write_json(summary_path, summary)

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Write JSON file."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _write_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        """Write CSV file."""
        if not rows:
            return

        if not rows[0]:
            return

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def _write_errors_log(self, path: Path, errors: list[str]) -> None:
        """Write errors log file."""
        with open(path, "w") as f:
            for error in errors:
                f.write(f"{error}\n")
