#!/usr/bin/env python3
"""Audit RR-010 beta outcome reporting authority and final outcome files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-010"

AUTHORITY_DOCS = {
    "policy": Path("docs/beta_outcomes/rr010_beta_outcome_reporting_policy.md"),
    "manifest": Path("docs/beta_outcomes/rr010_beta_outcome_manifest.json"),
    "outcome_report_template": Path("docs/beta_outcomes/rr010_beta_outcome_report.template.md"),
    "metrics_summary_template": Path("docs/beta_outcomes/rr010_beta_metrics_summary.template.json"),
    "weekly_reviews_template": Path("docs/beta_outcomes/rr010_weekly_health_reviews.template.md"),
    "educator_feedback_template": Path("docs/beta_outcomes/rr010_educator_feedback_summary.template.md"),
    "incident_summary_template": Path("docs/beta_outcomes/rr010_incident_summary.template.md"),
}

FINAL_DOCS = {
    "outcome_report": Path("docs/beta_outcomes/rr010_beta_outcome_report.md"),
    "metrics_summary": Path("docs/beta_outcomes/rr010_beta_metrics_summary.json"),
    "weekly_reviews": Path("docs/beta_outcomes/rr010_weekly_health_reviews.md"),
    "educator_feedback": Path("docs/beta_outcomes/rr010_educator_feedback_summary.md"),
    "incident_summary": Path("docs/beta_outcomes/rr010_incident_summary.md"),
}

REQUIRED_AUTHORITY_MARKERS = {
    "policy": "Beta outcome reporting authority recorded: true",
    "outcome_report_template": "Beta outcome report template recorded: true",
    "weekly_reviews_template": "Weekly beta health review template recorded: true",
    "educator_feedback_template": "Educator feedback summary template recorded: true",
    "incident_summary_template": "Incident summary template recorded: true",
}

REQUIRED_FINAL_TEXT_MARKERS = {
    "outcome_report": (
        "Beta outcome report completed: true",
        "Minimum beta duration met: true",
        "Cohort size requirement met: true",
        "Weekly health reviews completed: true",
        "Beta outcome reporting complete: true",
        "Production release authorised: false",
        "Public beta authorised: false",
        "Runtime KG implementation claimed: false",
    ),
    "weekly_reviews": (
        "Weekly beta health reviews completed: true",
        "Minimum weekly review cadence met: true",
    ),
    "educator_feedback": (
        "Educator feedback collected: true",
        "Educator content approval threshold met: true",
    ),
    "incident_summary": (
        "Zero critical security incidents: true",
        "Zero PII exposure events: true",
        "Zero consent incidents: true",
    ),
}

REQUIRED_METRIC_FLAGS = (
    "minimum_beta_duration_met",
    "cohort_size_requirement_met",
    "educator_feedback_collected",
    "uptime_target_met",
    "p95_diagnostic_latency_target_met",
    "zero_critical_security_incidents",
    "zero_pii_exposure_events",
    "zero_consent_incidents",
    "educator_content_approval_threshold_met",
    "learner_session_completion_threshold_met",
    "backup_restore_drill_references_recorded",
    "weekly_health_reviews_completed",
)

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def _metric_number(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def audit(root: Path | str = Path("."), require_final: bool = False) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    authority_checks: dict[str, bool] = {}
    final_checks: dict[str, bool] = {}

    for key, rel in AUTHORITY_DOCS.items():
        exists = (root / rel).exists()
        authority_checks[f"{key}_exists"] = exists
        if not exists:
            errors.append(f"missing RR-010 authority document: {rel}")

    for key, marker in REQUIRED_AUTHORITY_MARKERS.items():
        contains = marker in _read(root, AUTHORITY_DOCS[key])
        authority_checks[f"{key}_marker_present"] = contains
        if not contains:
            errors.append(f"missing authority marker in {AUTHORITY_DOCS[key]}: {marker}")

    manifest = _json(root, AUTHORITY_DOCS["manifest"])
    if manifest.get("__json_error__"):
        errors.append(f"RR-010 manifest JSON invalid: {manifest['__json_error__']}")
    elif not manifest:
        errors.append("RR-010 manifest is missing")
    else:
        if manifest.get("rr_id") != RR_ID:
            errors.append("RR-010 manifest rr_id must be RR-010")
        for key in (
            "beta_outcome_reporting_authority_recorded",
            "minimum_beta_duration_required",
            "cohort_metrics_required",
            "educator_feedback_required",
            "uptime_latency_metrics_required",
            "security_pii_consent_incident_summary_required",
            "completion_rate_required",
            "backup_restore_drill_references_required",
            "weekly_health_reviews_required",
            "outcome_report_required",
        ):
            if manifest.get(key) is not True:
                errors.append(f"RR-010 manifest flag must be true: {key}")
        for key in BOUNDARY_FALSE_KEYS:
            if manifest.get(key) is not False:
                errors.append(f"RR-010 manifest boundary flag must be false: {key}")

    policy = _read(root, AUTHORITY_DOCS["policy"])
    if "RR-003" not in policy or "0.0" not in policy:
        errors.append("RR-010 policy must carry RR-003 fallback coverage caveat")
    if "RR-006" not in policy or "non-required" not in policy:
        errors.append("RR-010 policy must carry RR-006 non-required checks caveat")
    if "RR-015" not in policy or "RR-016" not in policy:
        errors.append("RR-010 policy must keep RR-015/RR-016 outstanding visible")
    if "public beta" not in policy.lower() or "not authorised" not in policy:
        errors.append("RR-010 policy must preserve public beta boundary")
    if "Runtime KG" not in policy or "not authorised" not in policy:
        errors.append("RR-010 policy must preserve runtime KG boundary")

    final_docs_present = all((root / rel).exists() for rel in FINAL_DOCS.values())
    final_checks["final_docs_present"] = final_docs_present
    if require_final and not final_docs_present:
        for key, rel in FINAL_DOCS.items():
            if not (root / rel).exists():
                errors.append(f"missing final RR-010 outcome file: {rel}")

    metrics = _json(root, FINAL_DOCS["metrics_summary"])
    if final_docs_present or require_final:
        for key, markers in REQUIRED_FINAL_TEXT_MARKERS.items():
            text = _read(root, FINAL_DOCS[key])
            for marker in markers:
                contains = marker in text
                final_checks[f"{key}:{marker}"] = contains
                if not contains:
                    errors.append(f"missing final marker in {FINAL_DOCS[key]}: {marker}")

        if metrics.get("__json_error__"):
            errors.append(f"RR-010 metrics summary JSON invalid: {metrics['__json_error__']}")
        elif not metrics:
            errors.append("RR-010 metrics summary is missing")
        else:
            if metrics.get("rr_id") != RR_ID:
                errors.append("RR-010 metrics rr_id must be RR-010")
            for key in REQUIRED_METRIC_FLAGS:
                if metrics.get(key) is not True:
                    errors.append(f"RR-010 metrics flag must be true: {key}")
            for key in BOUNDARY_FALSE_KEYS:
                if metrics.get(key) is not False:
                    errors.append(f"RR-010 metrics boundary flag must be false: {key}")

            checks = {
                "cohort_size_at_least_20": (_metric_number(metrics, "cohort_size") or 0) >= 20,
                "cohort_size_at_most_50": (_metric_number(metrics, "cohort_size") or 999999) <= 50,
                "beta_duration_at_least_28_days": (_metric_number(metrics, "beta_duration_days") or 0) >= 28,
                "uptime_at_least_99_5": (_metric_number(metrics, "uptime_percent") or 0) >= 99.5,
                "p95_diagnostic_latency_at_most_2s": (_metric_number(metrics, "p95_diagnostic_latency_seconds") or 999999) <= 2.0,
                "educator_content_approval_at_least_80": (_metric_number(metrics, "educator_content_approval_percent") or 0) >= 80,
                "learner_session_completion_at_least_70": (_metric_number(metrics, "learner_session_completion_percent") or 0) >= 70,
                "backup_restore_drills_at_least_two": (_metric_number(metrics, "backup_restore_drill_count") or 0) >= 2,
                "weekly_health_reviews_at_least_four": (_metric_number(metrics, "weekly_health_review_count") or 0) >= 4,
                "critical_security_incidents_zero": (_metric_number(metrics, "critical_security_incidents") or 0) == 0,
                "pii_exposure_events_zero": (_metric_number(metrics, "pii_exposure_events") or 0) == 0,
                "consent_incidents_zero": (_metric_number(metrics, "consent_incidents") or 0) == 0,
            }
            final_checks.update(checks)
            for key, passed in checks.items():
                if not passed:
                    errors.append(f"RR-010 numeric threshold failed: {key}")
    elif not final_docs_present:
        warnings.append("final beta outcome files are not present yet; authority can merge but evidence capture will fail until they exist")

    final_outputs_valid = final_docs_present and not any(
        error for error in errors if "authority" not in error.lower() and "manifest" not in error.lower() and "policy" not in error.lower()
    )

    return {
        "valid": not errors,
        "authority_valid": not [e for e in errors if not e.startswith("missing final") and "final marker" not in e and "metrics" not in e and "numeric threshold" not in e],
        "final_outputs_valid": final_outputs_valid,
        "errors": errors,
        "warnings": warnings,
        "authority_checks": authority_checks,
        "final_checks": final_checks,
        "metrics_summary": metrics if metrics else {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root), require_final=args.require_final)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-010 beta outcome audit:", "valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
