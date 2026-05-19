from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CI_EVIDENCE = ROOT / "docs/release/ci_evidence.md"
CI_STATUS_JSON = ROOT / "docs/release/ci_authority_status.json"
CI_STATUS_MD = ROOT / "docs/release/ci_authority_status.md"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

REQUIRED_LOCAL_TARGETS = [
    "backend-implementation-1071-1110-full-check",
    "backend-implementation-1111-1150-full-check",
    "backend-implementation-1191-1230-full-check",
    "backend-implementation-1231-1270-full-check",
    "backend-implementation-1271-1310-full-check",
    "backend-implementation-1351-1390R-full-check",
    "backend-implementation-1591-1630-full-check",
    "backend-implementation-1631-1670-full-check",
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "pytest",
    "ruff",
]


@dataclass(frozen=True)
class CIAuthorityStatus:
    generated_at: str
    current_commit: str
    workflow_files: list[str]
    workflow_present: bool
    workflow_mentions_required_snippets: bool
    ci_evidence_file_exists: bool
    ci_run_url: str | None
    ci_run_url_present: bool
    ci_status: str
    required_local_targets_present: list[str]
    missing_local_targets: list[str]
    remaining_blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def workflow_files() -> list[Path]:
    return sorted((ROOT / ".github/workflows").glob("*.yml")) + sorted((ROOT / ".github/workflows").glob("*.yaml"))


def workflow_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def ci_run_url_from_evidence() -> str | None:
    if not CI_EVIDENCE.exists():
        return None
    text = CI_EVIDENCE.read_text(encoding="utf-8")
    match = re.search(r"https://github\.com/[^\s)]+/actions/runs/\d+", text)
    if match:
        return match.group(0)
    return None


def makefile_targets() -> set[str]:
    makefile = ROOT / "Makefile"
    if not makefile.exists():
        return set()
    targets: set[str] = set()
    for line in makefile.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("\t") and ":" in line:
            target = line.split(":", 1)[0].strip()
            if target:
                targets.add(target)
    return targets


def build_status() -> CIAuthorityStatus:
    workflows = workflow_files()
    text = workflow_text(workflows)
    targets = makefile_targets()
    present_targets = [target for target in REQUIRED_LOCAL_TARGETS if target in targets]
    missing_targets = [target for target in REQUIRED_LOCAL_TARGETS if target not in targets]
    url = ci_run_url_from_evidence()

    blockers: list[str] = []
    if not workflows:
        blockers.append("No GitHub Actions workflow file found under .github/workflows")
    if workflows and not all(snippet in text for snippet in REQUIRED_WORKFLOW_SNIPPETS):
        blockers.append("Workflow file does not mention every required local CI-equivalent command family")
    if missing_targets:
        blockers.append("Missing local CI-equivalent Makefile targets: " + ", ".join(missing_targets))
    if not url:
        blockers.append("No GitHub Actions run URL recorded in docs/release/ci_evidence.md")

    return CIAuthorityStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        workflow_files=[str(path.relative_to(ROOT)) for path in workflows],
        workflow_present=bool(workflows),
        workflow_mentions_required_snippets=bool(workflows) and all(snippet in text for snippet in REQUIRED_WORKFLOW_SNIPPETS),
        ci_evidence_file_exists=CI_EVIDENCE.exists(),
        ci_run_url=url,
        ci_run_url_present=url is not None,
        ci_status="remote-ci-authoritative" if url and not missing_targets and workflows else "external-blocked",
        required_local_targets_present=present_targets,
        missing_local_targets=missing_targets,
        remaining_blockers=blockers,
    )


def write_ci_evidence_template() -> None:
    if CI_EVIDENCE.exists():
        text = CI_EVIDENCE.read_text(encoding="utf-8")
        if "CI-001" in text:
            return

    CI_EVIDENCE.write_text(
        "\n".join(
            [
                "# CI Authority Evidence",
                "",
                "**Item:** CI-001",
                "",
                "**Status:** external-blocked",
                "",
                "This file must be updated with an actual GitHub Actions run URL before CI-001 can move beyond `external-blocked`.",
                "",
                "## Required evidence",
                "",
                "- Repository: `NkgoloL/Eduboost-V2`",
                "- Branch: `codex/production_readiness`",
                "- Commit SHA: `PENDING`",
                "- GitHub Actions run URL: `PENDING`",
                "- Result: `PENDING`",
                "- Date verified: `PENDING`",
                "",
                "## Local CI-equivalent commands",
                "",
                "```bash",
                "make backend-implementation-1071-1110-full-check",
                "make backend-implementation-1111-1150-full-check",
                "make backend-implementation-1191-1230-full-check",
                "make backend-implementation-1231-1270-full-check",
                "make backend-implementation-1271-1310-full-check",
                "make backend-implementation-1351-1390R-full-check",
                "make backend-implementation-1591-1630-full-check",
                "make backend-implementation-1631-1670-full-check",
                "pytest -c pytest.ini -q --no-cov",
                "```",
                "",
                "## No false closure rule",
                "",
                "Local command success is not remote CI authority. CI-001 remains `external-blocked` until an actual GitHub Actions run URL is attached.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_status() -> CIAuthorityStatus:
    write_ci_evidence_template()
    status = build_status()
    CI_STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# CI Authority Status",
        "",
        f"Generated at: `{status.generated_at}`",
        "",
        f"**Status:** `{status.ci_status}`",
        "",
        f"- Current commit: `{status.current_commit}`",
        f"- Workflow files: `{status.workflow_files}`",
        f"- CI evidence file exists: `{status.ci_evidence_file_exists}`",
        f"- CI run URL present: `{status.ci_run_url_present}`",
        f"- CI run URL: `{status.ci_run_url or 'PENDING'}`",
        "",
        "## Local CI-equivalent target coverage",
        "",
        "| Target | Present |",
        "|---|---:|",
    ]
    present = set(status.required_local_targets_present)
    for target in REQUIRED_LOCAL_TARGETS:
        lines.append(f"| `{target}` | {target in present} |")

    lines.extend(["", "## Remaining blockers", ""])
    if status.remaining_blockers:
        lines.extend(f"- {blocker}" for blocker in status.remaining_blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This status is a release-governance check. It must not be used to claim remote CI success unless a real GitHub Actions run URL is present.",
            "",
        ]
    )
    CI_STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def registry_ci_status() -> str | None:
    if not REGISTRY.exists():
        return None
    text = REGISTRY.read_text(encoding="utf-8")
    marker = "id: CI-001"
    index = text.find(marker)
    if index < 0:
        return None
    next_index = text.find("\n  - id:", index + 1)
    block = text[index:] if next_index < 0 else text[index:next_index]
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("proof_status:"):
            return stripped.split(":", 1)[1].strip()
    return None
