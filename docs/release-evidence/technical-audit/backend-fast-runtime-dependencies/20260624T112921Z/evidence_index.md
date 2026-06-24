# Technical Audit Remediation Evidence — Backend Fast Runtime Dependencies

**Stream:** technical-audit-remediation  
**Slice:** 02b-backend-fast-runtime-dependencies  
**Branch:** feature/atlas-phase-02r-gate-2r1-remediation  
**Source commit:** f5d72b8380da6403371ea91f6c8298626ba07aa1  
**Generated at:** 2026-06-24T13:29:24+02:00  
**Status:** Runtime dependency verification failed — remediation pending  
**Authority command remains:** make test-fast

## Raw evidence

- raw/runtime_dependency_verification.json
- raw/runtime_dependency_verification.stdout
- raw/backend_fast_environment.json
- raw/compileall.txt
- raw/result.json
- raw/SHA256SUMS.txt

## Boundary

This evidence only proves that the backend-fast authority Python runtime dependencies are present. It is not backend-fast candidate evidence. Passing backend-fast evidence remains blocked until .venv/bin/python -m pytest -c pytest.ini tests/unit -n auto --no-cov -m "not governance and not slow and not llm and not e2e" -q
bringing up nodes...
bringing up nodes...

................................s.............s..........ss............. [  3%]
........................................................................ [  6%]
......................................................................... [  9%]
......................................................................... [ 12%]
........F.....................s......................................... [ 15%]
........................................................................ [ 18%]
...F..............................................FF.................... [ 22%]
......................F..................F..F........................... [ 25%]
..........................F............................................. [ 28%]
........................................................................ [ 31%]
..........................................FFF.F......................... [ 34%]
...................................FF.................................F. [ 37%]
........................................................................ [ 40%]
........................................................................ [ 44%]
......................ssssss............................................ [ 47%]
........................................................................ [ 50%]
............F......FFF........F......F.....FFFF......................... [ 53%]
........................................................................ [ 56%]
.........................................FFF............................ [ 59%]
....................F................................................... [ 62%]
........................................................................ [ 66%]
.....................................F.................................. [ 69%]
..............x.............................F...F.......F......F......F. [ 72%]
...F.................................................................... [ 75%]
............F.........................................F................. [ 78%]
.................FF...FF.FFF.FFF.F....F................................. [ 81%]
.......FFFFF......F..................................................... [ 85%]
......................................F...F.F........................... [ 88%]
..........................................F..FF......................... [ 91%]
..F..................................................................... [ 94%]
..............FFFFFF..................................................FF [ 97%]
FF.....................................................                  [100%]
=================================== FAILURES ===================================
______ test_registered_router_fragments_are_exposed_under_each_v2_prefix _______
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_api_v2_router_contract.py:48: in test_registered_router_fragments_are_exposed_under_each_v2_prefix
    fragment = expected_fragments[router_name]
E   KeyError: 'curriculum_expansion'
_ TestDiagnosticItemProperties.test_is_available_true_when_approved_and_under_cap _
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/modules/diagnostics/test_item_bank_models.py:214: in test_is_available_true_when_approved_and_under_cap
    assert item.is_available_for_selection
E   AssertionError: assert False
E    +  where False = <DiagnosticItem item_id=81e9f92a caps_ref='4.M.1.1' status='approved'>.is_available_for_selection
__________________ test_select_item_picks_nearest_b_to_theta ___________________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/modules/diagnostics/test_item_bank_service.py:165: in test_select_item_picks_nearest_b_to_theta
    assert selected.item_id == item_near.item_id
E   AttributeError: 'NoneType' object has no attribute 'item_id'
___________ test_select_item_expands_window_when_neighbourhood_empty ___________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/modules/diagnostics/test_item_bank_service.py:182: in test_select_item_expands_window_when_neighbourhood_empty
    assert selected.item_id == fallback_item.item_id
E   AttributeError: 'NoneType' object has no attribute 'item_id'
______________ test_days_until_expiry_returns_positive_for_future ______________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_consent_state_machine.py:189: in test_days_until_expiry_returns_positive_for_future
    assert c.days_until_expiry() == 30
E   AssertionError: assert 29 == 30
E    +  where 29 = <bound method ConsentRecord.days_until_expiry of ConsentRecord(id=UUID('2976e5d2-a0b5-4d45-875a-61ca59ea6329'), learne...o=datetime.timezone.utc), updated_at=datetime.datetime(2026, 6, 24, 11, 29, 47, 641282, tzinfo=datetime.timezone.utc))>()
E    +    where <bound method ConsentRecord.days_until_expiry of ConsentRecord(id=UUID('2976e5d2-a0b5-4d45-875a-61ca59ea6329'), learne...o=datetime.timezone.utc), updated_at=datetime.datetime(2026, 6, 24, 11, 29, 47, 641282, tzinfo=datetime.timezone.utc))> = ConsentRecord(id=UUID('2976e5d2-a0b5-4d45-875a-61ca59ea6329'), learner_id=UUID('00000000-0000-0000-0000-000000000001')...fo=datetime.timezone.utc), updated_at=datetime.datetime(2026, 6, 24, 11, 29, 47, 641282, tzinfo=datetime.timezone.utc)).days_until_expiry
_________ test_future_layers_return_configured_zero_count_placeholders _________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_coverage_service.py:142: in test_future_layers_return_configured_zero_count_placeholders
    assert report.layers[ContentLayer.ASSESSMENT_BLUEPRINTS].target == 4
