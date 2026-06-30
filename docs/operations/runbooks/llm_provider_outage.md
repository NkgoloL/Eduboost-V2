# Runbook: LLM Provider Outage

**Last Updated**: 2026-06-12  
**Severity**: High  
**SLA Impact**: Lesson generation and diagnostics unavailable

---

## Symptoms

- Lesson generation requests timeout or return 503
- Diagnostic scoring fails
- Error rate spikes on `/api/v2/lessons/generate` and `/api/v2/diagnostics/submit`
- AI-related metrics show 100% failure rate

---

## Diagnosis

### Step 1: Verify Provider Status

```bash
# Check Groq status
curl -s https://status.groq.com | jq '.status'

# Check Anthropic status  
curl -s https://status.anthropic.com | jq '.status'
```

### Step 2: Test Connectivity

```bash
# Test Groq API
curl -s -H "Authorization: Bearer $GROQ_API_KEY" \
  "https://api.groq.com/openai/v1/models" | jq '.data'

# Test Anthropic API
curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
  "https://api.anthropic.com/v1/models" | jq '.data'
```

### Step 3: Check Application Logs

```bash
# Look for LLM errors
kubectl logs -l app=api -n eduboost | grep -i "groq\|anthropic\|llm\|rate"

# Check error types
kubectl logs -l app=api -n eduboost | jq -c 'select(.severity=="ERROR")'
```

---

## Resolution

### Scenario A: Primary Provider (Groq) Down

**Action**: Automatic fallback to Anthropic

The application is configured with automatic fallback. If Groq is unavailable, it should automatically use Anthropic.

```bash
# Verify fallback is working
kubectl logs -l app=api -n eduboost | grep -i "fallback"

# If fallback not working, check configuration
grep -r "fallback\|LLM_PROVIDER" app/core/config.py
```

**If fallback not triggered**, restart pods:

```bash
kubectl rollout restart deployment/eduboost-v2-api -n eduboost
```

### Scenario B: Both Providers Down

**Action**: Enable graceful degradation

1. **Disable AI features**:
   ```bash
   # Set feature flag via config
   # This returns pre-built lessons only
   ```

2. **Notify users**:
   ```
   🔶 Service Notice: AI features temporarily limited
   
   Some AI-powered features are unavailable. 
   Pre-built content is still accessible.
   ```

### Scenario C: Rate Limiting

**Action**: Implement backoff

- Current limit: 20 requests/minute (configurable)
- Check if burst exceeded

```bash
# Check rate limit settings
grep -r "RATE_LIMIT" app/core/config.py
```

---

## Communication Template

### Internal Alert

```
🚨 INCIDENT: LLM Provider Outage

Primary: Groq
Status: Investigating
Impact: Lesson generation failing
Fallback: Anthropic (testing)
```

### User Notification

```
🟡 Service Notice: Some features may be slower than usual

Our AI provider is experiencing issues.
We've enabled backup systems to minimize disruption.
```

---

## Post-Incident

1. **Document** incident duration and impact
2. **Review** provider status pages for patterns
3. **Consider** adding more fallback providers
4. **Update** runbook with new learnings

---

## Contacts

| Role | Contact |
|------|---------|
| On-call Engineer | PagerDuty |
| Groq Support | support@groq.com (if enterprise) |
| Anthropic Support | support@anthropic.com |

---

## References

- LLM Provider Configuration: `app/core/config.py`
- Fallback Implementation: `app/services/llm_provider.py`
- Rate Limiting: `app/core/rate_limit.py`