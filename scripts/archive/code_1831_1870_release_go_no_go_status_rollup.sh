#!/usr/bin/env bash
set -euo pipefail

# code_1831_1870_release_go_no_go_status_rollup.sh
#
# Roadmap item:
# RELEASE-GO-001 / code_1831_1870 — release-owner go/no-go status rollup.
#
# Purpose:
# Produce a single release-owner status report that aggregates engineering,
# CI, external approvals, and release-critical evidence status without falsely
# converting local proof into beta approval.
#
# Boundary:
# This batch produces a decision support artifact. It does not approve release.
# It must remain NO-GO while any beta-blocking registry item is incomplete or
# external-blocked.

mkdir -p docs/release scripts tests/unit

cat > scripts/release_go_no_go.py <<'PY'
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
PY

cat > scripts/patch_release_go_no_go_registry.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


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


def block() -> str:
    return f"""  - id: RELEASE-GO-001
    title: Release-owner go/no-go status rollup
    severity: P1
    gate: 7
    owner: release
    implementation_batch: code_1831_1870
    proof_status: runtime-passing
    proof_command: make backend-implementation-1831-1870-full-check
    evidence_file: docs/release/release_go_no_go_status.md
    last_verified_commit: {current_commit()}
    closure_blocker: generated status remains NO-GO until all beta-blocking gates clear
    blocks_beta: false
    external_dependency: false
"""


