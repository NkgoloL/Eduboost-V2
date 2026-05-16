#!/usr/bin/env python3
"""Capture Alembic/database migration evidence for release readiness."""
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
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO_ROOT / "docs" / "release" / "migration_latest.json"
DEFAULT_MARKDOWN = REPO_ROOT / "docs" / "release" / "migration_latest.md"
GATE_MARKDOWN = REPO_ROOT / "docs" / "release" / "migration_evidence.md"


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    return_code: int
    stdout: str
    passed: bool


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _redact_database_url(url: str) -> str:
    return re.sub(r"://([^:/@]+):([^@]+)@", r"://\1:***@", url)


def _database_url_has_placeholder_credentials(url: str) -> bool:
    """Return true for documentation/demo credentials that should not run Alembic."""
    lowered = url.lower()
    return any(
        token in lowered
        for token in (
            "://user:pass@",
            "://username:password@",
            "://postgres:postgres@",
            "://test:test@",
            "://change_me:",
            ":change_me@",
            ":changeme@",
            ":placeholder@",
        )
    )


def _database_url_is_disposable(url: str) -> bool:
    lower = url.lower()
    return (
        "sqlite" in lower
        or "test" in lower
        or "eduboost_test" in lower
        or re.search(r"[/_]test(?:[/?#]|$)", lower) is not None
    )


def _run_command(name: str, command: list[str], env: dict[str, str]) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return CommandResult(
        name=name,
        command=command,
        return_code=result.returncode,
        stdout=result.stdout,
        passed=result.returncode == 0,
    )


def build_plan(include_downgrade: bool = False) -> list[tuple[str, list[str]]]:
    commands = [
        ("alembic_current_before", ["alembic", "current"]),
        ("alembic_upgrade_head", ["alembic", "upgrade", "head"]),
        ("alembic_current_after", ["alembic", "current"]),
    ]

    # Optional local schema checks if present in this repository.
    optional_scripts = [
        ("migration_graph_check", "scripts/verify_migration_graph.py"),
        ("schema_integrity_check", "scripts/validate_schema_integrity.py"),
    ]
    for name, script in optional_scripts:
        if (REPO_ROOT / script).exists():
            commands.append((name, [sys.executable, script]))

    if include_downgrade:
        commands.append(("alembic_downgrade_minus_one", ["alembic", "downgrade", "-1"]))
        commands.append(("alembic_upgrade_head_after_downgrade", ["alembic", "upgrade", "head"]))

    return commands


