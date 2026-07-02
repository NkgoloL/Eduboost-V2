from __future__ import annotations

import json
import pathlib

from scripts.runtime_readiness.capture_controlled_beta_launch_monitoring_evidence import (
    build_result,
    validate_monitoring_documents,
)


def _write_valid_docs(root: pathlib.Path) -> dict[str, pathlib.Path]:
    report = root / "monitoring.md"
    report.write_text(
        """# Monitoring Report

Controlled beta monitoring complete: true
Live learner traffic observed: true
No critical incidents: true
Rollback required: false
Production release authorised: false
Public beta authorised: false
Runtime KG implementation claimed: false
""",
        encoding="utf-8",
    )
    support = root / "support.json"
    support.write_text(
        json.dumps(
            {
                "support_owner": "Support Owner",
                "support_channel": "#beta-ops",
                "total_tickets": 2,
                "unresolved_p0_tickets": 0,
                "unresolved_p1_tickets": 0,
                "controlled_beta_launch_authorised": True,
                "public_beta_authorised": False,
            }
        ),
        encoding="utf-8",
    )
    incidents = root / "incidents.json"
    incidents.write_text(
        json.dumps(
            {
                "incident_commander": "Incident Owner",
                "open_p0_incidents": 0,
                "open_p1_incidents": 0,
                "critical_incidents_open": False,
                "rollback_required": False,
                "production_release_authorised": False,
                "incidents": [],
            }
        ),
        encoding="utf-8",
    )
    rollback = root / "rollback.md"
    rollback.write_text(
        """# Rollback Decision

Rollback reviewed: true
Rollback required: false
Controlled beta continuation authorised: true
Production release authorised: false
Public beta authorised: false
""",
        encoding="utf-8",
    )
    metrics = root / "metrics.json"
    metrics.write_text(
        json.dumps(
            {
                "live_learner_traffic_observed": True,
                "health_checks_green": True,
                "seeded_e2e_regression_green": True,
                "error_budget_breached": False,
                "data_rights_routes_available": True,
            }
        ),
        encoding="utf-8",
    )
    return {
        "report": report,
        "support": support,
        "incidents": incidents,
        "rollback": rollback,
        "metrics": metrics,
    }


def test_valid_monitoring_documents(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    result = validate_monitoring_documents(
        monitoring_report=docs["report"],
        support_log=docs["support"],
        incident_log=docs["incidents"],
        rollback_decision=docs["rollback"],
        metrics_snapshot=docs["metrics"],
    )
    assert result["valid"] is True
    assert result["errors"] == []


def test_monitoring_documents_reject_public_beta(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    docs["report"].write_text(docs["report"].read_text(encoding="utf-8").replace("Public beta authorised: false", "Public beta authorised: true"), encoding="utf-8")
    result = validate_monitoring_documents(
        monitoring_report=docs["report"],
        support_log=docs["support"],
        incident_log=docs["incidents"],
        rollback_decision=docs["rollback"],
        metrics_snapshot=docs["metrics"],
    )
    assert result["valid"] is False
    assert any("Public beta authorised: false" in error for error in result["errors"])


def test_monitoring_documents_reject_open_p0_incident(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    payload = json.loads(docs["incidents"].read_text(encoding="utf-8"))
    payload["open_p0_incidents"] = 1
    payload["critical_incidents_open"] = True
    docs["incidents"].write_text(json.dumps(payload), encoding="utf-8")
    result = validate_monitoring_documents(
        monitoring_report=docs["report"],
        support_log=docs["support"],
        incident_log=docs["incidents"],
        rollback_decision=docs["rollback"],
        metrics_snapshot=docs["metrics"],
    )
    assert result["valid"] is False
    assert "incident log open_p0_incidents must be 0" in result["errors"]
    assert "incident log critical_incidents_open must be false" in result["errors"]


def test_build_result_preserves_boundaries(tmp_path: pathlib.Path) -> None:
    docs = _write_valid_docs(tmp_path)
    validation = validate_monitoring_documents(
        monitoring_report=docs["report"],
        support_log=docs["support"],
        incident_log=docs["incidents"],
        rollback_decision=docs["rollback"],
        metrics_snapshot=docs["metrics"],
    )
    result = build_result(
        claim_monitoring=True,
        monitoring_owner="Nkgolo Lebelo",
        target_branch="master",
        phase20_verification={"valid": True},
        monitoring_documents=validation,
        source_sha="abc123",
        captured_at="2026-07-02T00:00:00Z",
    )
    assert result["status"] == "controlled_beta_launch_monitoring_recorded"
    assert result["controlled_beta_launch_monitoring_recorded"] is True
    assert result["live_learner_traffic_observed"] is True
    assert result["controlled_beta_continuation_authorised"] is True
    assert result["controlled_beta_launch_authorised"] is True
    assert result["production_release_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False
