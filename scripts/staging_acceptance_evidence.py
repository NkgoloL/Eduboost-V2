from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_FILE = ROOT / "docs/release/staging_smoke_evidence.md"
STATUS_JSON = ROOT / "docs/release/staging_acceptance_status.json"
STATUS_MD = ROOT / "docs/release/staging_acceptance_status.md"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}

REQUIRED_FIELDS = [
    "Environment",
    "Staging URL",
    "Commit SHA",
    "GitHub Actions run URL",
    "Smoke command",
    "Smoke result",
    "Health endpoint result",
    "API smoke result",
    "Database migration status",
    "Verified by",
    "Date verified",
]


@dataclass(frozen=True)
class StagingField:
    name: str
    value: str
    valid: bool
    reason: str


@dataclass(frozen=True)
class StagingAcceptanceStatus:
    generated_at: str
    current_commit: str
    evidence_file: str
    status: str
    fields: list[StagingField]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip().strip("`").strip()

    # Support table format as fallback.
    table_pattern = rf"\|\s*{re.escape(name)}\s*\|\s*([^|]+)\|"
    match = re.search(table_pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip().strip("`").strip()
    return ""


def template() -> str:
    return "\n".join(
        [
            "# Staging Smoke Evidence",
            "",
            "**Item:** STAGING-001",
            "",
            "**Environment:** pending",
            "",
            "**Staging URL:** pending",
            "",
            "**Commit SHA:** pending",
            "",
            "**GitHub Actions run URL:** pending",
            "",
            "**Smoke command:** pending",
            "",
            "**Smoke result:** pending",
            "",
            "**Health endpoint result:** pending",
            "",
            "**API smoke result:** pending",
            "",
            "**Database migration status:** pending",
            "",
            "**Verified by:** pending",
            "",
            "**Date verified:** pending",
            "",
            "## Required attachments or links",
            "",
            "- Staging deployment URL.",
            "- Passing GitHub Actions run URL for the deployed commit.",
            "- Health/readiness smoke output.",
            "- API smoke output.",
            "- Migration status output.",
            "",
            "## No false-closure rule",
            "",
            "This file is not staging acceptance while any required field remains pending or while the smoke result is not `pass`.",
            "",
        ]
    )


def write_template() -> None:
    if EVIDENCE_FILE.exists() and "**Item:** STAGING-001" in EVIDENCE_FILE.read_text(encoding="utf-8"):
        return
    EVIDENCE_FILE.write_text(template(), encoding="utf-8")


def _validate_field(name: str, value: str) -> StagingField:
    if _is_pending(value):
        return StagingField(name=name, value=value, valid=False, reason="pending")

    if name in {"Staging URL", "GitHub Actions run URL"} and not _is_url(value):
        return StagingField(name=name, value=value, valid=False, reason="must be URL")

    if name == "GitHub Actions run URL" and "/actions/runs/" not in value:
        return StagingField(name=name, value=value, valid=False, reason="must be GitHub Actions run URL")

    if name in {"Smoke result", "Health endpoint result", "API smoke result", "Database migration status"}:
        normalized = value.strip().lower()
        if normalized not in {"pass", "passed", "green", "ok"}:
            return StagingField(name=name, value=value, valid=False, reason="must be pass/passed/green/ok")

    if name == "Commit SHA":
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", value):
            return StagingField(name=name, value=value, valid=False, reason="must look like git SHA")

    return StagingField(name=name, value=value, valid=True, reason="ok")


def build_status() -> StagingAcceptanceStatus:
    write_template()
    text = EVIDENCE_FILE.read_text(encoding="utf-8")
    fields = [_validate_field(name, _field(text, name)) for name in REQUIRED_FIELDS]
    blockers = [f"{field.name}: {field.reason}" for field in fields if not field.valid]

    return StagingAcceptanceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        evidence_file="docs/release/staging_smoke_evidence.md",
        status="staging-accepted" if not blockers else "external-blocked",
        fields=fields,
        blockers=blockers,
    )


def write_status() -> StagingAcceptanceStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Staging Acceptance Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Field | Value | Valid | Reason |",
        "|---|---|---:|---|",
    ]
    for field in status.fields:
        lines.append(f"| `{field.name}` | `{field.value}` | {field.valid} | {field.reason} |")

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This status is accepted only when actual staging smoke evidence is attached. Local checks do not satisfy STAGING-001.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def registry_staging_status() -> str | None:
    if not REGISTRY.exists():
        return None
    text = REGISTRY.read_text(encoding="utf-8")
    marker = "id: STAGING-001"
    index = text.find(marker)
    if index < 0:
        return None
    next_index = text.find("\n  - id:", index + 1)
    block = text[index:] if next_index < 0 else text[index:next_index]
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("proof_status:"):
            return stripped.split(":", 1)[1].strip()
    return None


__all__ = [
    "REQUIRED_FIELDS",
    "StagingAcceptanceStatus",
    "StagingField",
    "build_status",
    "registry_staging_status",
    "template",
    "write_status",
    "write_template",
]
