#!/usr/bin/env python3
"""Verify Technical Audit Phase 02H residual backend-fast contracts."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    name: str
    valid: bool
    detail: str


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def load_json(path: str) -> dict:
    p = ROOT / path
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def run_checks() -> list[Check]:
    consent = read("app/domain/consent.py")
    coverage = load_json("data/content_factory/coverage_targets.json")
    diag = read("scripts/diagnostic_score_live_audit.py")
    generation = read("app/api_v2_routers/generation.py")
    ops = read("scripts/validate_ops_assets.py")
    config = read("app/core/config.py")
    hygiene = read("scripts/maintenance/check_repo_hygiene.py")
    source_manifest = read("scripts/curriculum/validate_source_manifest.py")
    text_extracts = load_json("data/content_factory/source_text_extracts_manifest.json")
    topic_validate = read("scripts/curriculum/validate_topic_maps.py")
    worklist = read("scripts/curriculum/build_topic_map_worklist.py")
    auth = read("app/api_v2_routers/auth.py")
    jobs = read("app/modules/jobs.py")
    phase02e = read("scripts/audit_remediation/verify_backend_fast_phase02e.py")
    blueprint = read("app/services/content_generation/scope_blueprint_generator.py")
    project_status = read("docs/operations/project_assistance_status.md")
    blocker = read("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
    targets = {
        (row.get("scope_id"), row.get("caps_ref")): row.get("targets", {})
        for row in coverage.get("targets", [])
    }
    grade4_first = targets.get(("grade4_mathematics_en", "4.M.1.1"), {})
    records = text_extracts.get("records", []) if isinstance(text_extracts, dict) else []

    return [
        Check(
            "consent_expiry_uses_ceiling_days",
            "math.ceil(delta.total_seconds() / 86400)" in consent,
            "Consent expiry calculation is stable across sub-second test boundaries.",
        ),
        Check(
            "future_layer_targets_restored",
            grade4_first.get("assessment_blueprints.approved") == 4
            and grade4_first.get("study_plan_templates.approved") == 3,
            "Grade 4 future-layer coverage targets match backend-fast contract.",
        ),
        Check(
            "diagnostic_score_item_id_generated",
            'if name == "item_id" and "id" in irt_columns:' in diag and 'return "gen_random_uuid()"' in diag,
            "Diagnostic bridge generates target item_id rather than copying IRT id.",
        ),
        Check(
            "generation_cancel_enveloped",
            "from app.domain.api_v2_models import ok" in generation and "return ok({\"run_id\":" in generation,
            "Generation cancel response uses V2 envelope helper.",
        ),
        Check(
            "ops_python_pin_matches_v2_dockerfile",
            "FROM python:3.12.3-slim" in ops,
            "Ops validator expects the V2 Docker Python base pin.",
        ),
        Check(
            "production_key_vault_fails_closed",
            'raise ValueError("AZURE_KEY_VAULT_URL is required when APP_ENV is production")' in config
            and "_production_key_vault_url_required" in config,
            "Production settings require Key Vault URL before fetching secrets.",
        ),
        Check(
            "repo_hygiene_root_operational_files_allowed",
            "'.gitleaks.toml'" in hygiene and "'Memory.md'" in hygiene and "'pnpm-lock.yaml'" in hygiene,
            "Known operational root files are explicitly allowed.",
        ),
        Check(
            "source_manifest_object_store_cache_boundary",
            "local cache missing; object store URI recorded" in source_manifest,
            "Source-manifest local file verification tolerates object-store-backed clean checkouts.",
        ),
        Check(
            "grade7_math_text_extract_hash_recorded",
            any(record.get("document_id") == "caps_senior_mathematics_en" and record.get("text_sha256") == "881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33" for record in records),
            "Grade 7 mathematics text extract hash is recorded for topic-map worklist evidence.",
        ),
        Check(
            "topic_map_draft_fallback",
            "result.draft_status_summary[\"draft_reviewed\"] = reviewed_scope_count" in topic_validate,
            "Topic-map validator preserves reviewed-draft counts when generated draft envelopes are absent.",
        ),
        Check(
            "topic_worklist_text_sha_fallback",
            "record[\"text_sha256\"] if record" in worklist and "_document_hash(document)" in worklist,
            "Topic-map worklist preserves text/source hashes for registered source documents.",
        ),
        Check(
            "auth_revoke_all_dict_compatible",
            'current_user.raw_claims if hasattr(current_user, "raw_claims") else current_user' in auth,
            "Auth revoke-all accepts both AuthContext and legacy dict test claims.",
        ),
        Check(
            "jobs_use_session_factory_alias",
            "AsyncSessionLocal" not in jobs and "AsyncSessionFactory" in jobs,
            "ARQ jobs use the canonical session factory alias, not direct AsyncSessionLocal references.",
        ),
        Check(
            "phase02e_verifier_history_survives_slice_advance",
            '"phase_02e_slice" in blocker' in phase02e,
            "Phase 02E verifier checks historical registration instead of active-slice ownership.",
        ),
        Check(
            "blueprint_generator_baseline_plus_three_per_ref",
            "self._recheck(" not in blueprint.split("blueprints.extend", 1)[1].split("return {", 1)[0]
            and "self._mastery_check(" in blueprint,
            "Scope blueprint generation yields baseline plus three approved blueprints per CAPS ref.",
        ),
        Check(
            "project_assistance_status_regenerated",
            "Project Assistance Status" in project_status and "Current Gate Snapshot" in project_status,
            "Project assistance report is regenerated for current source state.",
        ),
        Check(
            "phase02h_registered",
            "02h-backend-fast-residual-contracts" in blocker,
            "Blocker register records Phase 02H as the current backend-fast remediation slice.",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checks = run_checks()
    payload = {
        "valid": all(check.valid for check in checks),
        "checks": [asdict(check) for check in checks],
        "policy": "Phase 02H focused evidence only; backend-fast candidate evidence requires make test-fast exit 0.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for check in checks:
            print(f"{'PASS' if check.valid else 'FAIL'} {check.name}: {check.detail}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
