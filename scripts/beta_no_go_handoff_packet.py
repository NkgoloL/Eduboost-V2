from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/beta_no_go_handoff_packet.json"
OUT_MD = ROOT / "docs/release/beta_no_go_handoff_packet.md"

FINAL_GATE_JSON = ROOT / "docs/release/final_beta_gate_refresh.json"
RELEASE_STATUS_JSON = ROOT / "docs/release/release_go_no_go_status.json"
BURN_DOWN_JSON = ROOT / "docs/release/beta_blocker_burndown_plan.json"
RUNBOOK_MD = ROOT / "docs/release/evidence_attachment_runbook.md"

REQUIRED_EVIDENCE_ITEMS = [
    "CI-001",
    "LEGAL-001",
    "SEC-001",
    "CONTENT-001",
    "STAGING-001",
    "ROUTE-TX-AUTH-001",
    "ROUTE-TX-POPIA-001",
    "ROUTE-TX-DIAG-001",
]


@dataclass(frozen=True)
class HandoffSource:
    name: str
    path: str
    exists: bool
    status: str


@dataclass(frozen=True)
class HandoffRequiredItem:
    id: str
    category: str
    current_status: str
    required_action: str
    local_close_allowed: bool


@dataclass(frozen=True)
class BetaNoGoHandoffPacket:
    generated_at: str
    current_commit: str
    handoff_status: str
    beta_decision: str
    blocker_count: int
    sources: list[HandoffSource]
    required_items: list[HandoffRequiredItem]
    operator_next_steps: list[str]
    freeze_rules: list[str]
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


def _safe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _refresh_dependencies() -> None:
    for module_name, function_name in [
        ("scripts.final_gate_refresh", "write_refresh"),
        ("scripts.release_go_no_go", "write_status"),
        ("scripts.beta_blocker_burndown", "write_plan"),
    ]:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)()
        except Exception:
            continue


def _source_status(name: str, path: Path) -> HandoffSource:
    payload = _safe_read_json(path)
    status = str(
        payload.get("beta_decision")
        or payload.get("decision")
        or payload.get("burn_down_status")
        or payload.get("status")
        or ("missing" if not path.exists() else "unknown")
    )
    return HandoffSource(
        name=name,
        path=path.relative_to(ROOT).as_posix(),
        exists=path.exists(),
        status=status,
    )


def _category(item_id: str) -> str:
    if item_id == "CI-001":
        return "ci"
    if item_id in {"LEGAL-001", "SEC-001", "CONTENT-001"}:
        return "external-approval"
    if item_id == "STAGING-001":
        return "staging"
    if item_id.startswith("ROUTE-TX-"):
        return "live-db-transaction"
    return "release"


def _required_action(item_id: str) -> str:
    actions = {
        "CI-001": "Attach accepted GitHub Actions run metadata using `make ci-run-evidence-attach`.",
        "LEGAL-001": "Attach legal/POPIA approval metadata using `make approval-evidence-attach`.",
        "SEC-001": "Attach security approval metadata using `make approval-evidence-attach`.",
        "CONTENT-001": "Attach educator/content approval metadata using `make approval-evidence-attach`.",
        "STAGING-001": "Populate real staging smoke evidence and rerun staging release checks.",
        "ROUTE-TX-AUTH-001": "Attach accepted auth live DB rollback evidence using `make live-db-tx-evidence-attach`.",
        "ROUTE-TX-POPIA-001": "Attach accepted POPIA live DB rollback evidence using `make live-db-tx-evidence-attach`.",
        "ROUTE-TX-DIAG-001": "Attach accepted diagnostics live DB rollback evidence using `make live-db-tx-evidence-attach`.",
    }
    return actions.get(item_id, "Attach required release evidence and rerun final gate refresh.")


def _status_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    final_gate = _safe_read_json(FINAL_GATE_JSON)
    for item in final_gate.get("beta_critical_findings") or []:
        item_id = str(item.get("id") or "")
        if item_id:
            lookup[item_id] = str(item.get("proof_status") or "unknown")

    burn_down = _safe_read_json(BURN_DOWN_JSON)
    for action in burn_down.get("actions") or []:
        item_id = str(action.get("id") or "")
        if item_id and item_id not in lookup:
            lookup[item_id] = str(action.get("status") or "blocked")

    return lookup


