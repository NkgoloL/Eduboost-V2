"""PRD-10.0-10.4 controlled beta/live learner traffic preflight readiness."""
from __future__ import annotations

from dataclasses import dataclass, field

PRD_ID = "PRD-10.0-10.4"

PREFLIGHT_CONTROLS = (
    "prd10_authority_and_live_traffic_gate_definition",
    "pyjwt_auth_token_regression_gate",
    "controlled_beta_cohort_definition",
    "guardian_consent_approval_and_learner_eligibility_gate",
    "live_learner_traffic_dry_run",
    "kill_switch_and_rollback_readiness",
    "beta_support_monitoring_incident_escalation",
    "go_no_go_readiness_contract",
)

FALSE_BOUNDARIES = {
    "prd11_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "live_learner_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
}


@dataclass(frozen=True)
class ControlledBetaPreflightReport:
    prd_id: str = PRD_ID
    accepted: bool = True
    controls: tuple[str, ...] = PREFLIGHT_CONTROLS
    blockers: tuple[str, ...] = field(default_factory=tuple)
    beta_mode: str = "preflight_only"
    live_traffic_gate_state: str = "defined_not_authorised"
    auth_token_regression_gate: str = "pyjwt_migration_required_and_verified_before_live_traffic"
    cohort_gate: str = "guardian_consent_and_learner_eligibility_required"
    kill_switch_state: str = "required_before_any_live_traffic"
    support_go_no_go_state: str = "required_before_any_live_traffic"
    prd10_final_handoff_authorised: bool = False
    boundaries: dict[str, bool] = field(default_factory=lambda: dict(FALSE_BOUNDARIES))

    def to_payload(self) -> dict:
        return {
            "prd_id": self.prd_id,
            "accepted": self.accepted,
            "controls": list(self.controls),
            "blockers": list(self.blockers),
            "beta_mode": self.beta_mode,
            "live_traffic_gate_state": self.live_traffic_gate_state,
            "auth_token_regression_gate": self.auth_token_regression_gate,
            "cohort_gate": self.cohort_gate,
            "kill_switch_state": self.kill_switch_state,
            "support_go_no_go_state": self.support_go_no_go_state,
            "controlled_beta_preflight_defined": self.accepted,
            "pyjwt_auth_regression_gate_defined": self.accepted,
            "cohort_consent_eligibility_gate_defined": self.accepted,
            "dry_run_kill_switch_rollback_defined": self.accepted,
            "support_monitoring_incident_go_no_go_defined": self.accepted,
            "prd10_final_handoff_authorised": self.prd10_final_handoff_authorised,
            **self.boundaries,
        }


def build_default_controlled_beta_preflight_report() -> ControlledBetaPreflightReport:
    return ControlledBetaPreflightReport()


def build_blocked_controlled_beta_preflight_report() -> ControlledBetaPreflightReport:
    return ControlledBetaPreflightReport(
        accepted=False,
        blockers=("controlled_beta_preflight_incomplete",),
        beta_mode="blocked",
        live_traffic_gate_state="blocked_not_authorised",
    )
