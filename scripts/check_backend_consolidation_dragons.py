#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ["app", "tests", "scripts", "alembic"]


@dataclass(frozen=True)
class Finding:
    key: str
    count: int
    paths: list[str]


def _iter_text_files() -> list[Path]:
    paths: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".sql"}:
                paths.append(path)
    return paths


def _scan(pattern: str) -> Finding:
    regex = re.compile(pattern)
    count = 0
    matched_paths: list[str] = []
    for path in _iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        matches = regex.findall(text)
        if matches:
            count += len(matches)
            matched_paths.append(str(path.relative_to(REPO_ROOT)))
    return Finding(key=pattern, count=count, paths=sorted(set(matched_paths)))


def collect_findings() -> dict[str, Finding]:
    return {
        "audit_repository": _scan(r"\bAuditRepository\b"),
        "audit_events": _scan(r"\baudit_events\b"),
        "audit_logs": _scan(r"\baudit_logs\b"),
        "consent_records": _scan(r"\bconsent_records\b"),
        "parental_consents": _scan(r"\bparental_consents\b"),
        "consent_service": _scan(r"\bConsentService\b"),
        "deep_health": _scan(r"health/deep|deep health|check_audit_repository"),
    }


def main() -> int:
    print("Backend consolidation dragon diagnostic")
    findings = collect_findings()

    for name, finding in findings.items():
        print(f"- {name}: {finding.count} match(es)")
        for path in finding.paths[:12]:
            print(f"  - {path}")
        if len(finding.paths) > 12:
            print(f"  - ... {len(finding.paths) - 12} more file(s)")

    doc = REPO_ROOT / "docs" / "release" / "backend_consolidation_dragons.md"
    if not doc.exists():
        print(f"- FAIL documentation missing: {doc.relative_to(REPO_ROOT)}")
        return 1

    text = doc.read_text(encoding="utf-8")
    required = [
        "Split audit persistence",
        "Split consent persistence",
        "ORM/schema drift",
        "Health/readiness false positives",
        "Delete-first consolidation risk",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        print("- FAIL documentation missing required dragon headings: " + ", ".join(missing))
        return 1

    print("- PASS backend consolidation dragons documented and inventoried")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
