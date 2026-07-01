from __future__ import annotations

import json
import pathlib

from scripts.runtime_readiness.capture_controlled_beta_launch_activation_evidence import (
    build_result,
    validate_activation_documents,
)


def _write_valid_docs(root: pathlib.Path) -> dict[str, pathlib.Path]:
    go = root / "go.md"
    go.write_text(
        """# Go Decision\n\nDecision: go\nControlled beta launch authorised: true\nLive learner traffic authorised: true\nProduction release authorised: false\nPublic beta authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )
    cohort = root / "cohort.json"
    cohort.write_text(
        json.dumps(
            {
                "cohort_id": "cbeta-001",
                "controlled_beta_launch_authorised": True,
                "live_learner_traffic_authorised": True,
                "public_beta_authorised": False,
                "guardian_consent_required": True,
                "learner_count": 5,
                "max_allowed_learners": 50,
                "grades": [4],
                "subjects": ["Mathematics"],
                "launch_owner": "Nkgolo Lebelo",
                "support_owner": "Support Owner",
                "incident_commander": "Incident Owner",
                "data_protection_reviewer": "POPIA Reviewer",
                "rollback_owner": "Rollback Owner",
            }
        ),
        encoding="utf-8",
    )
    consent = root / "consent.md"
    consent.write_text(
        """# Consent Attestation\n\nGuardian consent reviewed: true\nPOPIA notice issued: true\nData export route reviewed: true\nRight-to-erasure route reviewed: true\nLearner data migration authorised: true\n""",
        encoding="utf-8",
    )
    traffic = root / "traffic.json"
    traffic.write_text(
        json.dumps(
            {
                "activation_start_utc": "2026-07-03T08:00:00Z",
                "activation_end_utc": "2026-07-03T12:00:00Z",
                "support_owner": "Support Owner",
                "incident_commander": "Incident Owner",
                "rollback_owner": "Rollback Owner",
                "monitoring_channel": "#beta-ops",
                "cohort_traffic_percentage": 100,
                "public_beta_authorised": False,
                "controlled_beta_launch_authorised": True,
                "live_learner_traffic_authorised": True,
            }
        ),
        encoding="utf-8",
    )
    return {"go": go, "cohort": cohort, "consent": consent, "traffic": traffic}


def test_valid_activation_documents(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    result = validate_activation_documents(
        go_no_go=docs["go"],
        cohort_manifest=docs["cohort"],
        consent_attestation=docs["consent"],
        traffic_window=docs["traffic"],
    )
    assert result["valid"] is True
    assert result["errors"] == []


def test_activation_documents_reject_public_beta(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    cohort_payload = json.loads(docs["cohort"].read_text(encoding="utf-8"))
    cohort_payload["public_beta_authorised"] = True
    docs["cohort"].write_text(json.dumps(cohort_payload), encoding="utf-8")
    result = validate_activation_documents(
        go_no_go=docs["go"],
        cohort_manifest=docs["cohort"],
        consent_attestation=docs["consent"],
        traffic_window=docs["traffic"],
    )
    assert result["valid"] is False
    assert any("public_beta_authorised" in error for error in result["errors"])


def test_build_result_requires_explicit_activation_flags() -> None:
    result = build_result(
        claimed=True,
        authorise_launch=True,
        authorise_live_traffic=False,
        authorise_migration=True,
        phase19={"valid": True},
        git={"tracked_worktree_clean_before_capture": True, "head_matches_remote_target": True},
        documents={"valid": True},
    )
    assert result["valid"] is False
    assert result["controlled_beta_launch_authorised"] is True
    assert result["live_learner_traffic_authorised"] is False


def test_build_result_preserves_non_production_boundaries() -> None:
    result = build_result(
        claimed=True,
        authorise_launch=True,
        authorise_live_traffic=True,
        authorise_migration=True,
        phase19={"valid": True},
        git={"tracked_worktree_clean_before_capture": True, "head_matches_remote_target": True},
        documents={"valid": True},
    )
    assert result["valid"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False
    assert result["controlled_beta_launch_authorised"] is True
    assert result["live_learner_traffic_authorised"] is True
    assert result["learner_data_migration_authorised"] is True
