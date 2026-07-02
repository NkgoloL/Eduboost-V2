#!/usr/bin/env python3
"""Build a structured report from a failed backend fast-gate log."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]

MODULE_NOT_FOUND_RE = re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]")
IMPORT_ERROR_RE = re.compile(r"ImportError: ([^\n]+)")
FAILED_OR_ERROR_RE = re.compile(r"^(FAILED|ERROR)\s+([^\s]+)", re.MULTILINE)
SUMMARY_RE = re.compile(r"(?P<count>\d+)\s+(?P<kind>failed|errors?|passed|skipped|xfailed|xpassed)")

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "popia": ("popia", "erasure", "data_rights", "data-rights", "restriction"),
    "openapi": ("openapi", "schema-drift", "route_contract"),
    "database_migration": ("database", "migration", "alembic", "schema_integrity", "sqlalchemy"),
    "content_factory": ("content_factory", "content factory", "scope_content", "launch_content"),
    "auth_security": ("auth", "jwt", "token", "security", "authorization"),
    "diagnostics": ("diagnostic", "irt", "item_bank"),
    "lessons_generation": ("lesson", "generation", "llm", "prompt"),
    "phase02r_grounding": ("phase02r", "grounding", "curriculum", "corpus", "tutor"),
}


def _load_classifier(root: Path) -> Callable[[str], dict[str, Any]] | None:
    classifier_path = root / "scripts/audit_remediation/classify_backend_fast_failures.py"
    if not classifier_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("classify_backend_fast_failures", classifier_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "classify_text", None)


def _summary_counts(text: str) -> dict[str, int]:
    summary: dict[str, int] = {}
    for match in SUMMARY_RE.finditer(text):
        kind = match.group("kind")
        if kind == "error":
            kind = "errors"
        summary[kind] = summary.get(kind, 0) + int(match.group("count"))
    return summary


def _domain_counts(failed_tests: list[str], text: str) -> dict[str, int]:
    counts = {domain: 0 for domain in DOMAIN_KEYWORDS}
    haystacks = failed_tests or text.splitlines()
    for value in haystacks:
        lower = value.lower()
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(keyword in lower for keyword in keywords):
                counts[domain] += 1
    return {domain: count for domain, count in counts.items() if count}


def _recommendations(categories: list[str], missing_modules: list[str], domain_counts: dict[str, int]) -> list[str]:
    recommendations: list[str] = []
    if missing_modules or "dependency_or_import" in categories:
        recommendations.append("Install and verify requirements/dev.txt in the authority Python environment before re-running make test-fast.")
    if "database_or_migration" in categories or domain_counts.get("database_migration"):
        recommendations.append("Separate import-time database engine creation from model imports or ensure test DATABASE_URL uses an installed driver.")
    if "popia_auth_or_route_contract" in categories or domain_counts.get("popia"):
        recommendations.append("Run focused POPIA unit tests and router contract tests before full backend-fast retry.")
    if "openapi_route_contract" in categories or domain_counts.get("openapi"):
        recommendations.append("Run OpenAPI route-contract verifier and regenerate docs/openapi.json before full backend-fast retry.")
    if domain_counts.get("content_factory"):
        recommendations.append("Verify Content Factory registries and generated fixture assumptions before full backend-fast retry.")
    if not recommendations:
        recommendations.append("Inspect the failed tests list and split the next remediation package by the largest domain cluster.")
    return recommendations


def find_backend_fast_log(path: Path) -> Path:
    if path.exists() and not path.is_dir():
        return path
    candidates = [
        path / "raw/backend_fast_gate.txt",
        path / "backend_fast_gate.txt",
        path / "backend-fast-gate/raw/backend_fast_gate.txt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = sorted(path.rglob("backend_fast_gate.txt"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Could not find backend_fast_gate.txt under {path}")


def build_report(text: str, *, root: Path = ROOT, source: str | None = None) -> dict[str, Any]:
    classifier = _load_classifier(root)
    base = classifier(text) if classifier else {"category_names": [], "failed_tests": [], "summary_counts": _summary_counts(text)}
    failed_tests = list(base.get("failed_tests") or [match.group(2) for match in FAILED_OR_ERROR_RE.finditer(text)])
    missing_modules = sorted(set(MODULE_NOT_FOUND_RE.findall(text)))
    import_errors = sorted(set(IMPORT_ERROR_RE.findall(text)))[:50]
    domain_counts = _domain_counts(failed_tests, text)
    category_names = sorted(set(base.get("category_names") or []))
    summary_counts = dict(base.get("summary_counts") or _summary_counts(text))
    failure_count = int(base.get("failure_count") or summary_counts.get("failed", 0) + summary_counts.get("errors", 0) or len(failed_tests))
    return {
        "valid": failure_count == 0,
        "source": source,
        "summary_counts": summary_counts,
        "failure_count": failure_count,
        "category_names": category_names,
        "domain_counts": domain_counts,
        "missing_modules": missing_modules,
        "import_errors": import_errors,
        "failed_tests_sample": failed_tests[:100],
        "failed_test_count_detected": len(failed_tests),
        "recommendations": _recommendations(category_names, missing_modules, domain_counts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="backend_fast_gate.txt or failed evidence directory; stdin when omitted")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    source = None
    if args.input:
        log_path = find_backend_fast_log(args.input.resolve())
        source = str(log_path)
        text = log_path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    report = build_report(text, root=args.root.resolve(), source=source)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST FAILURE REPORT")
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
