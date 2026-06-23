from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_verifier():
    module_path = Path(__file__).resolve().parents[3] / "scripts" / "audit_remediation" / "verify_openapi_route_contract.py"
    spec = importlib.util.spec_from_file_location("verify_openapi_route_contract", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_contract_fixture(root: Path, *, include_status_route: bool = True, stale_frontend: bool = False) -> None:
    (root / "docs").mkdir(parents=True)
    paths = {
        "/api/v2/popia/exports": {"post": {}},
        "/v2/popia/exports": {"post": {}},
        "/api/v2/popia/erasure": {"post": {}},
        "/v2/popia/erasure": {"post": {}},
        "/api/v2/popia/erasure/{learner_id}/cancel": {"post": {}},
        "/v2/popia/erasure/{learner_id}/cancel": {"post": {}},
        "/api/v2/popia/restriction": {"post": {}},
        "/v2/popia/restriction": {"post": {}},
        "/api/v2/parents/{guardian_id}/export": {"get": {}},
        "/v2/parents/{guardian_id}/export": {"get": {}},
    }
    if include_status_route:
        paths["/api/v2/popia/erasure/{learner_id}/status"] = {"get": {}}
        paths["/v2/popia/erasure/{learner_id}/status"] = {"get": {}}
    (root / "docs/openapi.json").write_text(json.dumps({"paths": paths}), encoding="utf-8")

    (root / "app/frontend/src/lib/api").mkdir(parents=True)
    stale = 'fetchApi<any>("/popia/data-export/abc")' if stale_frontend else ""
    (root / "app/frontend/src/lib/api/services.ts").write_text(
        f'''
export const DataRightsService = {{
  exportLearner: () => fetchApi<DataExportBundle>("/popia/exports", {{ method: "POST" }}),
  requestErasure: () => fetchApi<DataRightsStatus>("/popia/erasure", {{ method: "POST" }}),
  cancelErasure: (learnerId: string) => fetchApi<DataRightsStatus>(`/popia/erasure/${{learnerId}}/cancel`, {{ method: "POST" }}),
  restrictProcessing: () => fetchApi<DataRightsStatus>("/popia/restriction", {{ method: "POST" }}),
  deletionStatus: (learnerId: string) => fetchApi<DataRightsStatus>(`/popia/erasure/${{learnerId}}/status`),
}};
export const ParentService = {{
  getExportBundle: (guardianId: string) => fetchApi<ParentExportBundle>(`/parents/${{guardianId}}/export`),
}};
{stale}
''',
        encoding="utf-8",
    )

    (root / "app/api_v2_routers").mkdir(parents=True)
    (root / "app/api_v2_routers/parents.py").write_text(
        'export_url=f"/api/v2/popia/exports?learner_id={learner.id}"\n',
        encoding="utf-8",
    )
    (root / "app/api_v2_routers/popia.py").write_text(
        '@router.get("/erasure/{learner_id}/status")\n',
        encoding="utf-8",
    )


def test_openapi_contract_accepts_canonical_routes(tmp_path: Path) -> None:
    module = load_verifier()
    write_contract_fixture(tmp_path)
    result = module.verify(tmp_path)
    assert result["valid"], result


def test_openapi_contract_requires_status_route(tmp_path: Path) -> None:
    module = load_verifier()
    write_contract_fixture(tmp_path, include_status_route=False)
    result = module.verify(tmp_path)
    assert not result["valid"]
    assert any("/erasure/{learner_id}/status" in error for error in result["errors"])


def test_openapi_contract_rejects_stale_frontend_route(tmp_path: Path) -> None:
    module = load_verifier()
    write_contract_fixture(tmp_path, stale_frontend=True)
    result = module.verify(tmp_path)
    assert not result["valid"]
    assert any("stale POPIA route" in error for error in result["errors"])
