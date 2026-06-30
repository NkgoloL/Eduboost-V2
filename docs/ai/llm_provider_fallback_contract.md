# LLM Provider Fallback Contract

## Purpose

LLM provider fallback must preserve CAPS alignment, safety boundaries, timeout
limits, retry limits, and privacy boundaries when the primary provider is
unavailable.

## Required Configuration

- `LLM_PROVIDER`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_RETRIES`
- `ANTHROPIC_MODEL`
- `LOCAL_BASE_MODEL_ID`
- `LOCAL_ADAPTER_PATH`
- `LOCAL_MERGED_MODEL_PATH`
- `LOCAL_LLM_MAX_NEW_TOKENS`
- `LOCAL_LLM_TEMPERATURE`

## Fallback Rules

- fallback must not bypass consent or object authorization
- fallback must preserve CAPS-aligned prompt inputs
- fallback must preserve AI safety boundary instructions
- fallback must not expose provider secrets
- fallback must fail closed when no safe provider is available
- local fallback must use bounded token and temperature settings

## Evidence Command

```bash
make llm-provider-fallback-contract-check
```
