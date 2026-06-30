from __future__ import annotations

from app.api_v2 import ROUTER_REGISTRY
from app.api_v2_routers.curriculum_expansion import router
from app.jobs.curriculum_expansion_job import capture_weekly_curriculum_coverage
from app.modules.jobs import WorkerSettings


def test_curriculum_expansion_router_is_registered():
    registered = dict(ROUTER_REGISTRY)
    assert registered["curriculum_expansion"] is router
    paths = {route.path for route in router.routes}
    assert "/admin/curriculum-expansion/coverage/{scope_id}" in paths
    assert "/admin/curriculum-expansion/training-manifests" in paths


def test_weekly_snapshot_job_is_registered():
    assert capture_weekly_curriculum_coverage in WorkerSettings.functions
    assert any(
        getattr(job, "coroutine", None) is capture_weekly_curriculum_coverage
        or getattr(job, "name", "") == "capture_weekly_curriculum_coverage"
        for job in WorkerSettings.cron_jobs
    )
