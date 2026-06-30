#!/bin/bash
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null
# Run a fast smoke set of tests covering changed files
python -m pytest -q --no-header \
    tests/unit/test_api_v2_routers_contract_smoke.py \
    tests/unit/test_auth_context_claims.py \
    tests/unit/test_token_revocation.py \
    tests/unit/test_token_rotation.py \
    tests/unit/test_token_config.py \
    tests/unit/test_role_authorization.py \
    tests/unit/test_consent_state_machine.py \
    tests/unit/test_learner_service.py \
    tests/smoke/test_v2_smoke.py \
    2>&1 | tail -25
