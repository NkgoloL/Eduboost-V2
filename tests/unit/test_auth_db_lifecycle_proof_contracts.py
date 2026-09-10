from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import pytest

from app.services.auth_db_lifecycle_proof import SQLiteAuthLifecycleProofStore


ROOT = Path(__file__).resolve().parents[2]


def test_auth_db_lifecycle_store_contract_register_login_refresh():
    store = SQLiteAuthLifecycleProofStore()
    registered = store.register(email="contract@example.com", password="Password123!")
    logged_in = store.login(email="contract@example.com", password="Password123!")
    refreshed = store.refresh(refresh_token=logged_in.refresh_token)
    assert registered.guardian_learner_ids
    assert logged_in.guardian_learner_ids == registered.guardian_learner_ids
    assert refreshed.guardian_learner_ids == registered.guardian_learner_ids


def test_auth_db_lifecycle_store_edge_cases():
    from fastapi import HTTPException
    from app.services.auth_db_lifecycle_proof import _hash_password

    store = SQLiteAuthLifecycleProofStore()

    # Validation errors
    with pytest.raises(HTTPException) as exc1:
        store.register(email="", password="pass")
    assert exc1.value.status_code == 422

    with pytest.raises(HTTPException) as exc2:
        store.register(email="user@test.com", password="")
    assert exc2.value.status_code == 422

    # Duplicate registration
    store.register(email="dup@test.com", password="pwd")
    with pytest.raises(HTTPException) as exc3:
        store.register(email="dup@test.com", password="pwd")
    assert exc3.value.status_code == 409

    # Unknown login
    with pytest.raises(HTTPException) as exc4:
        store.login(email="missing@test.com", password="pwd")
    assert exc4.value.status_code == 401

    # Bad password
    with pytest.raises(HTTPException) as exc5:
        store.login(email="dup@test.com", password="wrongpassword")
    assert exc5.value.status_code == 401

    # Missing guardian
    store.connection.execute(
        "INSERT INTO users (id, email, password_salt, password_hash, role) VALUES ('u-nog', 'nog@test.com', 's', ?, 'guardian')",
        (_hash_password("pwd", "s"),),
    )
    store.connection.commit()
    with pytest.raises(HTTPException) as exc6:
        store.login(email="nog@test.com", password="pwd")
    assert exc6.value.status_code == 403

    # Unknown refresh
    with pytest.raises(HTTPException) as exc7:
        store.refresh(refresh_token="unknown-tok")
    assert exc7.value.status_code == 401

    # Reused refresh
    tokens = store.login(email="dup@test.com", password="pwd")
    store.refresh(refresh_token=tokens.refresh_token)
    with pytest.raises(HTTPException) as exc8:
        store.refresh(refresh_token=tokens.refresh_token)
    assert exc8.value.status_code == 401


def test_auth_db_proof_application_service_flow():
    import asyncio
    from app.services.auth_db_lifecycle_proof import (
        AuthDBProofApplicationService,
        _find_by_name,
        extract_auth_payload,
        extract_refresh_token,
        token_response,
    )
    from types import SimpleNamespace
    from fastapi import HTTPException

    store = SQLiteAuthLifecycleProofStore()
    app_service = AuthDBProofApplicationService(store)

    async def _run():
        reg = await app_service.register(email="app@test.com", password="password123")
        assert "access_token" in reg

        login_res = await app_service.login(email="app@test.com", password="password123")
        assert "access_token" in login_res

        ref_res = await app_service.refresh(refresh_token=login_res["refresh_token"])
        assert "access_token" in ref_res

        dev_res = await app_service.create_dev_session()
        assert "access_token" in dev_res

    asyncio.run(_run())

    # Helper coverage
    class DumpObj:
        def model_dump(self):
            return {"inner_key": "val1"}

    class DictObj:
        def dict(self):
            return {"inner_dict": "val2"}

    assert _find_by_name({"nested": DumpObj()}, {"inner_key"}) == "val1"
    assert _find_by_name({"nested": DictObj()}, {"inner_dict"}) == "val2"

    email, pwd, name = extract_auth_payload({})
    assert email == "guardian.success@example.com"
    assert pwd == "Password123!"
    assert name == "Guardian Success"

    req = SimpleNamespace(cookies={"refresh_token": "cookie-tok"})
    assert extract_refresh_token({"req": req}) == "cookie-tok"
    assert extract_refresh_token({"token": "explicit-tok"}) == "explicit-tok"

    with pytest.raises(HTTPException) as exc:
        extract_refresh_token({"other": 1})
    assert exc.value.status_code == 401



def test_auth_db_lifecycle_proof_scripts_run():
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    for command in [
        [sys.executable, "scripts/generate_auth_db_lifecycle_proof_report.py"],
        [sys.executable, "scripts/check_auth_db_lifecycle_proof.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, env=env)
        assert result.returncode == 0, result.stdout


def test_auth_db_lifecycle_proof_reports_exist():
    assert (ROOT / "docs/release/auth_db_lifecycle_proof_report.md").exists()
    assert (ROOT / "docs/release/auth_db_lifecycle_proof_report.json").exists()


def test_makefile_contains_auth_db_lifecycle_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-db-lifecycle-proof-report:" in text
    assert "auth-db-lifecycle-proof-check:" in text
    assert "backend-implementation-1031-1070-full-check:" in text
