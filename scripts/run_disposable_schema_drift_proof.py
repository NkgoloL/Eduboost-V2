#!/usr/bin/env python3
"""Run guarded disposable DB schema-drift proof commands."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "release" / "schema_drift_disposable_latest.json"
DEFAULT_MARKDOWN = REPO_ROOT / "docs" / "release" / "schema_drift_disposable_latest.md"


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    return_code: int
    output: str
    passed: bool


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _db_url_is_disposable(url: str) -> bool:
    lowered = url.lower()
    return (
        "sqlite" in lowered
        or "test" in lowered
        or "eduboost_test" in lowered
        or re.search(r"[/_]test(?:[/?#]|$)", lowered) is not None
    )


def _db_url_has_placeholder_credentials(url: str) -> bool:
    lowered = url.lower()
    return any(
        token in lowered
        for token in (
            "://user:pass@",
            "://username:password@",
            "://postgres:postgres@",
            "://test:test@",
            ":changeme@",
            ":change_me@",
            ":placeholder@",
        )
    )


def _redact_url(url: str) -> str:
    return re.sub(r"://([^:/@]+):([^@]+)@", r"://\1:***@", url)


def _run(name: str, command: list[str]) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return CommandResult(name, command, result.returncode, result.stdout, result.returncode == 0)


def preflight(database_url: str, allow_non_test: bool = False, allow_placeholder_credentials: bool = False) -> list[str]:
    failures: list[str] = []
    if not database_url:
        failures.append("DATABASE_URL is required")
    if database_url and not (_db_url_is_disposable(database_url) or allow_non_test):
        failures.append("DATABASE_URL does not look disposable/test-like")
    if database_url and _db_url_has_placeholder_credentials(database_url) and not allow_placeholder_credentials:
        failures.append("DATABASE_URL contains placeholder credentials")
    return failures


def build_commands(ignore_consolidation: bool = False) -> list[tuple[str, list[str]]]:
    commands = [
        ("migration_evidence_capture", [sys.executable, "scripts/capture_migration_evidence.py"]),
        ("migration_evidence_check", [sys.executable, "scripts/capture_migration_evidence.py", "--validate", "--require-pass"]),
    ]
    drift_cmd = [sys.executable, "scripts/compare_orm_tables_to_database.py", "--require-db", "--fail-on-drift"]
    if ignore_consolidation:
        drift_cmd.append("--ignore-consolidation-tables")
    commands.append(("schema_drift_db", drift_cmd))
    return commands


def write_outputs(payload: dict[str, object], json_path: Path = DEFAULT_OUTPUT, markdown_path: Path = DEFAULT_MARKDOWN) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Schema Drift Disposable DB Latest Proof",
        "",
        f"- Captured at: `{payload['captured_at']}`",
        f"- Database URL: `{payload['database_url_redacted']}`",
        f"- Passed: `{payload['passed']}`",
        "",
        "| Step | Return code | Passed |",
        "|---|---:|---|",
    ]
    for result in payload["results"]:  # type: ignore[index]
        lines.append(f"| {result['name']} | {result['return_code']} | {result['passed']} |")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_proof(database_url: str, *, dry_run: bool = False, allow_non_test: bool = False, allow_placeholder_credentials: bool = False, ignore_consolidation: bool = False) -> dict[str, object]:
    failures = preflight(database_url, allow_non_test, allow_placeholder_credentials)
    if failures:
        raise SystemExit("Schema drift disposable proof preflight failed: " + "; ".join(failures))

    if dry_run:
        results = [CommandResult(name, command, 0, "dry-run", True) for name, command in build_commands(ignore_consolidation)]
    else:
        results = [_run(name, command) for name, command in build_commands(ignore_consolidation)]

    return {
        "captured_at": _utc_now(),
        "database_url_redacted": _redact_url(database_url),
        "dry_run": dry_run,
        "passed": all(result.passed for result in results),
        "results": [asdict(result) for result in results],
    }


def validate(path: Path = DEFAULT_OUTPUT, require_pass: bool = False) -> bool:
    if not path.exists():
        print(f"- FAIL [file] {path}: missing")
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"captured_at", "database_url_redacted", "passed", "results"}
    missing = sorted(required - set(payload))
    if missing:
        print(f"- FAIL [json] {path}: missing {missing}")
        return False
    if require_pass and payload.get("passed") is not True:
        print(f"- FAIL [json] {path}: disposable proof exists but passed=false")
        return False
    print(f"- PASS [json] {path}: disposable proof present, passed={payload.get('passed')}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-non-test-db", action="store_true")
    parser.add_argument("--allow-placeholder-credentials", action="store_true")
    parser.add_argument("--ignore-consolidation-tables", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    if args.validate:
        return 0 if validate(require_pass=args.require_pass) else 1

    payload = run_proof(
        args.database_url,
        dry_run=args.dry_run,
        allow_non_test=args.allow_non_test_db,
        allow_placeholder_credentials=args.allow_placeholder_credentials,
        ignore_consolidation=args.ignore_consolidation_tables,
    )
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
