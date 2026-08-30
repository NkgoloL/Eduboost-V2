import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.admin_etl import router
from app.api_v2_deps.auth import require_admin


@pytest.mark.asyncio
async def test_admin_etl_visibility_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-usr"
    auth_ctx.roles = ["admin"]

    app.dependency_overrides[require_admin] = lambda: auth_ctx

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Status
        resp_status = await client.get("/admin/etl/status")
        assert resp_status.status_code == 200
        assert resp_status.json()["data"]["status"] == "available"

        # 2. Documents listing & item
        resp_docs = await client.get("/admin/etl/documents")
        assert resp_docs.status_code == 200

        resp_doc = await client.get("/admin/etl/documents/caps-grade4-maths-topic-map")
        assert resp_doc.status_code == 200

        resp_doc_nf = await client.get("/admin/etl/documents/nonexistent")
        assert resp_doc_nf.status_code == 200

        # 3. Chunks & audit
        resp_chunks = await client.get("/admin/etl/documents/doc-1/chunks")
        assert resp_chunks.status_code == 200

        resp_audit = await client.get("/admin/etl/documents/doc-1/audit")
        assert resp_audit.status_code == 200

        # 4. Review queue, quality, search, datasets, metrics
        resp_rq = await client.get("/admin/etl/review-queue")
        assert resp_rq.status_code == 200

        resp_q = await client.get("/admin/etl/quality/doc-1")
        assert resp_q.status_code == 200

        resp_s = await client.get("/admin/etl/search?q=maths")
        assert resp_s.status_code == 200

        resp_ds = await client.get("/admin/etl/datasets")
        assert resp_ds.status_code == 200

        resp_m = await client.get("/admin/etl/metrics")
        assert resp_m.status_code == 200
