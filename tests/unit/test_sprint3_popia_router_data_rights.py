from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api_v2_deps.consent_lifecycle import get_canonical_data_rights_service
from app.api_v2_routers import popia
from app.core.security import get_current_user


LEARNER_ID = uuid.uuid4()
ACTOR = {"sub": "guardian-1", "role": "parent"}


@dataclass
class FakeDataRightsService:
    calls: list[tuple[str, dict[str, Any]]] = field(default_factory=list)

    async def build_learner_export(self, *, learner_id: str, current_user: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("export", {"learner_id": learner_id, "current_user": current_user}))
        return {"request_type": "export", "learner_id": learner_id, "status": "completed"}

    async def request_erasure(self, *, learner_id: str, current_user: dict[str, Any], reason: str) -> dict[str, Any]:
        self.calls.append(("erasure", {"learner_id": learner_id, "current_user": current_user, "reason": reason}))
        return {"request_type": "erasure", "learner_id": learner_id, "status": "accepted", "reason": reason}

    async def cancel_erasure(self, *, learner_id: str, current_user: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("cancel_erasure", {"learner_id": learner_id, "current_user": current_user}))
        return {"request_type": "erasure", "learner_id": learner_id, "status": "cancelled"}

    async def request_correction(self, *, learner_id: str, current_user: dict[str, Any], fields: dict[str, Any], reason: str) -> dict[str, Any]:
        self.calls.append(("correction", {"learner_id": learner_id, "current_user": current_user, "fields": fields, "reason": reason}))
        return {"request_type": "correction", "learner_id": learner_id, "status": "completed", "fields": fields}

    async def restrict_processing(self, *, learner_id: str, current_user: dict[str, Any], reason: str) -> dict[str, Any]:
        self.calls.append(("restriction", {"learner_id": learner_id, "current_user": current_user, "reason": reason}))
        return {"request_type": "restriction", "learner_id": learner_id, "status": "accepted", "reason": reason}


def _client(service: FakeDataRightsService) -> TestClient:
    app = FastAPI()
    app.include_router(popia.router)
    app.dependency_overrides[get_current_user] = lambda: ACTOR
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: service
    return TestClient(app, raise_server_exceptions=True)


def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("data", payload)


def test_export_erasure_cancel_correction_and_restriction_routes_delegate_to_service():
    service = FakeDataRightsService()
    client = _client(service)

    export = client.post("/popia/exports", json={"learner_id": str(LEARNER_ID), "format": "json"})
    assert export.status_code == 200
    assert _unwrap(export.json())["request_type"] == "export"

    erasure = client.post("/popia/erasure", json={"learner_id": str(LEARNER_ID), "reason": "guardian_request"})
    assert erasure.status_code == 201
    assert _unwrap(erasure.json())["request_type"] == "erasure"

    cancel = client.post(f"/popia/erasure/{LEARNER_ID}/cancel")
    assert cancel.status_code == 200
    assert _unwrap(cancel.json())["status"] == "cancelled"

    correction = client.post(
        "/popia/correction",
        json={"learner_id": str(LEARNER_ID), "fields": {"display_name": "New Name"}, "reason": "typo_fix"},
    )
    assert correction.status_code == 200
    assert _unwrap(correction.json())["request_type"] == "correction"

    restriction = client.post(
        "/popia/restriction",
        json={"learner_id": str(LEARNER_ID), "reason": "dispute_accuracy"},
    )
    assert restriction.status_code == 200
    assert _unwrap(restriction.json())["request_type"] == "restriction"

    observed = {name for name, _ in service.calls}
    assert observed == {"export", "erasure", "cancel_erasure", "correction", "restriction"}
