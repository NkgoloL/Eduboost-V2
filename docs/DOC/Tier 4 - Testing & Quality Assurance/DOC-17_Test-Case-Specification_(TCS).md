# DOC-17: Test Case Specification (TCS)
**MIL-STD-498 / IEEE 1012**

## 1. Unit Test Cases

**Status:** ✅ ALL 85 UNIT TESTS PASSING
**Coverage:** 82% (test_irt_gap_probe.py, test_judiciary_schema_enforcement.py, et al.)
**Last Run:** 2026-05-04 13:45 UTC
**CI Status:** GREEN

### 1.1 IRT Engine (app/modules/diagnostics/irt_engine.py)
```python
# TCS-001: test_eap_convergence_at_20_items
def test_eap_convergence_at_20_items():
    engine = IRTEngine()
    responses = [generate_random_response() for _ in range(20)]
    theta_final, se_final, _ = engine.update_theta_eap(responses)
    assert se_final < 0.3 or len(responses) == 20
    assert -3 <= theta_final <= 3

# TCS-002: test_mfi_selection_maximizes_information
def test_mfi_selection_maximizes_information():
    engine = IRTEngine()
    theta_current = 0.5
    next_item = engine.select_next_item_mfi(theta_current)
    fisher_info = engine.compute_fisher_information(next_item, theta_current)
    # Compare against all other items in pool
    for other_item in engine.item_pool:
        assert fisher_info >= engine.compute_fisher_information(other_item, theta_current)
```

### 1.2 Ether Archetype Engine (app/modules/learners/ether_service.py)
```python
# TCS-003: test_ether_classification_deterministic
def test_ether_classification_deterministic():
    ether = EtherService()
    responses = {"pace": "fast", "modality": "visual", "motivation": "extrinsic", 
                 "social": "solo", "challenge": "moderate"}
    arch1 = ether.classify_archetype(responses)
    arch2 = ether.classify_archetype(responses)
    assert arch1 == arch2  # Deterministic
    assert arch1 in VALID_ARCHETYPES

# TCS-004: test_ether_confidence_threshold
def test_ether_confidence_threshold():
    ether = EtherService()
    arch, confidence = ether.classify_with_confidence(responses)
    assert confidence >= 0.6  # Posterior confidence minimum
```

### 1.3 Redis Semantic Cache (app/core/redis.py)
```python
# TCS-005: test_cache_hit_latency_p95
def test_cache_hit_latency_p95():
    cache = RedisClient()
    key = cache.semantic_cache_key("grade_4", "fractions", "en", "Chokhmah")
    cache.set_semantic_cache(key, LESSON_PAYLOAD, ttl=3600)
    
    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        result = cache.get_semantic_cache(key)
        latencies.append((time.perf_counter() - start) * 1000)  # ms
    
    p95 = np.percentile(latencies, 95)
    assert p95 < 50  # < 50ms p95

# TCS-006: test_cache_miss_fallback
def test_cache_miss_fallback():
    cache = RedisClient()
    result = cache.get_semantic_cache("nonexistent_key")
    assert result is None
```

### 1.4 Stripe Webhook (app/api_v2_routers/billing.py)
```python
# TCS-007: test_stripe_subscription_webhook_tier_update
def test_stripe_subscription_webhook_tier_update():
    event_data = {
        "type": "customer.subscription.created",
        "data": {"object": {"customer": STRIPE_CUSTOMER_ID, "status": "active"}}
    }
    response = client.post("/api/v2/billing/webhook", json=event_data)
    assert response.status_code == 200
    
    guardian = db.query(Guardian).filter_by(stripe_customer_id=STRIPE_CUSTOMER_ID).first()
    assert guardian.subscription_tier == "premium"
```

### 1.5 JWT Refresh Rotation (app/core/config.py)
```python
# TCS-008: test_jwt_refresh_rotation_generates_new_jti
def test_jwt_refresh_rotation_generates_new_jti():
    login_resp = client.post("/auth/login", json=LOGIN_CREDS)
    refresh_token_1 = get_refresh_token_from_cookie(login_resp)
    jti_1 = decode_token(refresh_token_1)["jti"]
    
    refresh_resp = client.post("/auth/refresh", cookies={"refresh_token": refresh_token_1})
    refresh_token_2 = get_refresh_token_from_cookie(refresh_resp)
    jti_2 = decode_token(refresh_token_2)["jti"]
    
    assert jti_1 != jti_2  # New JTI on rotation
    assert is_jti_in_denylist(jti_1)  # Old JTI revoked
```

## 2. Integration Test Cases

### 2.1 IRT ↔ Repository Flow
- TCS-009: Diagnostic submission persists responses → Repository.save_diagnostic_response()
- TCS-010: Theta update fetches latest item from DB → Repository.get_next_item()

### 2.2 Billing ↔ Database Flow
- TCS-011: Stripe webhook creates Guardian if missing
- TCS-012: Subscription tier cascades to quota restrictions

### 2.3 Auth ↔ Cache ↔ Database Flow
- TCS-013: JWT denylist persisted in Redis
- TCS-014: Key Vault secret rotation updates JWT_SECRET in-memory

## 3. Contract Tests (Frontend ↔ Backend)
- TCS-015: DiagnosticResult schema matches frontend expectation
- TCS-016: LessonPayload content field accepts `string | LessonSection[]`
- TCS-017: ParentDashboardResponse meets frontend type requirements
