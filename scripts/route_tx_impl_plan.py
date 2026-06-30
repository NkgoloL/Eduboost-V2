from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TX_ROUTE_INVENTORY_JSON = ROOT / "docs/architecture/tx_route_wiring_inventory.json"
TX_ROUTE_INVENTORY_MD = ROOT / "docs/architecture/tx_route_wiring_inventory.md"
OUT_JSON = ROOT / "docs/release/route_transaction_implementation_plan.json"
OUT_MD = ROOT / "docs/release/route_transaction_implementation_plan.md"

DOMAIN_PRIORITY = {
    "auth": 10,
    "popia": 20,
    "diagnostics": 30,
    "lessons": 40,
}

DOMAIN_SERVICE_HINTS = {
    "auth": "TransactionalAuthRegistrationService",
    "popia": "TransactionalPOPIAConsentLifecycleService",
    "diagnostics": "TransactionalDiagnosticResponseService",
    "lessons": "TransactionalLessonCompletionService",
}

DOMAIN_TEST_HINTS = {
    "auth": "register rollback: fail after user/guardian/learner creation and assert no partial rows remain",
    "popia": "consent lifecycle rollback: fail after consent/audit write and assert atomic rollback",
    "diagnostics": "response/mastery/audit rollback: fail after response or mastery update and assert atomic rollback",
    "lessons": "lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback",
}


@dataclass(frozen=True)
class RouteTxImplementationAction:
    id: str
    domain: str
    route_function: str
    route_file: str
    line: int
    current_status: str
    priority: str
    service_hint: str
    implementation_action: str
    negative_test_action: str
    live_db_proof_required: bool
    can_be_closed_by_static_marker: bool


@dataclass(frozen=True)
class RouteTxImplementationPlan:
    generated_at: str
    current_commit: str
    source_inventory: str
    source_status: str
    plan_status: str
    action_count: int
    actions: list[RouteTxImplementationAction]
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


def _generate_inventory_if_possible() -> None:
    if TX_ROUTE_INVENTORY_JSON.exists():
        return
    try:
        from scripts.tx_route_wiring_inventory import write_inventory

        write_inventory()
    except Exception:
        return


def _load_inventory() -> dict[str, Any]:
    _generate_inventory_if_possible()
    if not TX_ROUTE_INVENTORY_JSON.exists():
        return {
            "status": "missing-inventory",
            "routes": [],
        }
    return json.loads(TX_ROUTE_INVENTORY_JSON.read_text(encoding="utf-8"))


def _route_rows_requiring_wiring(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    rows = inventory.get("routes") or []
    return [
        row
        for row in rows
        if row.get("mutation_candidate") is True
        and row.get("status") == "route-transaction-wiring-not-proven"
    ]


def _priority_for(domain: str, index: int) -> str:
    if domain in {"auth", "popia"}:
        return "P0"
    if domain == "diagnostics":
        return "P1"
    return "P2"


def _action_id(domain: str, route_function: str, index: int) -> str:
    safe_fn = "".join(ch if ch.isalnum() else "_" for ch in route_function).strip("_").lower()
    return f"ROUTE-TX-{index:03d}-{domain}-{safe_fn}"


def build_plan() -> RouteTxImplementationPlan:
    inventory = _load_inventory()
    rows = _route_rows_requiring_wiring(inventory)
    rows = sorted(
        rows,
        key=lambda row: (
            DOMAIN_PRIORITY.get(str(row.get("domain")), 99),
            str(row.get("path")),
            int(row.get("line") or 0),
            str(row.get("function_name")),
        ),
    )

    actions: list[RouteTxImplementationAction] = []
    for index, row in enumerate(rows, start=1):
        domain = str(row.get("domain") or "unknown")
        function = str(row.get("function_name") or "unknown")
        route_file = str(row.get("path") or "")
        line = int(row.get("line") or 0)
        service_hint = DOMAIN_SERVICE_HINTS.get(domain, "transactional application service")
        actions.append(
            RouteTxImplementationAction(
                id=_action_id(domain, function, index),
                domain=domain,
                route_function=function,
                route_file=route_file,
                line=line,
                current_status=str(row.get("status") or "unknown"),
                priority=_priority_for(domain, index),
                service_hint=service_hint,
                implementation_action=(
                    f"Refactor `{route_file}:{function}` to delegate mutation work to `{service_hint}` "
                    "inside one transaction boundary instead of coordinating partial writes in the router."
                ),
                negative_test_action=DOMAIN_TEST_HINTS.get(
                    domain,
                    "add route-level rollback negative test with injected failure and assert no partial persistence",
                ),
                live_db_proof_required=True,
                can_be_closed_by_static_marker=False,
            )
        )

    status = "blocked-until-route-wiring-and-live-db-proof" if actions else "no-unproven-mutation-routes-detected"

    return RouteTxImplementationPlan(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        source_inventory="docs/architecture/tx_route_wiring_inventory.json",
        source_status=str(inventory.get("status") or "unknown"),
        plan_status=status,
        action_count=len(actions),
        actions=actions,
        no_false_closure_rules=[
            "Do not close route transaction wiring from static service-name markers.",
            "Do not close route transaction wiring from isolated rollback service tests alone.",
            "Do not close route transaction wiring until route-level negative tests exercise the production route path.",
            "Do not close live DB proof until a real database transaction rollback check is attached.",
        ],
    )


def write_plan() -> RouteTxImplementationPlan:
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(asdict(plan), indent=2), encoding="utf-8")

    lines = [
        "# Route Transaction Implementation Plan",
        "",
        f"Generated at: `{plan.generated_at}`",
        f"Commit: `{plan.current_commit}`",
        "",
        f"- Source inventory: `{plan.source_inventory}`",
        f"- Source status: `{plan.source_status}`",
        f"- Plan status: `{plan.plan_status}`",
        f"- Action count: `{plan.action_count}`",
        "",
        "## Ordered implementation actions",
        "",
        "| Priority | ID | Domain | Route function | File | Line | Service hint | Live DB proof required |",
        "|---|---|---|---|---|---:|---|---:|",
    ]
    for action in plan.actions:
        lines.append(
            f"| `{action.priority}` | `{action.id}` | `{action.domain}` | `{action.route_function}` | "
            f"`{action.route_file}` | {action.line} | `{action.service_hint}` | {action.live_db_proof_required} |"
        )

    lines.extend(["", "## Implementation detail", ""])
    if plan.actions:
        for action in plan.actions:
            lines.extend(
                [
                    f"### {action.id}",
                    "",
                    f"- Current status: `{action.current_status}`",
                    f"- Implementation: {action.implementation_action}",
                    f"- Negative test: {action.negative_test_action}",
                    f"- Static marker closure allowed: `{action.can_be_closed_by_static_marker}`",
                    "",
                ]
            )
    else:
        lines.append("- No unproven mutation routes detected by the current inventory.")

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in plan.no_false_closure_rules)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This plan is an implementation queue. It does not prove route transaction wiring is complete.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return plan


__all__ = [
    "RouteTxImplementationAction",
    "RouteTxImplementationPlan",
    "build_plan",
    "write_plan",
]
