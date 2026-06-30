#!/usr/bin/env python3
"""Validate staging/operations evidence for the release PR series."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "staging_operations_evidence_2026-05-11.md"
MAKEFILE = REPO_ROOT / "Makefile"

REQUIRED_DOC_SNIPPETS = (
    "Staging And Operations Evidence",
    "codex/pr22-staging-operations-evidence",
    "make staging-operations-release-evidence-check staging-release-gate-check cicd-staging-check release-evidence-artifacts-check post-deploy-staging-smoke-check staging-smoke-evidence-manifest-check observability-ops-check release-state-snapshot-check release-candidate-tag-manifest-check",
    "Staging release gate documentation and required artifacts are present",
    "Post-deploy staging smoke checklist covers backend, security/compliance, data resilience, AI safety, and frontend smoke checks",
    "Observability/ops evidence references metrics, structured logging, incident response, support model, Prometheus, Grafana, Alertmanager, and focused tests",
    "No live staging deployment was executed in this PR",
    "Release tags must not be created or pushed until Cluster H checks and manual sign-offs pass",
    "does not claim live staging readiness, production observability readiness, release tag approval, or production promotion approval",
)

REQUIRED_MAKE_TARGETS = (
    "post-deploy-staging-smoke-checklist-check:",
    "post-deploy-staging-smoke-check:",
    "staging-smoke-evidence-manifest-check:",
    "observability-ops-check:",
    "release-state-snapshot-check:",
    "release-candidate-tag-manifest-check:",
    "staging-operations-release-evidence-check:",
)


def _check(label: str, text: str, snippets: tuple[str, ...]) -> bool:
    ok = True
    for snippet in snippets:
        if snippet in text:
            print(f"- PASS {label}: contains {snippet!r}")
            continue
        print(f"- FAIL {label}: missing {snippet!r}")
        ok = False
    return ok


def main() -> int:
    print("Staging/operations release evidence check")
    ok = True

    if DOC.exists():
        print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    else:
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        ok = False

    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    ok = _check(str(DOC.relative_to(REPO_ROOT)), doc_text, REQUIRED_DOC_SNIPPETS) and ok
    ok = _check(str(MAKEFILE.relative_to(REPO_ROOT)), makefile_text, REQUIRED_MAKE_TARGETS) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
