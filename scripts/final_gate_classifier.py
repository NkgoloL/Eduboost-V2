from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
OUT_JSON = ROOT / "docs/release/final_beta_gate_refresh.json"
OUT_MD = ROOT / "docs/release/final_beta_gate_refresh.md"

ACCEPTED_STATUSES = {"production-ready", "runtime-passing", "integration-passing"}
BLOCKED_STATUSES = {
    "external-blocked",
    "not-proven",
    "blocked",
    "scaffold-only",
    "not_proven",
    "runtime-blocked",
    "external_blocked",
}
ACCEPTED_AUTH_REFRESH_IDS = {
    "AUTH-REFRESH-DB-PROOF-001",
    "AUTH-REFRESH-DB-EVIDENCE-001",
}
BETA_CRITICAL_IDS = {
    "CI-001",
    "LEGAL-001",
    "SEC-001",
    "CONTENT-001",
    "STAGING-001",
}
FALSE_CLOSURE_TOKENS = {
    "skipped",
    "not proof",
    "not-proven",
    "not proven",
    "pending",
    "required",
    "still required",
    "still pending",
    "external-blocked",
    "scaffold",
    "template",
    "placeholder",
    "blocked",
    "not accepted",
    "gap",
    "gaps",
    "remain",
    "remains",
    "live db",
    "staging",
    "production route",
    "full http",
    "redis",
    "approval",
    "sign-off",
    "smoke evidence",
}
NONE_VALUES = {"", "none", "null", "n/a", "false", "no", "-"}


@dataclass(frozen=True)
class RegistryFinding:
    id: str
    title: str
    proof_status: str
    closure_blocker: str
    evidence_file: str
    external_dependency: bool
    registry_blocks_beta: bool
    release_ready: bool
    effective_blocks_beta: bool


@dataclass(frozen=True)
class StatusSurface:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class FinalGateRefresh:
    generated_at: str
    current_commit: str
    beta_decision: str
    beta_blocker_count: int
    surfaces: list[StatusSurface]
    refresh_results: list[StatusSurface]
    beta_critical_findings: list[RegistryFinding]
    non_ready_beta_findings: list[RegistryFinding]
    resolved_non_blocking_findings: list[RegistryFinding]
    required_next_actions: list[str]
    no_false_closure_rules: list[str]
    # Note: keep the canonical fields above. Backward-compatible aliases
    # (e.g. `refresh_results`, `non_ready_beta_findings`, `no_false_closure_rules`)
    # are provided as dataclass fields to ensure the object is directly
    # serializable and compatible with legacy consumers. Do not shadow
    # these names with @property definitions, which breaks dataclass field
    # initialization order.


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


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "on"}


def _norm(value: Any) -> str:
    return str(value or "").strip().strip('"').strip("'")


def _lower(value: Any) -> str:
    return _norm(value).lower()


def _closure_has_blocker(value: Any) -> bool:
    lowered = _lower(value)
    if lowered in NONE_VALUES:
        return False
    return any(token in lowered for token in FALSE_CLOSURE_TOKENS) or bool(lowered)


def release_ready_for(proof_status: str, closure_blocker: str) -> bool:
    status = _lower(proof_status)
    if status in BLOCKED_STATUSES:
        return False
    if "skip" in status or ("not" in status and "proven" in status):
        return False
    if _closure_has_blocker(closure_blocker):
        return False
    return status in ACCEPTED_STATUSES


def _parse_registry_fallback(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    blocks = re.split(r"(?m)^  - id:\s*", text)
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        item: dict[str, Any] = {"id": lines[0].strip()}
        for line in lines[1:]:
            match = re.match(r"\s{4}([A-Za-z0-9_\-]+):\s*(.*)$", line)
            if match:
                item[match.group(1)] = match.group(2).strip()
        findings.append(item)
    return findings


def _load_yaml() -> dict[str, Any]:
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"findings": _parse_registry_fallback(text)}


def registry_findings() -> list[RegistryFinding]:
    data = _load_yaml()
    raw_findings = data.get("findings", [])
    findings: list[RegistryFinding] = []

    if not isinstance(raw_findings, list):
        return findings

    for item in raw_findings:
        if not isinstance(item, dict):
            continue
        proof_status = _norm(item.get("proof_status"))
        closure_blocker = _norm(item.get("closure_blocker"))
        release_ready = release_ready_for(proof_status, closure_blocker)
        registry_blocks_beta = _bool(item.get("blocks_beta"))
        findings.append(
            RegistryFinding(
                id=_norm(item.get("id")),
                title=_norm(item.get("title")),
                proof_status=proof_status,
                closure_blocker=closure_blocker,
                evidence_file=_norm(item.get("evidence_file")),
                external_dependency=_bool(item.get("external_dependency")),
                registry_blocks_beta=registry_blocks_beta,
                release_ready=release_ready,
                effective_blocks_beta=registry_blocks_beta and not release_ready,
            )
        )
    return findings


def _read_json_status(path: Path, keys: tuple[str, ...] = ("status", "beta_decision", "decision")) -> str:
    if not path.exists():
        return "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in keys:
                if key in data:
                    return str(data[key])
    except Exception:
        pass
    return path.stem


