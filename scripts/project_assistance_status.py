#!/usr/bin/env python3
"""Generate the five-lane project assistance status report."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "project_assistance_status.md"


@dataclass(frozen=True)
class AssistanceLane:
    number: int
    name: str
    purpose: str
    sources: tuple[str, ...]
    commands: tuple[str, ...]
    output: str
    done_when: str


LANES: tuple[AssistanceLane, ...] = (
    AssistanceLane(
        1,
        "Current-state triage",
        "Keep the project honest about what is implemented, verified, blocked, or external.",
        ("docs/current_state.md", "docs/project_status.md", "TODO.md"),
        ("make refresh-current-state", "make project-assistance-status"),
        "Updated project status and current-state evidence.",
        "Open blockers are reflected in TODO.md and no release-ready claim exceeds the evidence.",
    ),
    AssistanceLane(
        2,
        "Verification and repair",
        "Run focused checks, repair failures, and capture the exact command evidence.",
        ("Makefile", "pytest.ini", "docs/current_state.md"),
        ("pytest -c pytest.ini tests/unit -q --no-cov", "make runtime-check", "make openapi-check"),
        "Passing local checks or a concrete failure record with owner and next action.",
        "The relevant failing gate is either green or documented as blocked with evidence.",
    ),
    AssistanceLane(
        3,
        "Release evidence and governance",
        "Maintain release evidence bundles, owner accountability, and claim discipline.",
        (
            "docs/operations/recommended_operating_model.md",
            "docs/release/EVIDENCE_INDEX.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ),
        (
            "make recommended-operating-model-check",
            "make release-owner-accountability-check",
            "make beta-release-readiness-contract-check",
        ),
        "Release evidence files that link to real, readable artifacts.",
        "Release decisions are backed by current evidence and unsigned external approvals stay external.",
    ),
    AssistanceLane(
        4,
        "Architecture, security, and compliance hardening",
        "Protect V2 boundaries, authorization, POPIA, and AI/CAPS safety claims.",
        ("app/", "docs/security/", "docs/POPIA_COMPLIANCE.md"),
        ("make architecture-gates", "make privacy-boundary-check", "make caps-ai-safety-evidence-check"),
        "Boundary fixes, security evidence, or explicit scoped exceptions.",
        "Security, privacy, and architecture claims match passing checks or documented exceptions.",
    ),
    AssistanceLane(
        5,
        "Staging, beta, and operational readiness",
        "Prepare deployment, smoke, backup, restore, rollback, and beta go/no-go evidence.",
        ("docs/operations/", "docs/release/", ".github/workflows/"),
        ("make staging-smoke-check", "make local-release-evidence-check", "make beta-release-evidence-bundle-check"),
        "Staging and beta readiness records with commands, outputs, owners, and dates.",
        "A release owner can make an evidence-backed go/no-go decision without guessing.",
    ),
)


def _path_status(path: str) -> str:
    candidate = REPO_ROOT / path
    if candidate.exists():
        return "present"
    return "missing"


def _current_gate_summary() -> list[str]:
    current_state = REPO_ROOT / "docs" / "current_state.md"
    if not current_state.exists():
        return ["- `docs/current_state.md` is missing."]

    lines = current_state.read_text(encoding="utf-8").splitlines()
    wanted_prefixes = ("**Last refreshed:**", "**Assessed commit:**", "**Quality gate:**")
    summary = [f"- {line.strip()}" for line in lines if line.strip().startswith(wanted_prefixes)]
    return summary or ["- Current-state summary markers were not found."]


def build_report() -> str:
    lines: list[str] = [
        "# Project Assistance Status",
        "",
        "This report implements the five ways Codex assists this project. It is a",
        "working control surface, not a release approval.",
        "",
        "## Current Gate Snapshot",
        "",
        *_current_gate_summary(),
        "",
        "## Source Coverage",
        "",
        "| Source | Status |",
        "| --- | --- |",
    ]

    sources = sorted({source for lane in LANES for source in lane.sources})
    for source in sources:
        lines.append(f"| `{source}` | {_path_status(source)} |")

    lines.extend(
        [
            "",
            "## Assistance Lanes",
            "",
            "| # | Lane | Primary output | First command |",
            "| --- | --- | --- | --- |",
        ]
    )
    for lane in LANES:
        lines.append(f"| {lane.number} | {lane.name} | {lane.output} | `{lane.commands[0]}` |")

    for lane in LANES:
        lines.extend(
            [
                "",
                f"## {lane.number}. {lane.name}",
                "",
                lane.purpose,
                "",
                "Sources:",
            ]
        )
        lines.extend(f"- `{source}` ({_path_status(source)})" for source in lane.sources)
        lines.extend(["", "Commands:"])
        lines.extend(f"- `{command}`" for command in lane.commands)
        lines.extend(["", f"Done when: {lane.done_when}"])

    lines.extend(
        [
            "",
            "## Maintenance",
            "",
            "Run this after meaningful status, evidence, release, or readiness changes:",
            "",
            "```bash",
            "make project-assistance-status",
            "make project-assistance-status-check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_report() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_report(), encoding="utf-8")


def check_report() -> bool:
    expected = build_report()
    actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
    return actual == expected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated report is stale")
    args = parser.parse_args(argv)

    if args.check:
        if check_report():
            print("Project assistance status is current")
            return 0
        print("Project assistance status is stale; run make project-assistance-status")
        return 1

    write_report()
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
