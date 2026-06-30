from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs/release"
REGISTRY = RELEASE / "evidence_status_registry.yml"

OUT_JSON = RELEASE / "audit_baseline_refresh_status.json"
OUT_MD = RELEASE / "audit_baseline_refresh_status.md"
RELEASE_GO_JSON = RELEASE / "release_go_no_go_status.json"
RELEASE_GO_MD = RELEASE / "release_go_no_go_status.md"

FINAL_BETA_JSON = RELEASE / "final_beta_gate_refresh.json"
FINAL_BETA_MD = RELEASE / "final_beta_gate_refresh.md"

ACCEPTED_EVIDENCE_MARKERS = {
    "AUTH-REFRESH-DB-EVIDENCE-001": (
        RELEASE / "auth_refresh_db_evidence_status.json",
        "auth-refresh-db-evidence-accepted",
    ),
    "POPIA-001": (
        RELEASE / "popia_response_contract_no_skip_status.json",
        "popia-response-contract-no-skip-passing",
    ),
    "CI-001": (
        RELEASE / "ci_evidence_status.json",
        "ci-evidence-accepted",
    ),
    "EVID-001": (
        RELEASE / "ci_evidence_status.json",
        "ci-evidence-accepted",
    ),
    "STAGING-001": (
        RELEASE / "staging_smoke_evidence_status.json",
        "staging-smoke-evidence-accepted",
    ),
    "DIAG-001": (
        RELEASE / "diag_deep_health_runtime_status.json",
        "diag-deep-health-runtime-accepted",
    ),
}

SURFACE_PATHS = {
    "final_beta_gate_refresh": FINAL_BETA_JSON,
    "release_go_no_go_status": RELEASE_GO_JSON,
    "ci_evidence": RELEASE / "ci_evidence_status.json",
    "ci_run_evidence": RELEASE / "ci_run_evidence_status.json",
    "external_approval": RELEASE / "external_approval_status.json",
    "approval_evidence": RELEASE / "approval_evidence_status.json",
    "staging_smoke_evidence": RELEASE / "staging_smoke_evidence_status.json",
    "staging_acceptance": RELEASE / "staging_acceptance_status.json",
    "auth_refresh_db_evidence": RELEASE / "auth_refresh_db_evidence_status.json",
    "popia_response_contract_no_skip": RELEASE / "popia_response_contract_no_skip_status.json",
    "diag_deep_health_runtime": RELEASE / "diag_deep_health_runtime_status.json",
    "live_db_transaction_evidence": RELEASE / "live_db_transaction_evidence_status.json",
    "beta_blocker_burndown": RELEASE / "beta_blocker_burndown_plan.json",
    "docs_inventory": ROOT / "docs/docs_inventory.json",
}


@dataclass(frozen=True)
class CommandResult:
    command: str
    return_code: int
    output_excerpt: str


@dataclass(frozen=True)
class SurfaceStatus:
    name: str
    path: str
    exists: bool
    status: str
    decision: str
    commit: str
    stale: bool


@dataclass(frozen=True)
class EvidenceMarkerStatus:
    id: str
    path: str
    expected_marker: str
    exists: bool
    accepted: bool


@dataclass(frozen=True)
class AuditBaselineRefreshStatus:
    generated_at: str
    current_commit: str
    current_branch: str
    status: str
    beta_decision: str
    beta_blocker_count: int | None
    commands: list[CommandResult]
    surfaces: list[SurfaceStatus]
    accepted_evidence_markers: list[EvidenceMarkerStatus]
    remaining_beta_blockers: list[str]
    blockers: list[str]


def _run(command: list[str]) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return CommandResult(
        command=" ".join(command),
        return_code=result.returncode,
        output_excerpt=result.stdout[-5000:],
    )


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


