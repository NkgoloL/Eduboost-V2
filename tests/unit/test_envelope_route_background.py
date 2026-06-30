from fastapi import APIRouter, BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

from app.core.envelope_route import EnvelopedRoute


def test_enveloped_route_preserves_background_tasks():
    calls: list[str] = []
    router = APIRouter(route_class=EnvelopedRoute)

    def mark_complete() -> None:
        calls.append("ran")

    @router.get("/task")
    def task_endpoint(background_tasks: BackgroundTasks):
        background_tasks.add_task(mark_complete)
        return {"ok": True}

    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).get("/task")

    assert response.status_code == 200
    assert response.json()["data"] == {"ok": True}
    assert calls == ["ran"]
