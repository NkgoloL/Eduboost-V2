# Production LLM Gateway Contract

## Purpose

This contract defines the canonical LLM gateway interface for EduBoost lesson generation and AI-assisted learning flows.

## Required gateway metadata

- provider name is required in gateway metadata
- model/version is required in gateway metadata
- prompt template version is required in gateway metadata
- input schema is required in gateway metadata
- output schema is required in gateway metadata
- latency is required in gateway metadata
- token usage is required in gateway metadata
- safety status is required in gateway metadata
- fallback status is required in gateway metadata
- timeout per provider is recorded
- retry policy per provider is recorded
- circuit breaker status is recorded
- budget guardrail status is recorded

## Required gateway controls

- provider fallback is supported
- deterministic mock provider is supported
- local/offline fallback is development-only
- provider health checks are supported
- emergency flag DISABLE_LESSON_GENERATION disables lesson generation
- model comparison harness remains a post-baseline optimisation

## Boundary

This repository-side LLM gateway contract records deterministic implementation evidence only. It does not call external providers, provision GPU capacity, certify model quality, or replace human AI-safety review.
