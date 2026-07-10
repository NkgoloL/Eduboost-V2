"""PRD-11.0-11.4 production release/deployment preflight readiness."""
from __future__ import annotations

from dataclasses import dataclass, field

PRD_ID = "PRD-11.0-11.4"

PRODUCTION_RELEASE_PREFLIGHT_CONTROLS = (
    "prd11_authority_and_release_gate_definition",
    "release_candidate_artifact_and_version_contract",
    "release_tag_freeze_and_changelog_gate",
    "deployment_environment_secret_and_config_preflight",
    "database_migration_and_rollback_preflight",
    "controlled_beta_to_production_go_no_go_gate",
    "support_monitoring_incident_and_release_comms_gate",
    "production_release_dry_run_evidence_gate",
)

PRODUCTION_RELEASE_BOUNDARIES = {
    "prd12_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
}


@dataclass(frozen=True)
class ProductionReleasePreflightReport:
    """Deterministic PRD-11.0-11.4 production release preflight contract.

    The report acknowledges that PRD-10 authorised limited controlled-beta live
    learner traffic. It does not authorise public beta, general availability,
    production deployment, release tagging, billing launch, or live payments.
    """

    accepted: bool = True
    prd_id: str = PRD_ID
    controls: tuple[str, ...] = PRODUCTION_RELEASE_PREFLIGHT_CONTROLS
    blockers: tuple[str, ...] = field(default_factory=tuple)
    release_scope: str = "production_release_preflight_only"
    controlled_beta_state: str = "limited_controlled_beta_live_traffic_already_authorised_by_prd10"
    release_candidate_gate_state: str = "defined_not_authorised"
    deployment_gate_state: str = "defined_not_authorised"
    migration_rollback_gate_state: str = "defined_not_authorised"
    go_no_go_gate_state: str = "defined_not_authorised"
    production_release_final_handoff_authorised: bool = False
    controlled_beta_live_traffic_authorised: bool = True
    live_learner_traffic_authorised: bool = True
    boundaries: dict[str, bool] = field(default_factory=lambda: dict(PRODUCTION_RELEASE_BOUNDARIES))

    def to_payload(self) -> dict:
        return {
            "prd_id": self.prd_id,
            "accepted": self.accepted,
            "controls": list(self.controls),
            "blockers": list(self.blockers),
            "release_scope": self.release_scope,
            "controlled_beta_state": self.controlled_beta_state,
            "release_candidate_gate_state": self.release_candidate_gate_state,
            "deployment_gate_state": self.deployment_gate_state,
            "migration_rollback_gate_state": self.migration_rollback_gate_state,
            "go_no_go_gate_state": self.go_no_go_gate_state,
            "production_release_preflight_defined": self.accepted,
            "release_candidate_artifact_gate_defined": self.accepted,
            "release_tag_freeze_gate_defined": self.accepted,
            "deployment_environment_preflight_defined": self.accepted,
            "secrets_config_preflight_defined": self.accepted,
            "database_migration_rollback_gate_defined": self.accepted,
            "controlled_beta_to_production_go_no_go_defined": self.accepted,
            "support_monitoring_incident_release_comms_defined": self.accepted,
            "production_release_dry_run_gate_defined": self.accepted,
            "production_release_final_handoff_authorised": self.production_release_final_handoff_authorised,
            "controlled_beta_live_traffic_authorised": self.controlled_beta_live_traffic_authorised,
            "live_learner_traffic_authorised": self.live_learner_traffic_authorised,
            **self.boundaries,
        }


def build_default_production_release_preflight_report() -> ProductionReleasePreflightReport:
    return ProductionReleasePreflightReport()


def build_blocked_production_release_preflight_report() -> ProductionReleasePreflightReport:
    return ProductionReleasePreflightReport(
        accepted=False,
        blockers=("production_release_preflight_incomplete",),
        release_scope="blocked",
        controlled_beta_live_traffic_authorised=False,
        live_learner_traffic_authorised=False,
    )