def current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _walk_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            values.extend(_walk_values(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(_walk_values(item))
    else:
        values.append(str(value))
    return values


def _surface_status(name: str, path: Path, current_sha: str) -> SurfaceStatus:
    data = _load_json(path)
    values = _walk_values(data)

    status = str(
        data.get("status")
        or data.get("beta_decision")
        or data.get("decision")
        or data.get("release_decision")
        or ""
    )
    decision = str(
        data.get("beta_decision")
        or data.get("decision")
        or data.get("release_decision")
        or ""
    )
    commit = str(
        data.get("current_commit")
        or data.get("commit")
        or data.get("head_sha")
        or data.get("sha")
        or ""
    )

    if not commit:
        for value in values:
            if re.fullmatch(r"[0-9a-f]{40}", value.strip()):
                commit = value.strip()
                break

    stale = bool(commit and commit != current_sha)

    return SurfaceStatus(
        name=name,
        path=(str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)),
        exists=path.exists(),
        status=status,
        decision=decision,
        commit=commit,
        stale=stale,
    )


def _evidence_marker_status(
    item_id: str,
    path: Path,
    expected_marker: str,
) -> EvidenceMarkerStatus:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return EvidenceMarkerStatus(
        id=item_id,
        path=(str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)),
        expected_marker=expected_marker,
        exists=path.exists(),
        accepted=expected_marker in text,
    )


def _registry_entry(text: str, item_id: str) -> str:
    match = re.search(
        rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)",
        text,
    )
    return match.group(1) if match else ""


def remaining_beta_blockers_from_registry() -> list[str]:
    if not REGISTRY.exists():
        return []

    text = REGISTRY.read_text(encoding="utf-8")
    blockers: list[str] = []

    for match in re.finditer(r"(?m)^  - id:\s*([A-Z0-9-]+)", text):
        item_id = match.group(1)
        entry = _registry_entry(text, item_id)
        if "blocks_beta: true" in entry:
            blockers.append(item_id)

    return blockers


def _final_beta_data() -> dict[str, Any]:
    return _load_json(FINAL_BETA_JSON)


def _write_release_go_no_go_from_final(current_sha: str) -> None:
    final = _final_beta_data()
    decision = str(final.get("beta_decision") or final.get("decision") or "NO-GO")
    blocker_count = final.get("beta_blocker_count")
    blockers = remaining_beta_blockers_from_registry()

    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "current_commit": current_sha,
        "status": decision,
        "beta_decision": decision,
        "beta_blocker_count": blocker_count if blocker_count is not None else len(blockers),
        "remaining_beta_blockers": blockers,
        "source": "docs/release/final_beta_gate_refresh.json",
        "no_false_closure": [
            "This status is derived from the current final beta gate refresh.",
            "It does not approve beta release.",
            "Accepted evidence is preserved; missing external/runtime evidence remains blocking.",
        ],
    }
    RELEASE_GO_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")

    lines = [
        "# Release Go/No-Go Status",
        "",
        f"Generated at: `{data['generated_at']}`",
        f"Commit: `{current_sha}`",
        "",
        f"**Beta decision:** `{decision}`",
        f"**Beta blocker count:** `{data['beta_blocker_count']}`",
        "",
        "## Remaining beta blockers",
        "",
    ]

    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This status is derived from the current final beta gate refresh.",
            "- This status does not approve beta release by itself.",
            "- Stale external evidence must not be upgraded to accepted evidence.",
            "",
        ]
    )

    RELEASE_GO_MD.write_text("\n".join(lines), encoding="utf-8")


def _refresh_final_gate() -> CommandResult:
    # Prefer the project wrapper because it encodes the current release-gate policy.
    makefile = ROOT / "Makefile"
    if makefile.exists() and "final-gate-refresh:" in makefile.read_text(encoding="utf-8"):
        return _run(["make", "final-gate-refresh"])

    # Fallback for repos where final_gate_refresh.py is importable but the Make target is absent.
    if (ROOT / "scripts/final_gate_refresh.py").exists():
        return _run(
            [
                "python3",
                "-c",
                "from scripts.final_gate_refresh import write_refresh; r = write_refresh(); print(r.beta_decision)",
            ]
        )

    return CommandResult(
        command="final gate refresh",
        return_code=1,
        output_excerpt="No final-gate-refresh Make target or scripts/final_gate_refresh.py found",
    )


def _refresh_docs_inventory() -> CommandResult:
    if (ROOT / "scripts/docs_inventory.py").exists():
        return _run(["python3", "scripts/docs_inventory.py", "--write"])

    return CommandResult(
        command="docs inventory refresh",
        return_code=0,
        output_excerpt="scripts/docs_inventory.py not present; skipped",
    )


