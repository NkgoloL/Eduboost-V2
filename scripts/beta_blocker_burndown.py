from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE_STATUS_JSON = ROOT / "docs/release/release_go_no_go_status.json"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
OUT_JSON = ROOT / "docs/release/beta_blocker_burndown_plan.json"
OUT_MD = ROOT / "docs/release/beta_blocker_burndown_plan.md"

RELEASE_CRITICAL = {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}
EXTERNAL_CATEGORIES = {"ci-authority", "legal", "security", "content", "staging", "external"}


@dataclass(frozen=True)
class BetaBlockerAction:
    id: str
    category: str
    status: str
    reason: str
    owner: str
    evidence_file: str
    next_action: str
    verification_command: str
    priority: str
    can_be_closed_locally: bool


@dataclass(frozen=True)
class BetaBlockerBurndownPlan:
    generated_at: str
    current_commit: str
    source_decision: str
    source_beta_blocker_count: int
    burn_down_status: str
    actions: list[BetaBlockerAction]
    release_mode_allowed: bool
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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_scalar(value: str) -> Any:
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


def load_registry_items() -> dict[str, dict[str, Any]]:
    if not REGISTRY.exists():
        return {}
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in REGISTRY.read_text(encoding="utf-8").splitlines():
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
                current[key.strip()] = parse_scalar(value)
            continue
        if current is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current[key.strip()] = parse_scalar(value)
    if current:
        items.append(current)
    return {str(item.get("id")): item for item in items if item.get("id")}


def category_for(item_id: str, external: bool) -> str:
    if item_id == "CI-001":
        return "ci-authority"
    if item_id == "LEGAL-001":
        return "legal"
    if item_id == "SEC-001":
        return "security"
    if item_id == "CONTENT-001":
        return "content"
    if item_id == "STAGING-001":
        return "staging"
    return "external" if external else "engineering"


def priority_for(category: str) -> str:
    return "P0" if category in EXTERNAL_CATEGORIES else "P1"


def verification_for(item_id: str, category: str) -> str:
    if item_id == "CI-001":
        return "make ci-authority-release-check"
    if category in {"legal", "security", "content", "staging", "external"}:
        return "make external-approval-release-check"
    return "make release-go-no-go-local-check"


def next_action_for(item_id: str, category: str, reason: str) -> str:
    if item_id == "CI-001":
        return "Attach a passing GitHub Actions run URL for codex/production_readiness, then rerun CI authority release check."
    if item_id == "LEGAL-001":
        return "Obtain POPIA/legal approval and replace pending metadata in legal_approval.md."
    if item_id == "SEC-001":
        return "Obtain security approval or pen-test sign-off and replace pending metadata in security_approval.md."
    if item_id == "CONTENT-001":
        return "Obtain educator/content approval for beta scope and replace pending metadata in content_approval.md."
    if item_id == "STAGING-001":
        return "Run staging acceptance, attach evidence URL, and replace pending metadata in staging_acceptance.md."
    return f"Resolve registry blocker: {reason or 'blocked'}"


def make_action(item_id: str, reason: str, finding: dict[str, Any], registry_item: dict[str, Any]) -> BetaBlockerAction:
    external = bool(finding.get("external_dependency") or registry_item.get("external_dependency"))
    category = category_for(item_id, external)
    owner = str(registry_item.get("owner") or finding.get("owner") or category or "release")
    status = str(finding.get("proof_status") or registry_item.get("proof_status") or "unknown")
    evidence_file = str(finding.get("evidence_file") or registry_item.get("evidence_file") or "")
    return BetaBlockerAction(
        id=item_id,
        category=category,
        status=status,
        reason=reason or str(finding.get("reason") or registry_item.get("closure_blocker") or "blocked"),
        owner=owner,
        evidence_file=evidence_file,
        next_action=next_action_for(item_id, category, reason),
        verification_command=verification_for(item_id, category),
        priority=priority_for(category),
        can_be_closed_locally=category not in EXTERNAL_CATEGORIES,
    )


def build_plan() -> BetaBlockerBurndownPlan:
    release_status = read_json(RELEASE_STATUS_JSON)
    registry = load_registry_items()
    findings = {str(item.get("id")): item for item in release_status.get("findings", []) if item.get("id")}
    actions: list[BetaBlockerAction] = []
    seen: set[str] = set()

    for blocker in release_status.get("blockers", []) or []:
        item_id, _, reason = str(blocker).partition(":")
        item_id = item_id.strip()
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        actions.append(make_action(item_id, reason.strip(), findings.get(item_id, {}), registry.get(item_id, {})))

    for item_id in sorted(RELEASE_CRITICAL - seen):
        registry_item = registry.get(item_id)
        if registry_item and bool(registry_item.get("blocks_beta")):
            actions.append(make_action(item_id, str(registry_item.get("closure_blocker") or "release-critical blocker"), findings.get(item_id, {}), registry_item))

    actions = sorted(actions, key=lambda action: (action.priority, action.category, action.id))
    release_mode_allowed = not actions and release_status.get("decision") == "GO"
    return BetaBlockerBurndownPlan(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        source_decision=str(release_status.get("decision") or "UNKNOWN"),
        source_beta_blocker_count=int(release_status.get("beta_blocker_count") or len(actions)),
        burn_down_status="blocked" if actions else "clear",
        actions=actions,
        release_mode_allowed=release_mode_allowed,
        no_false_closure_rules=[
            "Do not close CI-001 from local command output.",
            "Do not close external approvals from generated templates.",
            "Do not close staging acceptance without a staging evidence URL.",
            "Do not change release decision to GO while any beta-blocking registry item remains incomplete.",
        ],
    )


def write_plan() -> BetaBlockerBurndownPlan:
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(asdict(plan), indent=2), encoding="utf-8")
    lines = [
        "# Beta Blocker Burn-Down Plan",
        "",
        f"Generated at: `{plan.generated_at}`",
        f"Commit: `{plan.current_commit}`",
        "",
        f"- Source decision: `{plan.source_decision}`",
        f"- Source beta blocker count: `{plan.source_beta_blocker_count}`",
        f"- Burn-down status: `{plan.burn_down_status}`",
        f"- Release mode allowed: `{plan.release_mode_allowed}`",
        "",
        "## Ordered blocker actions",
        "",
        "| Priority | ID | Category | Owner | Status | Local close? | Next action | Verification |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for action in plan.actions:
        lines.append(
            f"| `{action.priority}` | `{action.id}` | `{action.category}` | `{action.owner}` | "
            f"`{action.status}` | {action.can_be_closed_locally} | {action.next_action} | `{action.verification_command}` |"
        )
    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in plan.no_false_closure_rules)
    lines.extend(["", "## Interpretation", "", "This plan is an execution queue. It does not mark any blocker as resolved.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return plan


__all__ = ["BetaBlockerAction", "BetaBlockerBurndownPlan", "build_plan", "write_plan"]
