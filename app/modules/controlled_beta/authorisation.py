"""PRD-10.5-10.9 controlled beta final live-traffic authorisation."""
from __future__ import annotations

from dataclasses import dataclass, field

PRD_ID = "PRD-10.5-10.9"

FINAL_AUTHORISATION_CONTROLS = (
    "controlled_beta_final_evidence_acceptance",
    "cohort_guardian_consent_and_learner_eligibility_acceptance",
    "auth_token_regression_and_pyjwt_migration_acceptance",
    "live_learner_traffic_dry_run_acceptance",
    "kill_switch_and_rollback_drill_acceptance",
    "beta_support_monitoring_and_incident_escalation_acceptance",
    "go_no_go_decision_for_controlled_beta_live_traffic",
    "prd11_handoff_readiness",
)

LOCKED_FALSE_BOUNDARIES = {
    "prd11_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
}


@dataclass(frozen=True)
class ControlledBetaFinalAuthorisationReport:
    prd_id: str = PRD_ID
    accepted: bool = True
    controls: tuple[str, ...] = FINAL_AUTHORISATION_CONTROLS
    blockers: tuple[str, ...] = field(default_factory=tuple)
    beta_scope: str = "controlled_beta_only"
    authorisation_decision: str = "authorise_limited_controlled_beta_live_learner_traffic"
    cohort_gate_state: str = "cohort_guardian_consent_and_learner_eligibility_evidence_accepted"
    auth_gate_state: str = "pyjwt_migration_and_auth_token_regression_evidence_accepted"
    dry_run_gate_state: str = "live_traffic_dry_run_kill_switch_and_rollback_evidence_accepted"
    support_gate_state: str = "monitoring_support_and_incident_escalation_evidence_accepted"
    live_learner_traffic_authorised: bool = True
    controlled_beta_live_traffic_authorised: bool = True
    prd11_handoff_authorised: bool = True
    boundaries: dict[str, bool] = field(default_factory=lambda: dict(LOCKED_FALSE_BOUNDARIES))

    def to_payload(self) -> dict:
        return {
            "prd_id": self.prd_id,
            "accepted": self.accepted,
            "controls": list(self.controls),
            "blockers": list(self.blockers),
            "beta_scope": self.beta_scope,
            "authorisation_decision": self.authorisation_decision,
            "cohort_gate_state": self.cohort_gate_state,
            "auth_gate_state": self.auth_gate_state,
            "dry_run_gate_state": self.dry_run_gate_state,
            "support_gate_state": self.support_gate_state,
            "controlled_beta_final_evidence_accepted": self.accepted,
            "cohort_guardian_consent_learner_eligibility_accepted": self.accepted,
            "auth_token_regression_accepted": self.accepted,
            "dry_run_kill_switch_rollback_accepted": self.accepted,
            "support_monitoring_incident_go_no_go_accepted": self.accepted,
            "controlled_beta_live_traffic_authorised": self.controlled_beta_live_traffic_authorised,
            "live_learner_traffic_authorised": self.live_learner_traffic_authorised,
            "prd11_handoff_authorised": self.prd11_handoff_authorised,
            **self.boundaries,
        }


def build_default_controlled_beta_final_authorisation_report() -> ControlledBetaFinalAuthorisationReport:
    return ControlledBetaFinalAuthorisationReport()


def build_blocked_controlled_beta_final_authorisation_report() -> ControlledBetaFinalAuthorisationReport:
    return ControlledBetaFinalAuthorisationReport(
        accepted=False,
        blockers=("controlled_beta_final_authorisation_incomplete",),
        beta_scope="blocked",
        authorisation_decision="do_not_authorise_live_learner_traffic",
        live_learner_traffic_authorised=False,
        controlled_beta_live_traffic_authorised=False,
        prd11_handoff_authorised=False,
    )