def build_packet() -> BetaNoGoHandoffPacket:
    _refresh_dependencies()

    final_gate = _safe_read_json(FINAL_GATE_JSON)
    release_status = _safe_read_json(RELEASE_STATUS_JSON)
    burn_down = _safe_read_json(BURN_DOWN_JSON)

    beta_decision = str(final_gate.get("beta_decision") or release_status.get("decision") or "UNKNOWN")
    blocker_count = int(
        final_gate.get("beta_blocker_count")
        or release_status.get("beta_blocker_count")
        or len(burn_down.get("actions") or [])
        or 0
    )

    lookup = _status_lookup()
    required_items = [
        HandoffRequiredItem(
            id=item_id,
            category=_category(item_id),
            current_status=lookup.get(item_id, "pending-or-not-recorded"),
            required_action=_required_action(item_id),
            local_close_allowed=False,
        )
        for item_id in REQUIRED_EVIDENCE_ITEMS
    ]

    sources = [
        _source_status("final_beta_gate_refresh", FINAL_GATE_JSON),
        _source_status("release_go_no_go_status", RELEASE_STATUS_JSON),
        _source_status("beta_blocker_burndown_plan", BURN_DOWN_JSON),
        HandoffSource(
            name="evidence_attachment_runbook",
            path=RUNBOOK_MD.relative_to(ROOT).as_posix(),
            exists=RUNBOOK_MD.exists(),
            status="present" if RUNBOOK_MD.exists() else "missing",
        ),
    ]

    handoff_status = "handoff-ready-no-go" if beta_decision == "NO-GO" and RUNBOOK_MD.exists() else "handoff-incomplete"

    return BetaNoGoHandoffPacket(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        handoff_status=handoff_status,
        beta_decision=beta_decision,
        blocker_count=blocker_count,
        sources=sources,
        required_items=required_items,
        operator_next_steps=[
            "Stop adding release scaffolds unless a concrete evidence gap is found.",
            "Attach real CI, approval, staging, and live DB evidence using the evidence attachment runbook.",
            "Run `make final-gate-refresh` after each evidence attachment.",
            "Run all release-mode checks only after the final refresh reports GO.",
            "Obtain release-owner sign-off after all release-mode checks pass.",
        ],
        freeze_rules=[
            "Treat the local scaffold phase as frozen.",
            "Prioritize real evidence capture over additional local documentation gates.",
            "Only add new scripts if an existing evidence attachment path is objectively blocked.",
        ],
        no_false_closure_rules=[
            "Do not mark beta GO from this handoff packet.",
            "Do not close external approvals without approver, date, decision, and evidence URL.",
            "Do not close CI without a real GitHub Actions run URL.",
            "Do not close staging without real staging smoke evidence.",
            "Do not close live DB transaction proof without accepted live DB evidence metadata.",
        ],
    )


def write_packet() -> BetaNoGoHandoffPacket:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(asdict(packet), indent=2), encoding="utf-8")

    lines = [
        "# Beta NO-GO Handoff Packet",
        "",
        f"Generated at: `{packet.generated_at}`",
        f"Commit: `{packet.current_commit}`",
        "",
        f"**Handoff status:** `{packet.handoff_status}`",
        f"**Beta decision:** `{packet.beta_decision}`",
        f"**Blocker count:** `{packet.blocker_count}`",
        "",
        "## Source surfaces",
        "",
        "| Source | Exists | Status | Path |",
        "|---|---:|---|---|",
    ]
    for source in packet.sources:
        lines.append(f"| `{source.name}` | {source.exists} | `{source.status}` | `{source.path}` |")

    lines.extend(
        [
            "",
            "## Required evidence items",
            "",
            "| ID | Category | Current status | Local close allowed | Required action |",
            "|---|---|---|---:|---|",
        ]
    )
    for item in packet.required_items:
        lines.append(
            f"| `{item.id}` | `{item.category}` | `{item.current_status}` | "
            f"{item.local_close_allowed} | {item.required_action} |"
        )

    lines.extend(["", "## Operator next steps", ""])
    lines.extend(f"- {step}" for step in packet.operator_next_steps)

    lines.extend(["", "## Freeze rules", ""])
    lines.extend(f"- {rule}" for rule in packet.freeze_rules)

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in packet.no_false_closure_rules)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This packet is a handoff artifact. It preserves the current NO-GO decision until real evidence is attached and release-mode checks pass.",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return packet


__all__ = ["BetaNoGoHandoffPacket", "HandoffRequiredItem", "HandoffSource", "build_packet", "write_packet"]
