from app.api_v2 import ROUTER_REGISTRY, app
from app.modules.jobs import WorkerSettings


def test_ai_operations_router_registered():
    names = {name for name, _ in ROUTER_REGISTRY}
    assert "ai_operations" in names
    paths = {route.path for route in app.routes}
    assert "/api/v2/admin/ai-operations/providers/health" in paths
    assert "/v2/admin/ai-operations/usage" in paths


def test_expiry_job_registered_and_scheduled():
    function_names = {getattr(fn, "__name__", "") for fn in WorkerSettings.functions}
    assert "expire_ai_usage_reservations" in function_names
    assert any("expire_ai_usage_reservations" in repr(job) for job in WorkerSettings.cron_jobs)
