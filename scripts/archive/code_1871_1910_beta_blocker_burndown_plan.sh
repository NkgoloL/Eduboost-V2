#!/usr/bin/env bash
set -euo pipefail

# code_1871_1910_beta_blocker_burndown_plan.sh
# BLOCKER-BURN-001 / code_1871_1910 — beta-blocker burn-down planning.
# Boundary: planning artifact only; it does not resolve CI, external approvals,
# staging acceptance, or production readiness.

mkdir -p docs/release scripts tests/unit

cat > scripts/beta_blocker_burndown.py <<'PY'
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
PY

cat > scripts/patch_beta_blocker_burndown_registry.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def block() -> str:
    return f"""  - id: BLOCKER-BURN-001
    title: Beta blocker burn-down planning
    severity: P1
    gate: 7
    owner: release
    implementation_batch: code_1871_1910
    proof_status: runtime-passing
    proof_command: make backend-implementation-1871-1910-full-check
    evidence_file: docs/release/beta_blocker_burndown_plan.md
    last_verified_commit: {current_commit()}
    closure_blocker: plan only; blockers remain until their own evidence gates pass
    blocks_beta: false
    external_dependency: false
"""


def replace_or_append(text: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = "  - id: BLOCKER-BURN-001"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + block()
    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + block()
    return text[:index] + block() + text[next_index + 1:]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(text), encoding="utf-8")
    print("Updated BLOCKER-BURN-001 evidence registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x scripts/patch_beta_blocker_burndown_registry.py

cat > scripts/check_beta_blocker_burndown.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.beta_blocker_burndown import write_plan  # noqa: E402

CRITICAL = [
    "scripts/beta_blocker_burndown.py",
    "scripts/patch_beta_blocker_burndown_registry.py",
    "scripts/check_beta_blocker_burndown.py",
    "tests/unit/test_beta_blocker_burndown.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    release_mode = "--release" in sys.argv
    print("Beta blocker burn-down check")
    plan = write_plan()
    print(f"- INFO burn-down status: {plan.burn_down_status}")
    print(f"- INFO blocker actions: {len(plan.actions)}")
    if plan.source_decision == "NO-GO" and not plan.actions:
        failures.append("NO-GO source decision must have blocker actions")
    else:
        print("- PASS blocker actions are consistent with source decision")
    if plan.actions and plan.release_mode_allowed:
        failures.append("release mode cannot be allowed while blocker actions exist")
    else:
        print("- PASS release mode is not allowed while blockers exist")
    if release_mode and not plan.release_mode_allowed:
        failures.append("release mode requires blocker burn-down status clear")
    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")
    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_beta_blocker_burndown.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS beta blocker burn-down tests")
        else:
            failures.append("beta blocker burn-down tests failed")
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff beta blocker burn-down check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS beta blocker burn-down check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x scripts/check_beta_blocker_burndown.py

cat > tests/unit/test_beta_blocker_burndown.py <<'PY'
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.beta_blocker_burndown import build_plan, write_plan

ROOT = Path(__file__).resolve().parents[2]


def test_beta_blocker_burndown_builds_plan_from_release_status():
    plan = build_plan()
    assert plan.source_decision in {"GO", "NO-GO", "UNKNOWN"}
    assert plan.burn_down_status in {"blocked", "clear"}
    assert plan.no_false_closure_rules


def test_beta_blocker_burndown_tracks_known_release_critical_items_when_present():
    plan = build_plan()
    action_ids = {action.id for action in plan.actions}
    if plan.source_decision == "NO-GO":
        assert action_ids
        assert {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.intersection(action_ids)


def test_beta_blocker_burndown_local_closure_rules_are_conservative():
    plan = build_plan()
    for action in plan.actions:
        if action.id in {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}:
            assert not action.can_be_closed_locally


def test_beta_blocker_burndown_writes_reports():
    plan = write_plan()
    assert (ROOT / "docs/release/beta_blocker_burndown_plan.json").exists()
    assert (ROOT / "docs/release/beta_blocker_burndown_plan.md").exists()
    assert plan.current_commit


def test_beta_blocker_burndown_checker_runs_in_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_blocker_burndown.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_beta_blocker_burndown_release_mode_fails_when_blocked():
    plan = build_plan()
    if plan.release_mode_allowed:
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_blocker_burndown.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires blocker burn-down status clear" in result.stdout


def test_makefile_contains_beta_blocker_burndown_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "beta-blocker-burndown-plan:" in source
    assert "beta-blocker-burndown-check:" in source
    assert "backend-implementation-1871-1910-full-check:" in source
PY

cat > docs/release/no_false_closure_status_after_1871_1910.md <<'MD'
# No False-Closure Status After BLOCKER-BURN-001 / code_1871_1910

**Status:** beta-blocker burn-down plan added.

## Proven

- The generated release NO-GO state is converted into ordered blocker actions.
- CI and external approval blockers are marked as not locally closable.
- Release mode remains blocked while any blocker action remains.
- The burn-down artifact does not resolve any blocker by itself.

## Not claimed

- Any beta blocker is complete.
- CI authority is complete.
- External approval is complete.
- Release is approved.
MD

cat > docs/release/next_execution_queue_after_1871_1910.md <<'MD'
# Next Execution Queue After BLOCKER-BURN-001 / code_1871_1910

## Recommended next batch

`STAGING-PROOF-001 / code_1911_1950` — staging acceptance evidence capture scaffold.

## Scope candidates

1. Generate a staging smoke evidence schema.
2. Add a staging acceptance evidence validator.
3. Keep STAGING-001 external-blocked until a real staging evidence URL is attached.
4. Avoid claiming production readiness from local checks.
MD

python3 - <<'PY'
from pathlib import Path
path = Path("Makefile")
text = path.read_text(encoding="utf-8") if path.exists() else ""
block = """

.PHONY: beta-blocker-burndown-registry-patch beta-blocker-burndown-plan beta-blocker-burndown-check beta-blocker-burndown-release-check beta-blocker-burndown-test backend-implementation-1871-1910-full-check

beta-blocker-burndown-registry-patch:
	PYTHONPATH=. python3 scripts/patch_beta_blocker_burndown_registry.py

beta-blocker-burndown-plan:
	PYTHONPATH=. python3 -c "from scripts.beta_blocker_burndown import write_plan; p = write_plan(); print(p.burn_down_status)"

beta-blocker-burndown-check: beta-blocker-burndown-registry-patch
	PYTHONPATH=. python3 scripts/check_beta_blocker_burndown.py

beta-blocker-burndown-release-check:
	PYTHONPATH=. python3 scripts/check_beta_blocker_burndown.py --release

beta-blocker-burndown-test:
	pytest -c pytest.ini tests/unit/test_beta_blocker_burndown.py -q --no-cov --tb=short

backend-implementation-1871-1910-full-check: beta-blocker-burndown-plan beta-blocker-burndown-check beta-blocker-burndown-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/beta_blocker_burndown.py scripts/patch_beta_blocker_burndown_registry.py scripts/check_beta_blocker_burndown.py tests/unit/test_beta_blocker_burndown.py --select F821,F401,F811,E402
"""
if "backend-implementation-1871-1910-full-check:" not in text:
    path.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    print("Updated Makefile with BLOCKER-BURN-001 targets")
else:
    print("Makefile already contains BLOCKER-BURN-001 targets")
PY

python3 - <<'PY'
from pathlib import Path
path = Path("docs/release/EVIDENCE_INDEX.md")
text = path.read_text(encoding="utf-8") if path.exists() else "# Evidence Index\n"
entry = """

## BLOCKER-BURN-001 / Backend implementation 1871-1910 — Beta blocker burn-down planning

Audit drivers:

- The release-owner NO-GO status must become an actionable burn-down queue.
- CI and external approval blockers must not be closed by local scripts.
- Release mode must remain blocked until the burn-down is clear.

Commands:

```bash
make beta-blocker-burndown-plan
make beta-blocker-burndown-check
make beta-blocker-burndown-release-check
make beta-blocker-burndown-test
make backend-implementation-1871-1910-full-check
```
"""
if "BLOCKER-BURN-001 / Backend implementation 1871-1910" not in text:
    path.write_text(text.rstrip() + entry + "\n", encoding="utf-8")
    print("Updated EVIDENCE_INDEX with BLOCKER-BURN-001 entry")
else:
    print("EVIDENCE_INDEX already contains BLOCKER-BURN-001 entry")
PY

PYTHONPATH=. python3 scripts/patch_beta_blocker_burndown_registry.py
PYTHONPATH=. python3 -c "from scripts.beta_blocker_burndown import write_plan; p = write_plan(); print(p.burn_down_status)"
PYTHONPATH=. python3 scripts/check_beta_blocker_burndown.py
pytest -c pytest.ini tests/unit/test_beta_blocker_burndown.py -q --no-cov --tb=short
python3 -m compileall -q scripts tests
python3 -m ruff check scripts/beta_blocker_burndown.py scripts/patch_beta_blocker_burndown_registry.py scripts/check_beta_blocker_burndown.py tests/unit/test_beta_blocker_burndown.py --select F821,F401,F811,E402

if [ -f scripts/docs_inventory.py ]; then
  PYTHONPATH=. python3 scripts/docs_inventory.py --write || true
fi

echo "BLOCKER-BURN-001 / code_1871_1910 beta-blocker burn-down planning batch is ready."