E   AssertionError: assert 1 == 4
E    +  where 1 = CoverageLayerCounts(target=1, approved=0, pending_review=0, rejected=0, generated=0, status=<CoverageLayerStatus.RED: 'red'>, coverage_ratio=0.0).target
_________ TestContentArtifactStatusEnum.test_no_undeclared_orm_values __________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_factory_enums.py:53: in test_no_undeclared_orm_values
    assert not extra, (
E   AssertionError: ContentArtifactStatus has values not declared in the schema contract: {'superseded', 'revision_required', 'published'}. Add them to the contract or remove from the ORM.
E   assert not {'published', 'revision_required', 'superseded'}
________________ test_valid_approved_artifact_creates_seed_item ________________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_staging_seed_executor.py:195: in seed_staging
    staging_artifact_id = existing_staging.id
E   AttributeError: 'types.SimpleNamespace' object has no attribute 'id'

During handling of the above exception, another exception occurred:
tests/unit/test_content_staging_seed_executor.py:96: in test_valid_approved_artifact_creates_seed_item
    res = await executor.seed_staging(session, "some_scope", actor_id="admin")
app/services/content_staging_seed_executor.py:329: in seed_staging
    await session.rollback()
E   AttributeError: 'Session' object has no attribute 'rollback'
_______ test_auth_refresh_db_proof_workflow_runs_proof_and_evidence_gate _______
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_ci_auth_refresh_db_proof_workflow.py:33: in test_auth_refresh_db_proof_workflow_runs_proof_and_evidence_gate
    assert "actions/upload-artifact@v4" in source
E   assert 'actions/upload-artifact@v4' in 'name: Auth Refresh DB Proof\n\non:\n  workflow_dispatch:\n  pull_request:\n    paths:\n      - "app/**"\n      - "scr...            docs/release/auth_refresh_db_evidence_status.json\n            docs/release/evidence_status_registry.yml\n'
____________ test_ci_auth_refresh_db_proof_workflow_status_passing _____________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_ci_auth_refresh_db_proof_workflow.py:38: in test_ci_auth_refresh_db_proof_workflow_status_passing
    assert status.status == "ci-auth-refresh-db-proof-workflow-configured"
E   AssertionError: assert 'ci-auth-refr...ow-not-proven' == 'ci-auth-refr...ow-configured'
E     
E     - ci-auth-refresh-db-proof-workflow-configured
E     ?                                   ^  -------
E     + ci-auth-refresh-db-proof-workflow-not-proven
E     ?                                   ^ +++++++
_________ test_ci_auth_refresh_db_proof_workflow_status_writes_reports _________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_ci_auth_refresh_db_proof_workflow.py:46: in test_ci_auth_refresh_db_proof_workflow_status_writes_reports
    assert status.status == "ci-auth-refresh-db-proof-workflow-configured"
E   AssertionError: assert 'ci-auth-refr...ow-not-proven' == 'ci-auth-refr...ow-configured'
E     
E     - ci-auth-refresh-db-proof-workflow-configured
E     ?                                   ^  -------
E     + ci-auth-refresh-db-proof-workflow-not-proven
E     ?                                   ^ +++++++
________ test_ci_auth_refresh_db_proof_workflow_checker_runs_local_mode ________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_ci_auth_refresh_db_proof_workflow.py:61: in test_ci_auth_refresh_db_proof_workflow_checker_runs_local_mode
    assert result.returncode == 0, result.stdout
E   AssertionError: CI auth refresh DB proof workflow check
E     - INFO status: ci-auth-refresh-db-proof-workflow-not-proven
E     - PASS syntax scripts/ci_auth_refresh_db_proof_workflow.py
E     - PASS syntax scripts/check_ci_auth_refresh_db_proof_workflow.py
E     - PASS syntax scripts/patch_ci_auth_refresh_db_proof_workflow_registry.py
E     - PASS syntax tests/unit/test_ci_auth_refresh_db_proof_workflow.py
E     - PASS focused Ruff CI auth refresh DB proof workflow check
E     Failures:
E     - artifact upload configured
E     
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python', 'scripts/check_ci_au...f_workflow.py\n- PASS focused Ruff CI auth refresh DB proof workflow check\nFailures:\n- artifact upload configured\n').returncode
_________________ test_etl_mcp_server_uses_json_response_mode __________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_etl_mcp_server_startup.py:5: in test_etl_mcp_server_uses_json_response_mode
    import tools.etl.etl_mcp_server_v2 as server
tools/etl/etl_mcp_server_v2.py:55: in <module>
    from mcp.server.fastmcp import FastMCP
E   ModuleNotFoundError: No module named 'mcp'
______________ test_start_streamable_http_falls_back_to_settings _______________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_etl_mcp_server_startup.py:11: in test_start_streamable_http_falls_back_to_settings
    import tools.etl.etl_mcp_server_v2 as server
tools/etl/etl_mcp_server_v2.py:55: in <module>
    from mcp.server.fastmcp import FastMCP
E   ModuleNotFoundError: No module named 'mcp'
_______________ test_bridge_expression_maps_item_id_from_irt_id ________________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_diagnostic_score_live_audit.py:28: in test_bridge_expression_maps_item_id_from_irt_id
    assert expr == 'gen_random_uuid()'
E   assert 'i."id"' == 'gen_random_uuid()'
E     
E     - gen_random_uuid()
E     + i."id"
_________ TestOrmTableNameReconciliation.test_no_undeclared_orm_models _________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_factory_table_reconciliation.py:102: in test_no_undeclared_orm_models
    assert not undeclared, (
E   AssertionError: The following ORM models are not declared in ORM_TABLE_MAP. Add them to the schema contract:
E       ContentAnswerKeyVerification (__tablename__='content_answer_key_verifications')
E       ContentReviewDecision (__tablename__='content_review_decisions')
E       ContentStateTransitionEvent (__tablename__='content_state_transition_events')
E   assert not ["ContentAnswerKeyVerification (__tablename__='content_answer_key_verifications')", "ContentReviewDecision (__tablename__='content_review_decisions')", "ContentStateTransitionEvent (__tablename__='content_state_transition_events')"]
_ test_file_promotion_readiness_marks_review_scopes_staging_ready_not_production_ready _
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_promotion_readiness.py:18: in test_file_promotion_readiness_marks_review_scopes_staging_ready_not_production_ready
    result = service.evaluate_scope("grade5_mathematics_en")
app/services/content_file_promotion_readiness.py:69: in evaluate_scope
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_____ test_file_promotion_readiness_writes_summary_and_per_scope_manifests _____
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_file_promotion_readiness.py:33: in test_file_promotion_readiness_writes_summary_and_per_scope_manifests
    assert summary["summary"]["scope_count"] == 51
E   assert 1 == 51
__ test_registry_coverage_report_includes_layer_files_and_promotion_readiness __
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_file_promotion_readiness.py:45: in test_registry_coverage_report_includes_layer_files_and_promotion_readiness
    grade5 = next(row for row in report["scopes"] if row["scope_id"] == "grade5_mathematics_en")
E   StopIteration
________ test_pilot_review_packet_defaults_to_pending_educator_approval ________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:18: in test_pilot_review_packet_defaults_to_pending_educator_approval
    packet = service.build_review_packet("grade5_mathematics_en")
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
______ test_dev_approved_review_packet_unlocks_staging_but_not_production ______
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:30: in test_dev_approved_review_packet_unlocks_staging_but_not_production
    service.build_review_packet(
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_____ test_educator_and_legal_approval_unlocks_production_review_evidence ______
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:49: in test_educator_and_legal_approval_unlocks_production_review_evidence
    service.build_review_packet(
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
___________ test_placeholder_approval_urls_do_not_unlock_production ____________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:68: in test_placeholder_approval_urls_do_not_unlock_production
    service.build_review_packet(
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_________ test_import_plan_uses_pending_review_until_educator_approval _________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:87: in test_import_plan_uses_pending_review_until_educator_approval
    review_service.build_review_packet("grade5_mathematics_en")
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
___________ test_import_plan_switches_to_approved_with_dev_approval ____________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:104: in test_import_plan_switches_to_approved_with_dev_approval
    review_service.build_review_packet(
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
________________ test_operational_auth_boundary_matrix_statuses ________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_operational_auth_boundaries.py:20: in test_operational_auth_boundary_matrix_statuses
    ether = lookup[("ether.py", "GET", "/onboarding/questions")]
E   KeyError: ('ether.py', 'GET', '/onboarding/questions')
_______________ test_operational_auth_boundary_source_contracts ________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_operational_auth_boundaries.py:35: in test_operational_auth_boundary_source_contracts
    ether = (REPO_ROOT / "app" / "api_v2_routers" / "ether.py").read_text(encoding="utf-8")
/usr/lib/python3.12/pathlib.py:1029: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
/usr/lib/python3.12/pathlib.py:1015: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
E   FileNotFoundError: [Errno 2] No such file or directory: '/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/app/api_v2_routers/ether.py'
_______________ test_ops_assets_validate_static_deployment_files _______________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_ops_assets.py:22: in test_ops_assets_validate_static_deployment_files
    assert result.returncode == 0, result.stderr + result.stdout
E   AssertionError: Ops asset validation failed: docker/Dockerfile.v2 must use the pinned Python slim base selected for V2
E     
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python', 'scripts/validate_op...='', stderr='Ops asset validation failed: docker/Dockerfile.v2 must use the pinned Python slim base selected for V2\n').returncode
_____ test_phase2_content_generation_check_passes_with_restored_artifacts ______
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_phase2_content_generation_check.py:7: in test_phase2_content_generation_check_passes_with_restored_artifacts
    assert result.failures == []
E   AssertionError: assert ['expected 51...records', ...] == []
E     
E     Left contains 10 more items, first extra item: 'expected 51 generated lesson files'
E     Use -v to get more diff
_______________ test_no_raw_dict_responses_in_production_routers _______________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_no_raw_dict_responses.py:107: in test_no_raw_dict_responses_in_production_routers
    raise AssertionError(msg)
E   AssertionError: 
E   Raw dict responses detected in production routers.
E   Use ok(), fail(), paginated(), route_class=EnvelopedRoute, or add # envelope-exempt: <reason>.
E   
E     app/api_v2_routers/generation.py:301 - bare dict return without ok()/fail()/paginated() or EnvelopedRoute
__________________ test_playwright_default_matches_next_port ___________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_prod_frontend_deployment.py:42: in test_playwright_default_matches_next_port
    assert playwright_uses_next_port(text)
E   assert False
E    +  where False = playwright_uses_next_port('/**\n * playwright.config.ts — EduBoost SA V2\n *\n * Place at the project root:\n *   playwright.config.ts\n *\n * I... // ── Output directories ───────────────────────────────────────────────────────\n  outputDir: "test-results",\n});\n')
__________ test_production_frontend_deployment_status_writes_reports ___________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_prod_frontend_deployment.py:51: in test_production_frontend_deployment_status_writes_reports
    assert status.status == "production-frontend-configured"
E   AssertionError: assert 'deployment-config-not-proven' == 'production-f...nd-configured'
E     
E     - production-frontend-configured
E     + deployment-config-not-proven
________________ test_production_settings_require_key_vault_url ________________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_production_key_vault_behavior.py:16: in test_production_settings_require_key_vault_url
    with pytest.raises(ValueError, match="AZURE_KEY_VAULT_URL is required when APP_ENV is production"):
E   Failed: DID NOT RAISE <class 'ValueError'>
_________ test_production_frontend_deployment_checker_runs_local_mode __________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_prod_frontend_deployment.py:68: in test_production_frontend_deployment_checker_runs_local_mode
    assert result.returncode == 0, result.stdout
E   AssertionError: Production frontend deployment check
E     - INFO status: deployment-config-not-proven
E     - PASS syntax scripts/prod_frontend_deployment.py
E     - PASS syntax scripts/repair_prod_frontend_deployment.py
E     - PASS syntax scripts/check_prod_frontend_deployment.py
E     - PASS syntax tests/unit/test_prod_frontend_deployment.py
E     - PASS focused Ruff production frontend deployment check
E     Failures:
E     - playwright defaults to Next.js port 3050
E     
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python', 'scripts/check_prod_...py\n- PASS focused Ruff production frontend deployment check\nFailures:\n- playwright defaults to Next.js port 3050\n').returncode
________ test_production_frontend_deployment_status_builder_is_passing _________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_prod_frontend_deployment.py:95: in test_production_frontend_deployment_status_builder_is_passing
    assert status.status == "production-frontend-configured"
E   AssertionError: assert 'deployment-config-not-proven' == 'production-f...nd-configured'
E     
E     - production-frontend-configured
E     + deployment-config-not-proven
_________________ test_project_assistance_report_check_passes __________________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_project_assistance_status.py:41: in test_project_assistance_report_check_passes
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: Project assistance status is stale; run make project-assistance-status
E     
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python', 'scripts/project_ass...'--check'], returncode=1, stdout='Project assistance status is stale; run make project-assistance-status\n', stderr='').returncode
__________________ test_repo_hygiene_has_no_current_failures ___________________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_repo_hygiene.py:11: in test_repo_hygiene_has_no_current_failures
    assert failures == []
E   AssertionError: assert [HygieneFailu...t allowlist')] == []
E     
E     Left contains 3 more items, first extra item: HygieneFailure(code='ROOT_CLUTTER', path='.gitleaks.toml', detail='tracked root file is outside the repository root allowlist')
E     Use -v to get more diff
____ test_jobs_have_consent_reminder_aliases_without_missing_direct_symbols ____
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_runtime_blockers_after_followup_audit.py:57: in test_jobs_have_consent_reminder_aliases_without_missing_direct_symbols
    assert "AsyncSessionLocal" not in source
E   assert 'AsyncSessionLocal' not in '"""ARQ back..."),\n    )\n'
E     
E     'AsyncSessionLocal' is contained here:
E       se import AsyncSessionLocal
E               from app.domain.schemas import LessonRequest
E               from app.modules.lessons.service import LessonService
E       
E               async with AsyncSessionLocal() as db:...
E     
E     ...Full output truncated (379 lines hidden), use '-vv' to show
__________________ test_staging_executor_batch_size_respected __________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_seed_staging_review_scopes.py:74: in test_staging_executor_batch_size_respected
    assert res.seeded_count == 5
E   AttributeError: 'NoneType' object has no attribute 'seeded_count'
----------------------------- Captured stdout call -----------------------------
[2m2026-06-24T11:30:40.757399Z[0m [[32m[1minfo     [0m] [1mSeeded batch 0 for scope some_scope: attempted=2, upserted=2, skipped=0, elapsed=0.005s[0m [[0m[1m[34mapp.services.content_staging_seed_executor[0m][0m [36mapp_env[0m=[35mtest[0m [36mapp_version[0m=[35m2.0.0[0m
[2m2026-06-24T11:30:40.759252Z[0m [[32m[1minfo     [0m] [1mSeeded batch 1 for scope some_scope: attempted=2, upserted=2, skipped=0, elapsed=0.001s[0m [[0m[1m[34mapp.services.content_staging_seed_executor[0m][0m [36mapp_env[0m=[35mtest[0m [36mapp_version[0m=[35m2.0.0[0m
[2m2026-06-24T11:30:40.760994Z[0m [[32m[1minfo     [0m] [1mSeeded batch 2 for scope some_scope: attempted=1, upserted=1, skipped=0, elapsed=0.001s[0m [[0m[1m[34mapp.services.content_staging_seed_executor[0m][0m [36mapp_env[0m=[35mtest[0m [36mapp_version[0m=[35m2.0.0[0m
------------------------------ Captured log call -------------------------------
INFO     app.services.content_staging_seed_executor:content_staging_seed_executor.py:230 Seeded batch 0 for scope some_scope: attempted=2, upserted=2, skipped=0, elapsed=0.005s
INFO     app.services.content_staging_seed_executor:content_staging_seed_executor.py:230 Seeded batch 1 for scope some_scope: attempted=2, upserted=2, skipped=0, elapsed=0.001s
INFO     app.services.content_staging_seed_executor:content_staging_seed_executor.py:230 Seeded batch 2 for scope some_scope: attempted=1, upserted=1, skipped=0, elapsed=0.001s
______ test_staging_executor_constraint_violation_retry_record_by_record _______
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_seed_staging_review_scopes.py:106: in test_staging_executor_constraint_violation_retry_record_by_record
    assert res.seeded_count == 3
E   AttributeError: 'NoneType' object has no attribute 'seeded_count'
----------------------------- Captured stdout call -----------------------------
[2m2026-06-24T11:30:40.800752Z[0m [[33m[1mwarning  [0m] [1mIntegrityError in batch commit for scope some_scope, retrying record-by-record: (builtins.NoneType) None
[SQL: mock uniqueness violation]
(Background on this error at: https://sqlalche.me/e/20/gkpj)[0m [[0m[1m[34mapp.services.content_staging_seed_executor[0m][0m [36mapp_env[0m=[35mtest[0m [36mapp_version[0m=[35m2.0.0[0m
------------------------------ Captured log call -------------------------------
WARNING  app.services.content_staging_seed_executor:content_staging_seed_executor.py:235 IntegrityError in batch commit for scope some_scope, retrying record-by-record: (builtins.NoneType) None
[SQL: mock uniqueness violation]
(Background on this error at: https://sqlalche.me/e/20/gkpj)
______ test_sepedi_fal_replaces_generic_first_additional_language_scopes _______
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_inventory_expansion.py:18: in test_sepedi_fal_replaces_generic_first_additional_language_scopes
    assert "grade4_sepedi_first_additional_language_en" in scope_ids
E   AssertionError: assert 'grade4_sepedi_first_additional_language_en' in {'grade4_mathematics_en'}
____ test_coding_and_robotics_review_scopes_are_registered_for_grade_r_to_7 ____
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grader_coding_and_robotics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_source_inventory_expansion.py:36: in test_coding_and_robotics_review_scopes_are_registered_for_grade_r_to_7
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grader_coding_and_robotics_en
_________ test_source_manifest_validation_passes_after_scope_expansion _________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_inventory_expansion.py:65: in test_source_manifest_validation_passes_after_scope_expansion
    assert len(result.generation_ready_scope_ids) == 51
E   AssertionError: assert 1 == 51
E    +  where 1 = len(['grade4_mathematics_en'])
E    +    where ['grade4_mathematics_en'] = SourceManifestValidationResult(errors=[], warnings=[], generation_ready_scope_ids=['grade4_mathematics_en']).generation_ready_scope_ids
____ test_source_inventory_reports_generation_ready_and_missing_source_gaps ____
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_inventory_expansion.py:76: in test_source_inventory_reports_generation_ready_and_missing_source_gaps
    assert rows["grade4_natural_sciences_and_technology_en"]["gap_reason"] == "ok"
E   KeyError: 'grade4_natural_sciences_and_technology_en'
____________ test_source_manifest_validates_hashes_and_scope_links _____________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_manifest_readiness.py:20: in test_source_manifest_validates_hashes_and_scope_links
    assert len(result.generation_ready_scope_ids) == 51
E   AssertionError: assert 1 == 51
E    +  where 1 = len(['grade4_mathematics_en'])
E    +    where ['grade4_mathematics_en'] = SourceManifestValidationResult(errors=[], warnings=[], generation_ready_scope_ids=['grade4_mathematics_en']).generation_ready_scope_ids
_____________ test_generation_ready_can_precede_learner_visibility _____________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade4_natural_sciences_and_technology_en'

The above exception was the direct cause of the following exception:
tests/unit/test_source_manifest_readiness.py:39: in test_generation_ready_can_precede_learner_visibility
    assert generation_ready("grade4_natural_sciences_and_technology_en", registry=registry) is True
scripts/curriculum/validate_source_manifest.py:101: in generation_ready
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade4_natural_sciences_and_technology_en
_______ test_scope_validator_requires_source_readiness_for_active_scope ________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_manifest_readiness.py:51: in test_scope_validator_requires_source_readiness_for_active_scope
    assert result.passed is True
E   AssertionError: assert False is True
E    +  where False = ScopeValidationResult(scope_id='grade4_mathematics_en', status='active', skipped=False, errors=['Scope grade4_mathemat...are artifact path for diagnostic_items.'], item_counts={}, lesson_counts={}, blueprint_counts={}, study_plan_counts={}).passed
_ test_coverage_report_exposes_generation_readiness_separately_from_visibility _
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_manifest_readiness.py:58: in test_coverage_report_exposes_generation_readiness_separately_from_visibility
    assert report["summary"]["scopes.generation_ready"] == 51
E   assert 1 == 51
______ test_source_manifest_local_file_verification_passes_on_vm_sources _______
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_source_manifest_readiness.py:83: in test_source_manifest_local_file_verification_passes_on_vm_sources
    assert result.passed is True
E   AssertionError: assert False is True
E    +  where False = SourceManifestValidationResult(errors=['source document caps_foundation_coding_and_robotics_en path does not exist: da...ource_documents/raw/caps_senior_technology_en.pdf'], warnings=[], generation_ready_scope_ids=['grade4_mathematics_en']).passed
__________________ test_sessions_logout_and_revoke_all_paths ___________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_sprint2_auth_router_delegates.py:124: in test_sessions_logout_and_revoke_all_paths
    revoke_response = await auth.revoke_all_tokens(
app/api_v2_routers/auth.py:212: in revoke_all_tokens
    current_user=current_user.raw_claims,
E   AttributeError: 'dict' object has no attribute 'raw_claims'
______________ test_planned_scopes_are_registered_but_not_active _______________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_study_material_expansion_foundation.py:25: in test_planned_scopes_are_registered_but_not_active
    planned_scope = registry.get_scope("grade5_mathematics_en")
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
__ test_planned_scope_validation_is_skipped_and_not_failed_as_missing_content __
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_study_material_expansion_foundation.py:35: in test_planned_scope_validation_is_skipped_and_not_failed_as_missing_content
    result = validate_scope("grade5_mathematics_en", strict=True)
scripts/curriculum/validate_scope_content.py:57: in validate_scope
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_______________ test_planned_scope_cannot_be_served_to_learners ________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_study_material_expansion_foundation.py:49: in test_planned_scope_cannot_be_served_to_learners
    await service.get_scope_content_summary(NoDbSession(), "grade5_mathematics_en")
app/services/content_learner_read_service.py:313: in get_scope_content_summary
    self._require_learner_visible_scope(scope_id)
app/services/content_learner_read_service.py:91: in _require_learner_visible_scope
    self._scope_registry.require_active_scope(scope_id)
app/services/content_scope_registry.py:59: in require_active_scope
    scope = self.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en

During handling of the above exception, another exception occurred:
tests/unit/test_study_material_expansion_foundation.py:48: in test_planned_scope_cannot_be_served_to_learners
    with pytest.raises(LookupError, match="not active"):
E   AssertionError: Regex pattern did not match.
E    Regex: 'not active'
E    Input: 'Unknown content scope: grade5_mathematics_en'
____ test_generic_scope_validator_preserves_grade4_math_launch_strict_gate _____
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_study_material_expansion_foundation.py:59: in test_generic_scope_validator_preserves_grade4_math_launch_strict_gate
    assert result.passed is True
E   AssertionError: assert False is True
E    +  where False = ScopeValidationResult(scope_id='grade4_mathematics_en', status='active', skipped=False, errors=['Scope grade4_mathemat...are artifact path for diagnostic_items.'], item_counts={}, lesson_counts={}, blueprint_counts={}, study_plan_counts={}).passed
___________ test_coverage_report_separates_active_and_planned_scopes ___________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_study_material_expansion_foundation.py:70: in test_coverage_report_separates_active_and_planned_scopes
    assert report["summary"]["scopes.planned"] > 1
E   KeyError: 'scopes.planned'
_________ test_study_plan_route_imports_consent_gate_and_db_dependency _________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_study_plan_consent_gate_wiring.py:17: in test_study_plan_route_imports_consent_gate_and_db_dependency
    assert "from app.core.database import AsyncSessionLocal, get_db" in source
E   assert 'from app.core.database import AsyncSessionLocal, get_db' in '"""Study plan routes for EduBoost V2."""\n\nfrom fastapi import APIRouter, Depends\nfrom app.core.envelope_route impo...ap_ratio},\n    )\n    return JobAcceptedResponse(job_id=job_id, operation="study_plan_generation", status="queued")\n'
___________ test_generic_scope_builder_generates_valid_launch_slice ____________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_scope_content_builder.py:31: in test_generic_scope_builder_generates_valid_launch_slice
    assert report["blueprint_count"] == 10
E   assert 13 == 10
----------------------------- Captured stdout call -----------------------------
[2m2026-06-24T11:30:42.709650Z[0m [[32m[1minfo     [0m] [1mLoaded CAPS topic map: caps_topic_map_grade4_maths.json (50 refs)[0m [[0m[1m[34mapp.modules.lessons.caps_topic_map_service[0m][0m [36mapp_env[0m=[35mtest[0m [36mapp_version[0m=[35m2.0.0[0m
------------------------------ Captured log call -------------------------------
INFO     app.modules.lessons.caps_topic_map_service:caps_topic_map_service.py:173 Loaded CAPS topic map: caps_topic_map_grade4_maths.json (50 refs)
___________ test_generic_scope_builder_generates_valid_review_scope ____________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_scope_content_builder.py:90: in test_generic_scope_builder_generates_valid_review_scope
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
scripts/curriculum/build_scope_content_artifacts.py:155: in build_scope_content_artifacts
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_______ test_all_generation_ready_scopes_have_generated_artifact_layers ________
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_scope_content_builder.py:123: in test_all_generation_ready_scopes_have_generated_artifact_layers
    assert expected_layers <= set(scope.artifact_paths), scope.scope_id
E   AssertionError: grade4_mathematics_en
E   assert {'assessment_...an_templates'} <= set()
E     
E     Extra items in the left set:
E     'assessment_blueprints'
E     'diagnostic_items'
E     'study_plan_templates'
E     'lessons'
_________________ test_topic_map_review_framework_is_complete __________________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_topic_map_review_framework.py:7: in test_topic_map_review_framework_is_complete
    assert result.failures == []
E   AssertionError: assert ['expected 50...pes, found 1'] == []
E     
E     Left contains 2 more items, first extra item: 'expected 50 review scopes, found 0'
E     Use -v to get more diff
____ test_topic_map_worklist_covers_all_registered_scopes_and_current_gaps _____
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_topic_map_worklist.py:18: in test_topic_map_worklist_covers_all_registered_scopes_and_current_gaps
    assert worklist["summary"]["scopes_total"] == 51
E   assert 1 == 51
__________ test_topic_map_worklist_preserves_source_hashes_for_scope ___________
[gw3] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_topic_map_worklist.py:28: in test_topic_map_worklist_preserves_source_hashes_for_scope
    grade7_math = next(item for item in worklist["items"] if item["scope_id"] == "grade7_mathematics_en")
E   StopIteration
_______ test_topic_map_validator_accepts_current_draft_and_runtime_state _______
[gw4] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_validate_topic_maps.py:15: in test_topic_map_validator_accepts_current_draft_and_runtime_state
    assert result.draft_count == 50
E   assert 0 == 50
E    +  where 0 = TopicMapValidationResult(draft_count=0, runtime_count=51, draft_status_summary=Counter(), runtime_ref_count=1663, errors=[]).draft_count
_________ test_scope_builder_generates_lessons_that_pass_quality_audit _________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:68: in test_scope_builder_generates_lessons_that_pass_quality_audit
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
scripts/curriculum/build_scope_content_artifacts.py:155: in build_scope_content_artifacts
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
__________ test_scope_builder_generates_items_that_pass_quality_audit __________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:85: in test_scope_builder_generates_items_that_pass_quality_audit
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
scripts/curriculum/build_scope_content_artifacts.py:155: in build_scope_content_artifacts
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
______________ test_regenerated_grade6_lessons_pass_quality_audit ______________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade6_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:98: in test_regenerated_grade6_lessons_pass_quality_audit
    result = service.audit_scope("grade6_mathematics_en")
app/services/content_file_lesson_quality.py:46: in audit_scope
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade6_mathematics_en
______________ test_regenerated_grade5_lessons_pass_quality_audit ______________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:107: in test_regenerated_grade5_lessons_pass_quality_audit
    result = service.audit_scope("grade5_mathematics_en")
app/services/content_file_lesson_quality.py:46: in audit_scope
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_______ test_promotion_readiness_blocks_staging_when_lessons_quarantined _______
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade6_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:132: in test_promotion_readiness_blocks_staging_when_lessons_quarantined
    result = service.evaluate_scope("grade6_mathematics_en")
app/services/content_file_promotion_readiness.py:69: in evaluate_scope
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade6_mathematics_en
________________ test_scope_builder_records_source_context_hash ________________
[gw0] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_generated_lesson_quality.py:139: in test_scope_builder_records_source_context_hash
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
scripts/curriculum/build_scope_content_artifacts.py:155: in build_scope_content_artifacts
    scope = registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
_________ test_batch_import_plan_summarizes_dev_approved_review_scopes _________
[gw2] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_file_review_workflow.py:125: in test_batch_import_plan_summarizes_dev_approved_review_scopes
    assert manifest["summary"]["scope_count"] == 50
E   assert 0 == 50
_______________ test_batch_import_plan_builds_rollback_manifest ________________
[gw2] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
tests/unit/test_content_file_review_workflow.py:148: in test_batch_import_plan_builds_rollback_manifest
    assert manifest["summary"]["scope_count"] == 50
E   assert 0 == 50
____________ test_promotion_readiness_reports_pilot_review_evidence ____________
[gw2] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:158: in test_promotion_readiness_reports_pilot_review_evidence
    readiness = ContentFilePromotionReadinessService(project_root=REPO_ROOT).evaluate_scope("grade5_mathematics_en")
app/services/content_file_promotion_readiness.py:69: in evaluate_scope
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
___________ test_file_artifact_import_is_idempotent_for_pilot_scope ____________
[gw2] linux -- Python 3.12.3 /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/.venv/bin/python
app/services/content_scope_registry.py:66: in get_scope
    return self._scopes[scope_id]
E   KeyError: 'grade5_mathematics_en'

The above exception was the direct cause of the following exception:
tests/unit/test_content_file_review_workflow.py:212: in test_file_artifact_import_is_idempotent_for_pilot_scope
    review_service.build_review_packet("grade5_mathematics_en")
app/services/content_file_review_workflow.py:72: in build_review_packet
    scope = self.registry.get_scope(scope_id)
app/services/content_scope_registry.py:68: in get_scope
    raise LookupError(f"Unknown content scope: {scope_id}") from exc
E   LookupError: Unknown content scope: grade5_mathematics_en
=============================== warnings summary ===============================
tests/unit/test_popia_erasure_safety.py::TestPhysicalDeleteSafety::test_physical_delete_returns_false_on_no_rows
tests/unit/test_popia_erasure_safety.py::TestErasureRequestStateMachine::test_postflight_verification_soft_delete_pii_erased
tests/unit/test_popia_export_completeness.py::TestExportPayloadCompleteness::test_learner_profile_contains_all_required_fields
tests/unit/test_popia_export_completeness.py::TestExportPayloadCompleteness::test_knowledge_gaps_structure
tests/unit/test_v2_services_full.py::TestParentReportServiceV2::test_list_reports
tests/unit/test_guardian_consent_withdrawal.py::TestProcessingBlocking::test_consent_withdrawn_audit_event_logged
  /usr/lib/python3.12/unittest/mock.py:2188: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def __init__(self, name, parent):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_popia_erasure_safety.py::TestErasureRequestStateMachine::test_request_erasure_blocks_duplicate_requests
  /usr/lib/python3.12/typing.py:2154: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def cast(typ, val):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_popia_service.py::test_cancel_erasure_restores_learner
  /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/app/services/popia_service.py:288: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    self.db.add(erasure_request)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_popia_service.py::test_cancel_erasure_restores_learner
  /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/app/services/popia_service.py:294: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    self.db.add(learner)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_popia_service.py::test_request_correction_with_allowed_fields
  /home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1/app/services/popia_service.py:333: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    self.db.add(learner)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_v2_services.py::test_learner_service_returns_summary
  /usr/lib/python3.12/unittest/mock.py:653: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def __getattr__(self, name):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_api_v2_router_contract.py::test_registered_router_fragments_are_exposed_under_each_v2_prefix
FAILED tests/unit/modules/diagnostics/test_item_bank_models.py::TestDiagnosticItemProperties::test_is_available_true_when_approved_and_under_cap
FAILED tests/unit/modules/diagnostics/test_item_bank_service.py::test_select_item_picks_nearest_b_to_theta
FAILED tests/unit/modules/diagnostics/test_item_bank_service.py::test_select_item_expands_window_when_neighbourhood_empty
FAILED tests/unit/test_consent_state_machine.py::test_days_until_expiry_returns_positive_for_future
FAILED tests/unit/test_content_coverage_service.py::test_future_layers_return_configured_zero_count_placeholders
FAILED tests/unit/test_content_factory_enums.py::TestContentArtifactStatusEnum::test_no_undeclared_orm_values
FAILED tests/unit/test_content_staging_seed_executor.py::test_valid_approved_artifact_creates_seed_item
FAILED tests/unit/test_ci_auth_refresh_db_proof_workflow.py::test_auth_refresh_db_proof_workflow_runs_proof_and_evidence_gate
FAILED tests/unit/test_ci_auth_refresh_db_proof_workflow.py::test_ci_auth_refresh_db_proof_workflow_status_passing
FAILED tests/unit/test_ci_auth_refresh_db_proof_workflow.py::test_ci_auth_refresh_db_proof_workflow_status_writes_reports
FAILED tests/unit/test_ci_auth_refresh_db_proof_workflow.py::test_ci_auth_refresh_db_proof_workflow_checker_runs_local_mode
FAILED tests/unit/test_etl_mcp_server_startup.py::test_etl_mcp_server_uses_json_response_mode
FAILED tests/unit/test_etl_mcp_server_startup.py::test_start_streamable_http_falls_back_to_settings
FAILED tests/unit/test_diagnostic_score_live_audit.py::test_bridge_expression_maps_item_id_from_irt_id
FAILED tests/unit/test_content_factory_table_reconciliation.py::TestOrmTableNameReconciliation::test_no_undeclared_orm_models
FAILED tests/unit/test_content_file_promotion_readiness.py::test_file_promotion_readiness_marks_review_scopes_staging_ready_not_production_ready
FAILED tests/unit/test_content_file_promotion_readiness.py::test_file_promotion_readiness_writes_summary_and_per_scope_manifests
FAILED tests/unit/test_content_file_promotion_readiness.py::test_registry_coverage_report_includes_layer_files_and_promotion_readiness
FAILED tests/unit/test_content_file_review_workflow.py::test_pilot_review_packet_defaults_to_pending_educator_approval
FAILED tests/unit/test_content_file_review_workflow.py::test_dev_approved_review_packet_unlocks_staging_but_not_production
FAILED tests/unit/test_content_file_review_workflow.py::test_educator_and_legal_approval_unlocks_production_review_evidence
FAILED tests/unit/test_content_file_review_workflow.py::test_placeholder_approval_urls_do_not_unlock_production
FAILED tests/unit/test_content_file_review_workflow.py::test_import_plan_uses_pending_review_until_educator_approval
FAILED tests/unit/test_content_file_review_workflow.py::test_import_plan_switches_to_approved_with_dev_approval
FAILED tests/unit/test_operational_auth_boundaries.py::test_operational_auth_boundary_matrix_statuses
FAILED tests/unit/test_operational_auth_boundaries.py::test_operational_auth_boundary_source_contracts
FAILED tests/unit/test_ops_assets.py::test_ops_assets_validate_static_deployment_files
FAILED tests/unit/test_phase2_content_generation_check.py::test_phase2_content_generation_check_passes_with_restored_artifacts
FAILED tests/unit/test_no_raw_dict_responses.py::test_no_raw_dict_responses_in_production_routers
FAILED tests/unit/test_prod_frontend_deployment.py::test_playwright_default_matches_next_port
FAILED tests/unit/test_prod_frontend_deployment.py::test_production_frontend_deployment_status_writes_reports
FAILED tests/unit/test_production_key_vault_behavior.py::test_production_settings_require_key_vault_url
FAILED tests/unit/test_prod_frontend_deployment.py::test_production_frontend_deployment_checker_runs_local_mode
FAILED tests/unit/test_prod_frontend_deployment.py::test_production_frontend_deployment_status_builder_is_passing
FAILED tests/unit/test_project_assistance_status.py::test_project_assistance_report_check_passes
FAILED tests/unit/test_repo_hygiene.py::test_repo_hygiene_has_no_current_failures
FAILED tests/unit/test_runtime_blockers_after_followup_audit.py::test_jobs_have_consent_reminder_aliases_without_missing_direct_symbols
FAILED tests/unit/test_seed_staging_review_scopes.py::test_staging_executor_batch_size_respected
FAILED tests/unit/test_seed_staging_review_scopes.py::test_staging_executor_constraint_violation_retry_record_by_record
FAILED tests/unit/test_source_inventory_expansion.py::test_sepedi_fal_replaces_generic_first_additional_language_scopes
FAILED tests/unit/test_source_inventory_expansion.py::test_coding_and_robotics_review_scopes_are_registered_for_grade_r_to_7
FAILED tests/unit/test_source_inventory_expansion.py::test_source_manifest_validation_passes_after_scope_expansion
FAILED tests/unit/test_source_inventory_expansion.py::test_source_inventory_reports_generation_ready_and_missing_source_gaps
FAILED tests/unit/test_source_manifest_readiness.py::test_source_manifest_validates_hashes_and_scope_links
FAILED tests/unit/test_source_manifest_readiness.py::test_generation_ready_can_precede_learner_visibility
FAILED tests/unit/test_source_manifest_readiness.py::test_scope_validator_requires_source_readiness_for_active_scope
FAILED tests/unit/test_source_manifest_readiness.py::test_coverage_report_exposes_generation_readiness_separately_from_visibility
FAILED tests/unit/test_source_manifest_readiness.py::test_source_manifest_local_file_verification_passes_on_vm_sources
FAILED tests/unit/test_sprint2_auth_router_delegates.py::test_sessions_logout_and_revoke_all_paths
FAILED tests/unit/test_study_material_expansion_foundation.py::test_planned_scopes_are_registered_but_not_active
FAILED tests/unit/test_study_material_expansion_foundation.py::test_planned_scope_validation_is_skipped_and_not_failed_as_missing_content
FAILED tests/unit/test_study_material_expansion_foundation.py::test_planned_scope_cannot_be_served_to_learners
FAILED tests/unit/test_study_material_expansion_foundation.py::test_generic_scope_validator_preserves_grade4_math_launch_strict_gate
FAILED tests/unit/test_study_material_expansion_foundation.py::test_coverage_report_separates_active_and_planned_scopes
FAILED tests/unit/test_study_plan_consent_gate_wiring.py::test_study_plan_route_imports_consent_gate_and_db_dependency
FAILED tests/unit/test_scope_content_builder.py::test_generic_scope_builder_generates_valid_launch_slice
FAILED tests/unit/test_scope_content_builder.py::test_generic_scope_builder_generates_valid_review_scope
FAILED tests/unit/test_scope_content_builder.py::test_all_generation_ready_scopes_have_generated_artifact_layers
FAILED tests/unit/test_topic_map_review_framework.py::test_topic_map_review_framework_is_complete
FAILED tests/unit/test_topic_map_worklist.py::test_topic_map_worklist_covers_all_registered_scopes_and_current_gaps
FAILED tests/unit/test_topic_map_worklist.py::test_topic_map_worklist_preserves_source_hashes_for_scope
FAILED tests/unit/test_validate_topic_maps.py::test_topic_map_validator_accepts_current_draft_and_runtime_state
FAILED tests/unit/test_generated_lesson_quality.py::test_scope_builder_generates_lessons_that_pass_quality_audit
FAILED tests/unit/test_generated_lesson_quality.py::test_scope_builder_generates_items_that_pass_quality_audit
FAILED tests/unit/test_generated_lesson_quality.py::test_regenerated_grade6_lessons_pass_quality_audit
FAILED tests/unit/test_generated_lesson_quality.py::test_regenerated_grade5_lessons_pass_quality_audit
FAILED tests/unit/test_generated_lesson_quality.py::test_promotion_readiness_blocks_staging_when_lessons_quarantined
FAILED tests/unit/test_generated_lesson_quality.py::test_scope_builder_records_source_context_hash
FAILED tests/unit/test_content_file_review_workflow.py::test_batch_import_plan_summarizes_dev_approved_review_scopes
FAILED tests/unit/test_content_file_review_workflow.py::test_batch_import_plan_builds_rollback_manifest
FAILED tests/unit/test_content_file_review_workflow.py::test_promotion_readiness_reports_pilot_review_evidence
FAILED tests/unit/test_content_file_review_workflow.py::test_file_artifact_import_is_idempotent_for_pilot_scope
73 failed, 2204 passed, 11 skipped, 1 xfailed, 11 warnings in 239.53s (0:03:59) exits 0 from a clean implementation commit.
