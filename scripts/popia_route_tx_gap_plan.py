from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POPIA_REPORT_JSON = ROOT / "docs/release/popia_route_transaction_slice_report.json"
OUT_JSON = ROOT / "docs/release/popia_route_transaction_gap_plan.json"
OUT_MD = ROOT / "docs/release/popia_route_transaction_gap_plan.md"


@dataclass(frozen=True)
class POPIARouteTxGapAction:
    route_function: str
    line: int
    current_status: str
    blocker_reason: str
    implementation_action: str
    verification_action: str
    can_be_closed_by_current_report: bool


@dataclass(frozen=True)
class POPIARouteTxGapPlan:
    generated_at: str
    current_commit: str
    source_report: str
    source_local_status: str
    source_live_db_status: str
    status: str
    action_count: int
    actions: list[POPIARouteTxGapAction]
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


def _ensure_source_report() -> dict[str, Any]:
    if not POPIA_REPORT_JSON.exists():
        try:
            from scripts.route_tx_popia_slice import write_report

            write_report()
        except Exception:
            return {}
    if not POPIA_REPORT_JSON.exists():
        return {}
    return json.loads(POPIA_REPORT_JSON.read_text(encoding="utf-8"))


def _reason_for(finding: dict[str, Any]) -> str:
    reason = str(finding.get("reason") or "").strip()
    if reason:
        return reason

    problems: list[str] = []
    if not finding.get("service_delegate_calls"):
        problems.append("no POPIA service delegate call found")
    if finding.get("direct_db_mutations"):
        problems.append("direct DB mutations present")
    return "; ".join(problems) or "route transaction source proof not established"


def build_plan() -> POPIARouteTxGapPlan:
    report = _ensure_source_report()
    findings = report.get("findings") or []
    actions: list[POPIARouteTxGapAction] = []

    for finding in findings:
        status = str(finding.get("route_source_status") or "unknown")
        if status == "route-delegates-to-service-boundary":
            continue
        route_function = str(finding.get("route_function") or "unknown")
        line = int(finding.get("line") or 0)
        reason = _reason_for(finding)
        actions.append(
            POPIARouteTxGapAction(
                route_function=route_function,
                line=line,
                current_status=status,
                blocker_reason=reason,
                implementation_action=(
                    f"Refactor POPIA route `{route_function}` to delegate mutation work to an application/service "
                    "boundary that owns the transaction, and remove direct router-level persistence coordination."
                ),
                verification_action=(
                    f"Rerun `make route-tx-popia-slice-check` and add a route-level negative test for `{route_function}` "
                    "with injected failure before accepting local proof."
                ),
                can_be_closed_by_current_report=False,
            )
        )

    local_status = str(report.get("local_status") or "missing-report")
    live_status = str(report.get("live_db_status") or "missing-report")
    status = "blocked" if actions or local_status != "route-popia-delegation-passing" else "local-source-clear-live-db-still-required"

    return POPIARouteTxGapPlan(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        source_report="docs/release/popia_route_transaction_slice_report.json",
        source_local_status=local_status,
        source_live_db_status=live_status,
        status=status,
        action_count=len(actions),
        actions=actions,
        no_false_closure_rules=[
            "Do not mark ROUTE-TX-POPIA-001 runtime-passing while local_status is route-popia-delegation-not-proven.",
            "Do not proceed to diagnostics route transaction slices as if POPIA were closed.",
            "Do not close live DB proof from local source reports.",
            "Do not use generated plans as implementation evidence.",
        ],
    )


def write_plan() -> POPIARouteTxGapPlan:
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(asdict(plan), indent=2), encoding="utf-8")

    lines = [
        "# POPIA Route Transaction Gap Plan",
        "",
        f"Generated at: `{plan.generated_at}`",
        f"Commit: `{plan.current_commit}`",
        "",
        f"- Source report: `{plan.source_report}`",
        f"- Source local status: `{plan.source_local_status}`",
        f"- Source live DB status: `{plan.source_live_db_status}`",
        f"- Status: `{plan.status}`",
        f"- Action count: `{plan.action_count}`",
        "",
        "## Gap actions",
        "",
        "| Route function | Line | Current status | Reason | Closeable by current report |",
        "|---|---:|---|---|---:|",
    ]
    if plan.actions:
        for action in plan.actions:
            lines.append(
                f"| `{action.route_function}` | {action.line} | `{action.current_status}` | "
                f"{action.blocker_reason} | {action.can_be_closed_by_current_report} |"
            )
    else:
        lines.append("| `-` | 0 | `none` | No local source gaps detected | False |")

    lines.extend(["", "## Implementation actions", ""])
    if plan.actions:
        for action in plan.actions:
            lines.extend(
                [
                    f"### {action.route_function}",
                    "",
                    f"- Implementation: {action.implementation_action}",
                    f"- Verification: {action.verification_action}",
                    "",
                ]
            )
    else:
        lines.append("- No POPIA route-source implementation gaps detected by the current report.")

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in plan.no_false_closure_rules)
    lines.extend(["", "## Interpretation", "", "This plan is a blocker queue. It is not proof that POPIA route transaction wiring is complete.", ""])

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return plan


__all__ = ["POPIARouteTxGapAction", "POPIARouteTxGapPlan", "build_plan", "write_plan"]