def capture(include_downgrade: bool = False, allow_non_test_db: bool = False, allow_placeholder_credentials: bool = False) -> dict[str, Any]:
    env = os.environ.copy()
    database_url = env.get("DATABASE_URL", "")

    if not database_url:
        raise SystemExit("DATABASE_URL is required for migration evidence capture")

    if _database_url_has_placeholder_credentials(database_url) and not allow_placeholder_credentials:
        raise SystemExit(
            "Refusing migration evidence capture because DATABASE_URL contains placeholder/demo credentials. "
            "Use a real disposable database credential, or pass --allow-placeholder-credentials for tooling-debug only."
        )

    if not (_database_url_is_disposable(database_url) or allow_non_test_db):
        raise SystemExit(
            "Refusing migration evidence capture because DATABASE_URL does not look disposable/test-like. "
            "Use a test DB, or set EDUBOOST_ALLOW_MIGRATION_EVIDENCE_CAPTURE=1 after manual verification."
        )

    command_results = [_run_command(name, command, env) for name, command in build_plan(include_downgrade)]
    passed = all(result.passed for result in command_results)

    return {
        "captured_at": _utc_now(),
        "database_url_redacted": _redact_database_url(database_url),
        "include_downgrade": include_downgrade,
        "passed": passed,
        "results": [asdict(result) for result in command_results],
    }


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, markdown_path: Path = DEFAULT_MARKDOWN) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "passed" if payload["passed"] else "failed"
    lines = [
        "# Database Migration Latest Run",
        "",
        f"**Status:** migration evidence {status}",
        f"<!-- Status: migration evidence {status} -->",
        "",
        f"- Captured at: `{payload['captured_at']}`",
        f"- Database URL: `{payload['database_url_redacted']}`",
        f"- Include downgrade: `{payload['include_downgrade']}`",
        f"- JSON evidence: `{json_path.as_posix()}`",
        "",
        "| Step | Command | Return code | Passed |",
        "|---|---|---:|---|",
    ]

    for result in payload["results"]:
        command = " ".join(result["command"]).replace("|", "\\|")
        lines.append(
            f"| {result['name']} | `{command}` | {result['return_code']} | {'yes' if result['passed'] else 'no'} |"
        )

    lines.extend(["", "## Command output", ""])
    for result in payload["results"]:
        lines.extend(
            [
                f"### {result['name']}",
                "",
                "```text",
                result["stdout"].rstrip(),
                "```",
                "",
            ]
        )

    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def ensure_gate_template(path: Path = GATE_MARKDOWN) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and "Status: pending runtime execution" in path.read_text(encoding="utf-8"):
        return

    path.write_text(
        """# Database Migration Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

This file is the stable release gate for database migration evidence. It must remain pending until a disposable PostgreSQL migration run is accepted by the release owner.

Latest raw migration output, when available:

- JSON: `docs/release/migration_latest.json`
- Markdown: `docs/release/migration_latest.md`

## Required environment

| Field | Value |
|---|---|
| Database name | TODO |
| Database host | TODO |
| Commit SHA | TODO |
| Alembic head before | TODO |
| Alembic head after | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| `alembic current` before upgrade | known baseline or empty DB | TODO |
| `alembic upgrade head` | succeeds | TODO |
| `alembic current` after upgrade | at repository head | TODO |
| schema integrity check | succeeds | TODO |
| migration graph check | single linear/resolvable head | TODO |
| downgrade/rollback path | succeeds or documented non-downgrade rationale | TODO |

## Command log

```bash
# paste accepted migration evidence commands and output here
```

## Decision

- [ ] Migration proof passed and is accepted for release evidence.
- [ ] Migration proof failed and release is blocked.
""",
        encoding="utf-8",
    )


def validate_payload(path: Path = DEFAULT_JSON, require_pass: bool = False) -> bool:
    if not path.exists():
        print(f"- FAIL [file] {path}: missing")
        return False

    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"captured_at", "database_url_redacted", "passed", "results"}
    missing = sorted(required - set(payload))
    if missing:
        print(f"- FAIL [json] {path}: missing {missing}")
        return False

    if not isinstance(payload["results"], list) or not payload["results"]:
        print(f"- FAIL [json] {path}: no migration command results")
        return False

    if require_pass and payload.get("passed") is not True:
        print(f"- FAIL [json] {path}: migration evidence exists but passed=false")
        return False

    print(f"- PASS [json] {path}: {len(payload['results'])} migration result(s), passed={payload['passed']}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-downgrade", action="store_true", help="Also run alembic downgrade -1 and upgrade head.")
    parser.add_argument("--validate", action="store_true", help="Validate existing migration_latest.json.")
    parser.add_argument("--require-pass", action="store_true", help="When validating, fail unless migration evidence passed.")
    parser.add_argument("--allow-placeholder-credentials", action="store_true", help="Allow using placeholder/demo credentials (for debug only).")
    args = parser.parse_args(argv)

    ensure_gate_template()

    if args.validate:
        return 0 if validate_payload(require_pass=args.require_pass) else 1

    allow_non_test = os.getenv("EDUBOOST_ALLOW_MIGRATION_EVIDENCE_CAPTURE") == "1"
    payload = capture(include_downgrade=args.include_downgrade, allow_non_test_db=allow_non_test, allow_placeholder_credentials=args.allow_placeholder_credentials)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
