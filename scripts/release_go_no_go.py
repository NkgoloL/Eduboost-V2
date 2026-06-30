from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
OUT_JSON = ROOT / "docs/release/release_go_no_go_status.json"
OUT_MD = ROOT / "docs/release/release_go_no_go_status.md"
DECISION_LOG = ROOT / "docs/release/release_decision_log.md"

GO_STATUSES = {"runtime-passing", "integration-passing", "production-ready"}
EXTERNAL_PENDING_STATUSES = {"external-blocked", "not-started", "not-proven", "contradicted", "static-passing"}


@dataclass(frozen=True)
class ReleaseFinding:
    id: str
    title: str
    severity: str
    gate: str
    proof_status: str
    blocks_beta: bool
    external_dependency: bool
    evidence_file: str | None
    closure_blocker: str | None
    go_eligible: bool
    reason: str


@dataclass(frozen=True)
class ReleaseGoNoGoStatus:
    generated_at: str
    current_commit: str
    decision: str
    beta_blocker_count: int
    engineering_blocker_count: int
    external_blocker_count: int
    ci_blocker_count: int
    findings: list[ReleaseFinding]
    blockers: list[str]
    required_next_actions: list[str]


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


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "~", ""}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_registry_items() -> list[dict[str, Any]]:
    if not REGISTRY.exists():
        return []
    lines = REGISTRY.read_text(encoding="utf-8").splitlines()
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or stripped == "findings:":
            continue
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            rest = stripped[2:].strip()
            if rest and ":" in rest:
                key, _, value = rest.partition(":")
                current[key.strip()] = _parse_scalar(value)
            continue
        if current is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current[key.strip()] = _parse_scalar(value)
    if current:
        items.append(current)
    return items


def _file_exists(path: str | None) -> bool:
    if not path:
        return False
    return (ROOT / path).exists()


def _go_reason(item: dict[str, Any]) -> tuple[bool, str]:
    status = str(item.get("proof_status") or "not-started")
    blocks_beta = bool(item.get("blocks_beta"))
    external = bool(item.get("external_dependency"))
    evidence_file = item.get("evidence_file")
    item_id = str(item.get("id") or "")

    if not blocks_beta:
        return True, "non-beta-blocking item"

    if item_id == "CI-001":
        if status == "external-blocked":
            return False, "remote CI run URL not attached"
        if status not in GO_STATUSES:
            return False, f"CI status is {status}"
        return True, "CI evidence accepted by registry"

    if external:
        if status != "production-ready":
            return False, "external approval remains incomplete"
        if not _file_exists(evidence_file):
            return False, "external approval evidence file missing"
        return True, "external approval evidence complete"

    if status not in GO_STATUSES:
        return False, f"proof_status is {status}"
    if not _file_exists(evidence_file):
        return False, "evidence file missing"
    return True, "beta-blocking evidence is present"


def build_status() -> ReleaseGoNoGoStatus:
    items = load_registry_items()
    findings: list[ReleaseFinding] = []
    blockers: list[str] = []

    for item in items:
        eligible, reason = _go_reason(item)
        finding = ReleaseFinding(
            id=str(item.get("id") or "UNKNOWN"),
            title=str(item.get("title") or ""),
            severity=str(item.get("severity") or ""),
            gate=str(item.get("gate") or ""),
            proof_status=str(item.get("proof_status") or "not-started"),
            blocks_beta=bool(item.get("blocks_beta")),
            external_dependency=bool(item.get("external_dependency")),
            evidence_file=item.get("evidence_file"),
            closure_blocker=item.get("closure_blocker"),
            go_eligible=eligible,
            reason=reason,
        )
        findings.append(finding)
        if finding.blocks_beta and not finding.go_eligible:
            blockers.append(f"{finding.id}: {finding.reason}")

    beta_blockers = [f for f in findings if f.blocks_beta and not f.go_eligible]
    engineering_blockers = [f for f in beta_blockers if not f.external_dependency and f.id != "CI-001"]
    external_blockers = [f for f in beta_blockers if f.external_dependency]
    ci_blockers = [f for f in beta_blockers if f.id == "CI-001"]

    actions: list[str] = []
    if ci_blockers:
        actions.append("Attach a passing GitHub Actions run URL for CI-001.")
    if external_blockers:
        actions.append("Complete external approval files for legal, security, content, and staging gates.")
    if engineering_blockers:
        actions.append("Resolve remaining beta-blocking engineering evidence items.")
    if not actions:
        actions.append("Review release_decision_log.md and obtain explicit release-owner sign-off.")

    return ReleaseGoNoGoStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        decision="GO" if not beta_blockers else "NO-GO",
        beta_blocker_count=len(beta_blockers),
        engineering_blocker_count=len(engineering_blockers),
        external_blocker_count=len(external_blockers),
        ci_blocker_count=len(ci_blockers),
        findings=sorted(findings, key=lambda f: (not f.blocks_beta, f.gate, f.id)),
        blockers=blockers,
        required_next_actions=actions,
    )


def write_decision_log_template() -> None:
    if DECISION_LOG.exists() and "RELEASE-GO-001" in DECISION_LOG.read_text(encoding="utf-8"):
        return
    DECISION_LOG.write_text(
        "\n".join(
            [
                "# Release Decision Log",
                "",
                "**Item:** RELEASE-GO-001",
                "",
                "**Decision:** NO-GO",
                "",
                "**Decision maker:** pending",
                "",
                "**Date:** pending",
                "",
                "**Commit SHA:** pending",
                "",
                "**Basis:** pending",
                "",
                "## Required before GO",
                "",
                "- `docs/release/release_go_no_go_status.md` reports `GO`.",
                "- CI-001 has a passing GitHub Actions run URL.",
                "- Legal, security, content, and staging approvals are complete.",
                "- No beta-blocking item remains incomplete in `evidence_status_registry.yml`.",
                "",
                "## No false-closure rule",
                "",
                "This document is not a release approval while decision metadata remains pending or while the generated release status is `NO-GO`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_status() -> ReleaseGoNoGoStatus:
    write_decision_log_template()
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Release Go/No-Go Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Decision:** `{status.decision}`",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Beta blockers | {status.beta_blocker_count} |",
        f"| Engineering blockers | {status.engineering_blocker_count} |",
        f"| CI blockers | {status.ci_blocker_count} |",
        f"| External blockers | {status.external_blocker_count} |",
        "",
        "## Beta-blocking findings",
        "",
        "| ID | Status | External | Eligible | Reason | Evidence |",
        "|---|---|---:|---:|---|---|",
    ]
    for finding in status.findings:
        if not finding.blocks_beta:
            continue
        lines.append(
            f"| `{finding.id}` | `{finding.proof_status}` | {finding.external_dependency} | "
            f"{finding.go_eligible} | {finding.reason} | `{finding.evidence_file or '-'}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Required next actions", ""])
    lines.extend(f"- {action}" for action in status.required_next_actions)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report is release-owner decision support. It does not approve release by itself.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


__all__ = ["ReleaseFinding", "ReleaseGoNoGoStatus", "build_status", "write_status"]