def status_surfaces() -> list[StatusSurface]:
    candidates = [
        ("ci_run_evidence", ROOT / "docs/release/ci_run_evidence_status.json"),
        ("external_approval_gate", ROOT / "docs/release/external_approval_status.json"),
        ("approval_evidence", ROOT / "docs/release/approval_evidence_status.json"),
        ("staging_acceptance", ROOT / "docs/release/staging_acceptance_status.json"),
        ("live_db_tx_evidence", ROOT / "docs/release/live_db_transaction_evidence_status.json"),
        ("route_tx_slice_rollup", ROOT / "docs/architecture/route_transaction_slice_rollup.json"),
        ("release_go_no_go", ROOT / "docs/release/release_go_no_go_status.json"),
        ("beta_blocker_burndown", ROOT / "docs/release/beta_blocker_burndown_status.json"),
        ("docs_inventory", ROOT / "docs/docs_inventory.json"),
        ("auth_refresh_db_evidence", ROOT / "docs/release/auth_refresh_db_evidence_status.json"),
    ]
    return [
        StatusSurface(name=name, status="ok" if path.exists() else "missing", detail=_read_json_status(path))
        for name, path in candidates
    ]


def required_action_for(finding: RegistryFinding) -> str:
    if finding.id == "POPIA-001":
        return "Repair POPIA-001 skipped response-contract proof so no skipped tests are counted."
    if finding.id == "CI-001":
        return "Attach accepted GitHub Actions CI evidence for CI-001."
    if finding.id in {"LEGAL-001", "SEC-001", "CONTENT-001"}:
        return f"Attach complete external approval metadata for {finding.id}."
    if finding.id == "STAGING-001":
        return "Attach accepted staging smoke evidence and run URL for STAGING-001."
    if finding.id == "EXT-GATE-001":
        return "Complete all external approval items tracked by EXT-GATE-001."
    if finding.closure_blocker and _lower(finding.closure_blocker) not in NONE_VALUES:
        return f"Resolve {finding.id}: {finding.closure_blocker}."
    return f"Resolve {finding.id}."


def build_refresh() -> FinalGateRefresh:
    findings = registry_findings()
    beta_critical = [finding for finding in findings if finding.effective_blocks_beta]
    resolved = [
        finding
        for finding in findings
        if finding.id in ACCEPTED_AUTH_REFRESH_IDS and finding.release_ready and not finding.effective_blocks_beta
    ]

    required_actions: list[str] = []
    seen: set[str] = set()
    for finding in beta_critical:
        action = required_action_for(finding)
        if action not in seen:
            required_actions.append(action)
            seen.add(action)

    no_false_closure_rules = [
        "Do not mark beta GO while any effective beta-blocking registry item is not release-ready.",
        "Integration-passing with `closure_blocker: none` can be release-ready even when the item had an external dependency.",
        "External-blocked, not-proven, skipped-test, scaffold-only, and unresolved runtime/staging blockers remain beta-blocking.",
    ]

    return FinalGateRefresh(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        beta_decision="GO" if not beta_critical else "NO-GO",
        beta_blocker_count=len(beta_critical),
        surfaces=status_surfaces(),
        refresh_results=status_surfaces(),
        beta_critical_findings=beta_critical,
        non_ready_beta_findings=beta_critical,
        resolved_non_blocking_findings=resolved,
        required_next_actions=required_actions,
        no_false_closure_rules=no_false_closure_rules,
    )


def write_refresh() -> FinalGateRefresh:
    refresh = build_refresh()
    OUT_JSON.write_text(json.dumps(asdict(refresh), indent=2), encoding="utf-8")

    lines = [
        "# Final Beta Gate Refresh",
        "",
        f"Generated at: `{refresh.generated_at}`",
        f"Commit: `{refresh.current_commit}`",
        "",
        f"**Beta decision:** `{refresh.beta_decision}`",
        "",
        f"- Beta blocker count: `{refresh.beta_blocker_count}`",
        "",
        "## Refreshed status surfaces",
        "",
        "| Surface | Status | Detail |",
        "|---|---|---|",
    ]
    for surface in refresh.surfaces:
        lines.append(f"| `{surface.name}` | `{surface.status}` | `{surface.detail}` |")

    lines.extend(
        [
            "",
            "## Beta-critical findings",
            "",
            "| ID | Proof status | External | Evidence | Release-ready | Effective blocks beta | Blocker |",
            "|---|---|---:|---|---:|---:|---|",
        ]
    )
    for finding in refresh.beta_critical_findings:
        lines.append(
            f"| `{finding.id}` | `{finding.proof_status}` | {finding.external_dependency} | "
            f"`{finding.evidence_file}` | {finding.release_ready} | {finding.effective_blocks_beta} | {finding.closure_blocker or 'none'} |"
        )

    lines.extend(
        [
            "",
            "## Resolved non-blocking accepted findings",
            "",
            "| ID | Proof status | External | Release-ready | Registry blocks beta | Effective blocks beta | Blocker |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    if refresh.resolved_non_blocking_findings:
        for finding in refresh.resolved_non_blocking_findings:
            lines.append(
                f"| `{finding.id}` | `{finding.proof_status}` | {finding.external_dependency} | "
                f"{finding.release_ready} | {finding.registry_blocks_beta} | {finding.effective_blocks_beta} | "
                f"{finding.closure_blocker or 'none'} |"
            )
    else:
        lines.append("| `-` | `-` | False | False | False | False | none |")

    lines.extend(["", "## Required next actions", ""])
    if refresh.required_next_actions:
        lines.extend(f"- {action}" for action in refresh.required_next_actions)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- Do not mark beta GO while any effective beta-blocking registry item is not release-ready.",
            "- Integration-passing with `closure_blocker: none` can be release-ready even when the item had an external dependency.",
            "- External-blocked, not-proven, skipped-test, scaffold-only, and unresolved runtime/staging blockers remain beta-blocking.",
            "",
            "## Interpretation",
            "",
            "This is a release-gate refresh report. It does not approve beta release.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return refresh