def replace_or_append(text: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = "  - id: RELEASE-GO-001"
    index = text.find(marker)
    if index < 0:
        return text.rstrip() + "\n" + block()

    next_index = text.find("\n  - id:", index + 1)
    if next_index < 0:
        return text[:index] + block()
    return text[:index] + block() + text[next_index + 1 :]


def main() -> int:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    REGISTRY.write_text(replace_or_append(text), encoding="utf-8")
    print("Updated RELEASE-GO-001 evidence registry entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x scripts/patch_release_go_no_go_registry.py

cat > scripts/check_release_go_no_go.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.release_go_no_go import write_status  # noqa: E402


CRITICAL = [
    "scripts/release_go_no_go.py",
    "scripts/patch_release_go_no_go_registry.py",
    "scripts/check_release_go_no_go.py",
    "tests/unit/test_release_go_no_go.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Release go/no-go check")

    status = write_status()
    print(f"- INFO decision: {status.decision}")
    print(f"- INFO beta blockers: {status.beta_blocker_count}")

    if status.decision == "NO-GO":
        print("- PASS generated decision is NO-GO while blockers remain")
    elif status.decision == "GO":
        print("- PASS generated decision is GO")
    else:
        failures.append(f"unexpected decision: {status.decision}")

    if release_mode and status.decision != "GO":
        failures.append("release mode requires generated decision GO")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_release_go_no_go.py",
                "-q",
                "--no-cov",
                "--tb=short",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS release go/no-go unit tests")
        else:
            failures.append("release go/no-go unit tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff release go/no-go check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS release go/no-go check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x scripts/check_release_go_no_go.py

cat > tests/unit/test_release_go_no_go.py <<'PY'
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.release_go_no_go import build_status, write_status


ROOT = Path(__file__).resolve().parents[2]


def test_release_go_no_go_builds_decision_status():
    status = build_status()

    assert status.decision in {"GO", "NO-GO"}
    assert status.current_commit
    assert status.findings


def test_release_go_no_go_remains_no_go_when_external_or_ci_blockers_exist():
    status = build_status()
    blocker_ids = {blocker.split(":", 1)[0] for blocker in status.blockers}

    if {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.intersection(blocker_ids):
        assert status.decision == "NO-GO"


def test_release_go_no_go_writes_reports_and_decision_log():
    status = write_status()

    assert (ROOT / "docs/release/release_go_no_go_status.json").exists()
    assert (ROOT / "docs/release/release_go_no_go_status.md").exists()
    assert (ROOT / "docs/release/release_decision_log.md").exists()
    assert status.required_next_actions


def test_release_go_no_go_checker_runs_in_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_release_go_no_go.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_release_go_no_go_release_mode_fails_when_no_go():
    status = build_status()
    if status.decision == "GO":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_release_go_no_go.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires generated decision GO" in result.stdout


def test_makefile_contains_release_go_no_go_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "release-go-no-go-status:" in source
    assert "release-go-no-go-local-check:" in source
    assert "backend-implementation-1831-1870-full-check:" in source
PY

cat > docs/release/no_false_closure_status_after_1831_1870.md <<'MD'
# No False-Closure Status After RELEASE-GO-001 / code_1831_1870

**Status:** release-owner go/no-go rollup added.

## Proven

- A single go/no-go status report is generated.
- Beta-blocking registry items are aggregated.
- CI and external approval blockers influence the decision.
- Release-mode check fails while generated status is `NO-GO`.

## Not claimed

- Release is approved.
- Beta is approved.
- CI authority is complete.
- External approvals are complete.
- Production readiness is complete.
MD

cat > docs/release/next_execution_queue_after_1831_1870.md <<'MD'
# Next Execution Queue After RELEASE-GO-001 / code_1831_1870

## Recommended next batch

`BLOCKER-BURN-001 / code_1871_1910` — beta-blocker burn-down planning.

## Scope candidates

1. Read `release_go_no_go_status.md`.
2. Generate a concrete blocker burn-down queue.
3. Separate engineering blockers from external blockers.
4. Preserve NO-GO until all required gates are cleared.
MD

python3 - <<'PY'
from pathlib import Path

path = Path("Makefile")
text = path.read_text(encoding="utf-8") if path.exists() else ""

block = """

.PHONY: release-go-no-go-registry-patch release-go-no-go-status release-go-no-go-local-check release-go-no-go-release-check release-go-no-go-test backend-implementation-1831-1870-full-check

release-go-no-go-registry-patch:
\tPYTHONPATH=. python3 scripts/patch_release_go_no_go_registry.py

release-go-no-go-status:
\tPYTHONPATH=. python3 -c "from scripts.release_go_no_go import write_status; s = write_status(); print(s.decision)"

release-go-no-go-local-check: release-go-no-go-registry-patch
\tPYTHONPATH=. python3 scripts/check_release_go_no_go.py

release-go-no-go-release-check:
\tPYTHONPATH=. python3 scripts/check_release_go_no_go.py --release

release-go-no-go-test:
\tpytest -c pytest.ini tests/unit/test_release_go_no_go.py -q --no-cov --tb=short

backend-implementation-1831-1870-full-check: release-go-no-go-status release-go-no-go-local-check release-go-no-go-test
\tpython3 -m compileall -q scripts tests
\tpython3 -m ruff check scripts/release_go_no_go.py scripts/patch_release_go_no_go_registry.py scripts/check_release_go_no_go.py tests/unit/test_release_go_no_go.py --select F821,F401,F811,E402
"""

if "backend-implementation-1831-1870-full-check:" not in text:
    path.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    print("Updated Makefile with RELEASE-GO-001 targets")
else:
    print("Makefile already contains RELEASE-GO-001 targets")
PY

python3 - <<'PY'
from pathlib import Path

path = Path("docs/release/EVIDENCE_INDEX.md")
text = path.read_text(encoding="utf-8") if path.exists() else "# Evidence Index\n"

entry = """

## RELEASE-GO-001 / Backend implementation 1831-1870 — Release-owner go/no-go status rollup

Audit drivers:

- Release owners need one generated status surface.
- CI and external approval blockers must influence the release decision.
- Release-mode checks must fail while generated status is `NO-GO`.

Commands:

```bash
make release-go-no-go-status
make release-go-no-go-local-check
make release-go-no-go-release-check
make release-go-no-go-test
make backend-implementation-1831-1870-full-check
```
"""

if "RELEASE-GO-001 / Backend implementation 1831-1870" not in text:
    path.write_text(text.rstrip() + entry + "\n", encoding="utf-8")
    print("Updated EVIDENCE_INDEX with RELEASE-GO-001 entry")
else:
    print("EVIDENCE_INDEX already contains RELEASE-GO-001 entry")
PY

PYTHONPATH=. python3 scripts/patch_release_go_no_go_registry.py
PYTHONPATH=. python3 -c "from scripts.release_go_no_go import write_status; s = write_status(); print(s.decision)"
PYTHONPATH=. python3 scripts/check_release_go_no_go.py
pytest -c pytest.ini tests/unit/test_release_go_no_go.py -q --no-cov --tb=short
python3 -m compileall -q scripts tests
python3 -m ruff check scripts/release_go_no_go.py scripts/patch_release_go_no_go_registry.py scripts/check_release_go_no_go.py tests/unit/test_release_go_no_go.py --select F821,F401,F811,E402

if [ -f scripts/docs_inventory.py ]; then
  PYTHONPATH=. python3 scripts/docs_inventory.py --write || true
fi

echo "RELEASE-GO-001 / code_1831_1870 release-owner go/no-go status rollup batch is ready."
