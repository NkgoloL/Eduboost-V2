import anyio
from fastapi import APIRouter, BackgroundTasks, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.envelope_route import EnvelopedRoute


async def _run_background_task_request() -> tuple[int, dict[str, object], list[str]]:
    calls: list[str] = []
    router = APIRouter(route_class=EnvelopedRoute)

    async def mark_complete() -> None:
        calls.append("ran")

    @router.get("/task")
    async def task_endpoint(background_tasks: BackgroundTasks):
        background_tasks.add_task(mark_complete)
        return {"ok": True}

    app = FastAPI()
    app.include_router(router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/task")
    return response.status_code, response.json(), calls


def test_enveloped_route_preserves_background_tasks():
    status_code, payload, calls = anyio.run(_run_background_task_request)

    assert status_code == 200
    assert payload["data"] == {"ok": True}
    assert calls == ["ran"]
