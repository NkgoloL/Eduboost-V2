# ADR 0003: LLM Provider Abstraction

## Status
Accepted

## Context
EduBoost uses LLMs for lesson generation, explanations, diagnostics support, and content transformation. Provider APIs, model capabilities, pricing, latency, and safety characteristics can change. Direct provider coupling would make cost control, testing, and safety validation brittle.

## Decision
EduBoost will use a provider abstraction for LLM calls.

- Application code should call an internal LLM gateway/service rather than provider SDKs directly.
- Providers must be swappable through configuration and capability checks.
- Structured output contracts and validators sit outside individual provider clients.
- Tests should use deterministic fake/mock providers for golden-output and safety-gate scenarios.
- Provider-specific errors must be normalised before reaching domain services.

## Consequences

- **Pros**: Better testability, easier provider migration, clearer cost/safety controls, deterministic CI.
- **Cons**: Additional abstraction layer and some lowest-common-denominator pressure across model features.