def write_status() -> AuditBaselineRefreshStatus:
    current_sha = current_commit()
    branch = current_branch()
    commands = [
        _refresh_final_gate(),
    ]

    # Rebuild release_go_no_go_status from the just-refreshed final beta gate.
    _write_release_go_no_go_from_final(current_sha)
    commands.append(
        CommandResult(
            command="write release_go_no_go_status from final_beta_gate_refresh",
            return_code=0,
            output_excerpt="release_go_no_go_status.json/md regenerated from current final beta gate",
        )
    )

    commands.append(_refresh_docs_inventory())

    surfaces = [
        _surface_status(name, path, current_sha)
        for name, path in SURFACE_PATHS.items()
    ]

    accepted_markers = [
        _evidence_marker_status(item_id, path, marker)
        for item_id, (path, marker) in ACCEPTED_EVIDENCE_MARKERS.items()
    ]

    final = _final_beta_data()
    beta_decision = str(final.get("beta_decision") or final.get("decision") or "NO-GO")
    raw_count = final.get("beta_blocker_count")
    beta_blocker_count = raw_count if isinstance(raw_count, int) else None
    remaining_blockers = remaining_beta_blockers_from_registry()

    blockers: list[str] = []

    for command in commands:
        if command.return_code != 0:
            blockers.append(f"command failed: {command.command}")

    for surface in surfaces:
        if surface.name in {"final_beta_gate_refresh", "release_go_no_go_status"}:
            if not surface.exists:
                blockers.append(f"required status surface missing: {surface.name}")
            if surface.stale:
                blockers.append(
                    f"required status surface {surface.name} is stale: {surface.commit} != {current_sha}"
                )

    if beta_decision != "NO-GO" and remaining_blockers:
        blockers.append("final gate reports GO while registry still contains beta blockers")

    status = "audit-baseline-refresh-current" if not blockers else "audit-baseline-refresh-needs-attention"

    result = AuditBaselineRefreshStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_sha,
        current_branch=branch,
        status=status,
        beta_decision=beta_decision,
        beta_blocker_count=beta_blocker_count,
        commands=commands,
        surfaces=surfaces,
        accepted_evidence_markers=accepted_markers,
        remaining_beta_blockers=remaining_blockers,
        blockers=blockers,
    )

    OUT_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)

    return result


def _write_markdown(status: AuditBaselineRefreshStatus) -> None:
    lines = [
        "# Audit Baseline Refresh Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        f"Branch: `{status.current_branch}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Beta decision:** `{status.beta_decision}`",
        f"**Beta blocker count:** `{status.beta_blocker_count}`",
        "",
        "## Commands",
        "",
        "| Command | Return code |",
        "|---|---:|",
    ]

    for command in status.commands:
        lines.append(f"| `{command.command}` | {command.return_code} |")

    lines.extend(
        [
            "",
            "## Status surfaces",
            "",
            "| Surface | Exists | Status | Decision | Commit | Stale |",
            "|---|---:|---|---|---|---:|",
        ]
    )

    for surface in status.surfaces:
        lines.append(
            f"| `{surface.name}` | {surface.exists} | `{surface.status}` | `{surface.decision}` | "
            f"`{surface.commit}` | {surface.stale} |"
        )

    lines.extend(
        [
            "",
            "## Accepted evidence marker preservation",
            "",
            "| ID | Evidence file | Marker | Exists | Accepted marker present |",
            "|---|---|---|---:|---:|",
        ]
    )

    for marker in status.accepted_evidence_markers:
        lines.append(
            f"| `{marker.id}` | `{marker.path}` | `{marker.expected_marker}` | "
            f"{marker.exists} | {marker.accepted} |"
        )

    lines.extend(["", "## Remaining beta blockers", ""])
    if status.remaining_beta_blockers:
        lines.extend(f"- `{item_id}`" for item_id in status.remaining_beta_blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This refresh does not close any blocker by itself.",
            "- Accepted evidence is preserved but not fabricated.",
            "- Missing external approval, frontend runtime, JWT, ARQ, lesson auth, scoring, transaction, and operations evidence remains blocking until separately proven.",
            "- Beta remains NO-GO unless the final gate and registry genuinely clear all beta blockers.",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    result = write_status()
    print(result.status)
    print(result.beta_decision)
    print(result.beta_blocker_count)
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
