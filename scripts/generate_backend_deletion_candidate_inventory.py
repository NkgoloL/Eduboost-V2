#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "release" / "backend_deletion_candidate_inventory.md"
SCAN_ROOTS = ("app", "tests", "scripts", "alembic", "docs/release")
CANDIDATE_PATTERNS = [
    ("legacy_audit", re.compile(r"audit_logs|AuditLog|legacy audit", re.IGNORECASE)),
    ("legacy_consent", re.compile(r"parental_consents|ParentalConsent|legacy consent", re.IGNORECASE)),
    ("duplicate_repository", re.compile(r"class\s+\w*Repository|AuditRepository|ConsentRepository")),
    ("compat_adapter", re.compile(r"Compat|compatibility|adapter", re.IGNORECASE)),
]

@dataclass(frozen=True)
class Candidate:
    path: str
    line: int
    category: str
    text: str

def _iter_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".sql"}:
                files.append(path)
    return sorted(files)

def collect_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    for path in _iter_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for category, pattern in CANDIDATE_PATTERNS:
                if pattern.search(line):
                    candidates.append(Candidate(str(path.relative_to(REPO_ROOT)), line_number, category, line.strip()[:220]))
    return candidates

def render(candidates: list[Candidate]) -> str:
    lines = [
        "# Backend Deletion Candidate Inventory",
        "",
        "This inventory is diagnostic only. It does not approve deletion.",
        "",
        "| Path | Line | Category | Text | Replacement owner | Approved? |",
        "|---|---:|---|---|---|---|",
    ]
    for candidate in candidates:
        text = candidate.text.replace("|", "\\|")
        lines.append(f"| `{candidate.path}` | {candidate.line} | {candidate.category} | `{text}` | TODO | no |")
    lines.extend([
        "",
        "## Deletion criteria",
        "",
        "- [ ] Replacement owner identified.",
        "- [ ] Call sites migrated.",
        "- [ ] Historical data retention decision recorded.",
        "- [ ] Migration evidence captured if schema/data is affected.",
        "- [ ] Full local and CI tests are green.",
        "- [ ] Release owner explicitly approves deletion.",
        "",
    ])
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--fail-empty", action="store_true")
    args = parser.parse_args()
    candidates = collect_candidates()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(candidates), encoding="utf-8")
    print(f"Wrote {output} ({len(candidates)} candidate row(s))")
    if args.fail_empty and not candidates:
        print("No deletion candidates found")
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
