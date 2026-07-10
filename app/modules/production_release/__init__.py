"""Production release and deployment authorisation contracts for PRD-11."""
from app.modules.production_release.readiness import (
    PRD_ID,
    PRODUCTION_RELEASE_BOUNDARIES,
    PRODUCTION_RELEASE_PREFLIGHT_CONTROLS,
    ProductionReleasePreflightReport,
    build_blocked_production_release_preflight_report,
    build_default_production_release_preflight_report,
)

__all__ = [
    "PRD_ID",
    "PRODUCTION_RELEASE_BOUNDARIES",
    "PRODUCTION_RELEASE_PREFLIGHT_CONTROLS",
    "ProductionReleasePreflightReport",
    "build_blocked_production_release_preflight_report",
    "build_default_production_release_preflight_report",
    "TRUE_STATE_RUNTIME_BASELINE_PRD_ID",
    "TRUE_STATE_CONCERN_CATEGORIES",
    "TrueStateRuntimeBaselineReport",
    "build_default_true_state_runtime_baseline_report",
    "build_green_true_state_runtime_baseline_report",
]

from app.modules.production_release.true_state_baseline import (
    PRD_ID as TRUE_STATE_RUNTIME_BASELINE_PRD_ID,
    TRUE_STATE_CONCERN_CATEGORIES,
    TrueStateRuntimeBaselineReport,
    build_default_true_state_runtime_baseline_report,
    build_green_true_state_runtime_baseline_report,
)
