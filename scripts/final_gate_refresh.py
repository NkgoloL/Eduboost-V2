from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/final_beta_gate_refresh.json"
OUT_MD = ROOT / "docs/release/final_beta_gate_refresh.md"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

REFRESH_CALLS: list[tuple[str, str, str]] = [
    ("ci_run_evidence", "scripts.ci_run_evidence", "write_status"),
    ("external_approval_gate", "scripts.external_approval_gate", "write_status"),
    ("approval_evidence", "scripts.approval_evidence", "write_status"),
    ("staging_acceptance", "scripts.staging_acceptance_evidence", "write_status"),
    ("live_db_tx_evidence", "scripts.live_db_tx_evidence", "write_status"),
    ("route_tx_slice_rollup", "scripts.route_tx_slice_rollup", "write_rollup"),
    ("release_go_no_go", "scripts.release_go_no_go", "write_status"),
    ("beta_blocker_burndown", "scripts.beta_blocker_burndown", "write_plan"),
    ("docs_inventory", "scripts.docs_inventory", "write_inventory"),
]

BETA_CRITICAL_IDS = {
    "CI-001",
    "LEGAL-001",
    "SEC-001",
    "CONTENT-001",
    "STAGING-001",
}

PASSING_STATUSES = {"runtime-passing", "integration-passing", "production-ready"}


@dataclass(frozen=True)
class RefreshResult:
    name: str
    module: str
    function: str
    status: str
    detail: str


@dataclass(frozen=True)
class RegistryFindingSummary:
    id: str
    title: str
    proof_status: str
    blocks_beta: bool
    external_dependency: bool
    evidence_file: str
    closure_blocker: str
    release_ready: bool


@dataclass(frozen=True)
class FinalGateRefresh:
    generated_at: str
    current_commit: str
    beta_decision: str
    beta_blocker_count: int
    refresh_results: list[RefreshResult]
    beta_critical_findings: list[RegistryFindingSummary]
    non_ready_beta_findings: list[RegistryFindingSummary]
    required_next_actions: list[str]
    no_false_closure_rules: list[str]


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


def _import_callable(module_name: str, function_name: str) -> Callable[[], Any]:
    module = __import__(module_name, fromlist=[function_name])
    return getattr(module, function_name)


def _status_from_result(result: Any) -> str:
    for attr in ["decision", "status", "burn_down_status", "plan_status", "local_status"]:
        value = getattr(result, attr, None)
        if value is not None:
            return str(value)
    return result.__class__.__name__


def refresh_all() -> list[RefreshResult]:
    results: list[RefreshResult] = []
    for name, module_name, function_name in REFRESH_CALLS:
        try:
            fn = _import_callable(module_name, function_name)
            value = fn()
            results.append(
                RefreshResult(
                    name=name,
                    module=module_name,
                    function=function_name,
                    status="ok",
                    detail=_status_from_result(value),
                )
            )
        except Exception as exc:
            results.append(
                RefreshResult(
                    name=name,
                    module=module_name,
                    function=function_name,
                    status="error",
                    detail=f"{exc.__class__.__name__}: {exc}",
                )
            )
    return results


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "~", ""}:
        return None
    return value.strip("\"'")


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


def _evidence_exists(path: str) -> bool:
    return bool(path) and (ROOT / path).exists()


def summarize_finding(item: dict[str, Any]) -> RegistryFindingSummary:
    proof_status = str(item.get("proof_status") or "not-started")
    blocks_beta = bool(item.get("blocks_beta"))
    external = bool(item.get("external_dependency"))
    evidence_file = str(item.get("evidence_file") or "")
    release_ready = (
        (proof_status in PASSING_STATUSES)
        and _evidence_exists(evidence_file)
        and (not external or proof_status == "production-ready")
    )
    return RegistryFindingSummary(
        id=str(item.get("id") or "UNKNOWN"),
        title=str(item.get("title") or ""),
        proof_status=proof_status,
        blocks_beta=blocks_beta,
        external_dependency=external,
        evidence_file=evidence_file,
        closure_blocker=str(item.get("closure_blocker") or ""),
        release_ready=release_ready,
    )


def build_refresh() -> FinalGateRefresh:
    refresh_results = refresh_all()
    summaries = [summarize_finding(item) for item in load_registry_items()]
    beta_critical = [
        item for item in summaries
        if item.id in BETA_CRITICAL_IDS or item.blocks_beta
    ]
    non_ready = [item for item in beta_critical if not item.release_ready]

    actions: list[str] = []
    if any(item.id == "CI-001" for item in non_ready):
        actions.append("Attach accepted GitHub Actions run metadata for CI-001.")
    if any(item.id in {"LEGAL-001", "SEC-001", "CONTENT-001"} for item in non_ready):
        actions.append("Attach complete legal/security/content approval metadata.")
    if any(item.id == "STAGING-001" for item in non_ready):
        actions.append("Attach accepted staging smoke evidence.")
    if any(item.id.startswith("ROUTE-TX-") for item in non_ready):
        actions.append("Attach live DB route transaction evidence and rerun route transaction rollup.")
    if any(result.status == "error" for result in refresh_results):
        actions.append("Repair refresh errors before evaluating release readiness.")
    if not actions:
        actions.append("Review release_decision_log.md and obtain explicit release-owner sign-off.")

    return FinalGateRefresh(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        beta_decision="GO" if not non_ready and all(r.status == "ok" for r in refresh_results) else "NO-GO",
        beta_blocker_count=len(non_ready),
        refresh_results=refresh_results,
        beta_critical_findings=beta_critical,
        non_ready_beta_findings=non_ready,
        required_next_actions=actions,
        no_false_closure_rules=[
            "Do not mark beta GO while any beta-critical registry item is not release-ready.",
            "Do not treat generated templates as external approval.",
            "Do not treat local checks as remote CI, staging, or live DB evidence.",
            "Do not use this refresh report as release-owner approval.",
        ],
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
    for result in refresh.refresh_results:
        lines.append(f"| `{result.name}` | `{result.status}` | `{result.detail}` |")

    lines.extend(
        [
            "",
            "## Beta-critical findings",
            "",
            "| ID | Proof status | External | Evidence | Release-ready | Blocker |",
            "|---|---|---:|---|---:|---|",
        ]
    )
    for item in refresh.beta_critical_findings:
        lines.append(
            f"| `{item.id}` | `{item.proof_status}` | {item.external_dependency} | "
            f"`{item.evidence_file}` | {item.release_ready} | {item.closure_blocker} |"
        )

    lines.extend(["", "## Required next actions", ""])
    lines.extend(f"- {action}" for action in refresh.required_next_actions)

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in refresh.no_false_closure_rules)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a release-gate refresh report. It does not approve beta release.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return refresh


__all__ = ["FinalGateRefresh", "RefreshResult", "RegistryFindingSummary", "build_refresh", "write_refresh"]
