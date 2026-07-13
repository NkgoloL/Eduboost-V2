"""Budget, checkpoint, resume, and package helpers for Execution-7 terminal isolation.

The helpers are deliberately independent from pytest execution so their contracts can
be validated without running the full repository test suite.  They do not capture
Execution-7 green evidence or authorise Execution-8.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import tarfile
import time
from typing import Any, Sequence

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
REMEDIATION_ID = "PRD-11.0R.EXECUTION-7.BUDGETED-TERMINAL-ISOLATION-COMPLETION"
DEFAULT_OVERALL_BUDGET_SECONDS = 3900
DEFAULT_PACKAGING_RESERVE_SECONDS = 300
DEFAULT_OUTER_GATE_TIMEOUT_SECONDS = 4200
DEFAULT_MAX_BISECTION_DEPTH = 8
DEFAULT_MAX_GENERATED_LEAVES = 256
DEFAULT_TERMINAL_FILE_WORKERS = 2
DEFAULT_TERMINAL_NODE_WORKERS = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON through an adjacent temporary file and atomic replacement."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def revision_sha(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "git-unavailable"


def package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "missing"


def runtime_identity() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "pytest": package_version("pytest"),
        "coverage": package_version("coverage"),
    }


def file_content_hashes(root: Path, test_files: Sequence[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for relative in sorted(set(test_files)):
        path = root / relative
        values[relative] = sha256_file(path) if path.is_file() else "missing"
    return values


def build_attempt_fingerprint(
    *,
    root: Path,
    command: Sequence[str],
    timeout_seconds: int,
    test_files: Sequence[str],
    marker_expression: str,
    revision: str | None = None,
) -> tuple[str, dict[str, Any]]:
    identity = {
        "revision_sha": revision or revision_sha(root),
        "command": list(command),
        "timeout_seconds": timeout_seconds,
        "marker_expression": marker_expression,
        "test_file_hashes": file_content_hashes(root, test_files),
        "runtime": runtime_identity(),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest(), identity


@dataclass
class ExecutionBudget:
    overall_seconds: int
    packaging_reserve_seconds: int
    started_monotonic: float

    @classmethod
    def start(cls, overall_seconds: int, packaging_reserve_seconds: int) -> "ExecutionBudget":
        if overall_seconds < 1:
            raise ValueError("overall_seconds must be at least 1")
        if packaging_reserve_seconds < 0:
            raise ValueError("packaging_reserve_seconds cannot be negative")
        if packaging_reserve_seconds >= overall_seconds:
            packaging_reserve_seconds = max(1, overall_seconds // 5)
        return cls(overall_seconds, packaging_reserve_seconds, time.monotonic())

    @property
    def elapsed_seconds(self) -> float:
        return max(0.0, time.monotonic() - self.started_monotonic)

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.overall_seconds - self.elapsed_seconds)

    @property
    def execution_seconds_remaining(self) -> float:
        return max(0.0, self.remaining_seconds - self.packaging_reserve_seconds)

    def can_start(self, timeout_seconds: int) -> bool:
        return self.execution_seconds_remaining >= max(1, timeout_seconds)

    def snapshot(self) -> dict[str, Any]:
        return {
            "overall_budget_seconds": self.overall_seconds,
            "packaging_reserve_seconds": self.packaging_reserve_seconds,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "remaining_seconds": round(self.remaining_seconds, 3),
            "execution_seconds_remaining": round(self.execution_seconds_remaining, 3),
            "budget_exhausted": self.execution_seconds_remaining < 1,
        }


class ProgressJournal:
    """Atomic terminal progress and deterministic attempt-cache authority."""

    def __init__(
        self,
        *,
        output_dir: Path,
        revision: str,
        plan_fingerprint: str,
        resume: bool,
        budget: ExecutionBudget,
    ) -> None:
        self.output_dir = output_dir
        self.progress_path = output_dir / "terminal-progress.json"
        self.resume_path = output_dir / "resume-manifest.json"
        self.cache_dir = output_dir / "terminal-isolation" / "attempt-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        existing = load_json(self.progress_path) if resume else {}
        compatible = (
            existing.get("revision_sha") == revision
            and existing.get("plan_fingerprint") == plan_fingerprint
        )
        if compatible:
            self.payload = existing
        else:
            self.payload = {
                "schema_version": "prd11.0r/execution-7/terminal-progress/v1",
                "prd_id": PRD_ID,
                "remediation_id": REMEDIATION_ID,
                "revision_sha": revision,
                "plan_fingerprint": plan_fingerprint,
                "started_at": utc_now(),
                "updated_at": utc_now(),
                "completed_file_attempt_ids": [],
                "completed_collect_attempt_ids": [],
                "completed_node_attempt_ids": [],
                "reused_attempt_ids": [],
                "pending_leaf_ids": [],
                "pending_file_ids": [],
                "pending_nodeids": [],
                "terminal_failed_nodeids": [],
                "terminal_error_nodeids": [],
                "terminal_timeout_nodeids": [],
                "terminal_green_nodeids": [],
                "pending_due_to_budget": [],
                "attempt_fingerprints": {},
                "budget_exhausted": False,
                "resume_supported": True,
            }
        self.budget = budget
        self.write()

    def cache_path(self, fingerprint: str) -> Path:
        return self.cache_dir / f"{fingerprint}.json"

    def load_cached(self, fingerprint: str) -> dict[str, Any]:
        return load_json(self.cache_path(fingerprint))

    def record_attempt(
        self,
        *,
        kind: str,
        attempt_id: str,
        fingerprint: str,
        identity: dict[str, Any],
        result: dict[str, Any],
        reused: bool,
    ) -> None:
        result = dict(result)
        result["attempt_fingerprint"] = fingerprint
        result["attempt_identity"] = identity
        atomic_write_json(self.cache_path(fingerprint), result)
        key = {
            "file": "completed_file_attempt_ids",
            "collect": "completed_collect_attempt_ids",
            "node": "completed_node_attempt_ids",
        }[kind]
        values = set(self.payload.get(key, []))
        values.add(attempt_id)
        self.payload[key] = sorted(values)
        if reused:
            reused_values = set(self.payload.get("reused_attempt_ids", []))
            reused_values.add(attempt_id)
            self.payload["reused_attempt_ids"] = sorted(reused_values)
        self.payload.setdefault("attempt_fingerprints", {})[attempt_id] = fingerprint
        self.write()

    def set_pending(
        self,
        *,
        leaf_ids: Sequence[str] = (),
        file_ids: Sequence[str] = (),
        nodeids: Sequence[str] = (),
        budget_items: Sequence[str] = (),
    ) -> None:
        self.payload["pending_leaf_ids"] = sorted(set(leaf_ids))
        self.payload["pending_file_ids"] = sorted(set(file_ids))
        self.payload["pending_nodeids"] = sorted(set(nodeids))
        self.payload["pending_due_to_budget"] = sorted(set(budget_items))
        self.payload["budget_exhausted"] = bool(budget_items)
        self.write()

    def set_outcomes(
        self,
        *,
        failed: Sequence[str],
        errors: Sequence[str],
        timed_out: Sequence[str],
        green: Sequence[str],
    ) -> None:
        self.payload["terminal_failed_nodeids"] = sorted(set(failed))
        self.payload["terminal_error_nodeids"] = sorted(set(errors))
        self.payload["terminal_timeout_nodeids"] = sorted(set(timed_out))
        self.payload["terminal_green_nodeids"] = sorted(set(green))
        self.write()

    def write(self) -> None:
        self.payload["updated_at"] = utc_now()
        self.payload["budget"] = self.budget.snapshot()
        atomic_write_json(self.progress_path, self.payload)
        manifest = {
            "schema_version": "prd11.0r/execution-7/terminal-resume/v1",
            "prd_id": PRD_ID,
            "remediation_id": REMEDIATION_ID,
            "revision_sha": self.payload.get("revision_sha"),
            "plan_fingerprint": self.payload.get("plan_fingerprint"),
            "resume_supported": True,
            "attempt_fingerprints": self.payload.get("attempt_fingerprints", {}),
            "completed_attempt_count": sum(
                len(self.payload.get(key, []))
                for key in (
                    "completed_file_attempt_ids",
                    "completed_collect_attempt_ids",
                    "completed_node_attempt_ids",
                )
            ),
            "reused_attempt_count": len(self.payload.get("reused_attempt_ids", [])),
            "pending_leaf_ids": self.payload.get("pending_leaf_ids", []),
            "pending_file_ids": self.payload.get("pending_file_ids", []),
            "pending_nodeids": self.payload.get("pending_nodeids", []),
            "budget_exhausted": self.payload.get("budget_exhausted", False),
            "updated_at": self.payload.get("updated_at"),
        }
        atomic_write_json(self.resume_path, manifest)


def package_terminal_artifacts(output_dir: Path) -> dict[str, Any]:
    """Package resumable terminal evidence without recursively archiving itself."""
    archive_path = output_dir / "terminal-isolation-package.tar.gz"
    checksum_path = output_dir / "terminal-isolation-package.tar.gz.sha256"
    temporary = archive_path.with_name(f".{archive_path.name}.tmp")
    include = [
        output_dir / "summary.json",
        output_dir / "terminal-progress.json",
        output_dir / "resume-manifest.json",
        output_dir / "terminal-isolation",
    ]
    with tarfile.open(temporary, "w:gz") as archive:
        for path in include:
            if path.exists():
                archive.add(path, arcname=path.relative_to(output_dir))
    temporary.replace(archive_path)
    digest = sha256_file(archive_path)
    checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    return {
        "archive": str(archive_path),
        "checksum": str(checksum_path),
        "sha256": digest,
        "archive_created": archive_path.is_file(),
        "checksum_created": checksum_path.is_file(),
    }
