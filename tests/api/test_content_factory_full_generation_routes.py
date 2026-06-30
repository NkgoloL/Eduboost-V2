"""API tests for content factory full generation routes."""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.api_v2 import app


def test_unauthenticated_plan_rejected():
    """Unauthenticated plan rejected."""
    client = TestClient(app)
    response = client.post("/api/v2/admin/content-factory/full-generation/plan")
    assert response.status_code == 401


def test_unauthenticated_start_rejected():
    """Unauthenticated start rejected."""
    client = TestClient(app)
    response = client.post("/api/v2/admin/content-factory/full-generation/start")
    assert response.status_code == 401


def test_unauthenticated_list_runs_rejected():
    """Unauthenticated list runs rejected."""
    client = TestClient(app)
    response = client.get("/api/v2/admin/content-factory/full-generation/runs")
    assert response.status_code == 401


def test_unauthenticated_get_run_rejected():
    """Unauthenticated get run rejected."""
    client = TestClient(app)
    run_id = str(uuid.uuid4())
    response = client.get(f"/api/v2/admin/content-factory/full-generation/runs/{run_id}")
    assert response.status_code == 401


def test_unauthenticated_get_report_rejected():
    """Unauthenticated get report rejected."""
    client = TestClient(app)
    run_id = str(uuid.uuid4())
    response = client.get(f"/api/v2/admin/content-factory/full-generation/runs/{run_id}/report")
    assert response.status_code == 401


def test_unauthenticated_cancel_rejected():
    """Unauthenticated cancel rejected."""
    client = TestClient(app)
    run_id = str(uuid.uuid4())
    response = client.post(f"/api/v2/admin/content-factory/full-generation/runs/{run_id}/cancel")
    assert response.status_code == 401


def test_unauthenticated_resume_rejected():
    """Unauthenticated resume rejected."""
    client = TestClient(app)
    run_id = str(uuid.uuid4())
    response = client.post(f"/api/v2/admin/content-factory/full-generation/runs/{run_id}/resume")
    assert response.status_code == 401
