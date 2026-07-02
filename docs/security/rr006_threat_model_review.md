# RR-006 Threat Model Review

**Status:** required security review artifact  
**Register item:** RR-006  
**Primary threat model:** `docs/security/threat_model_v2.md`

## Review basis

The V2 threat model must remain aligned to the current controlled-beta architecture and must cover at least:

- authentication and session management;
- object-level authorization and IDOR risk;
- POPIA data rights and learner data handling;
- API and route-boundary exposure;
- LLM/prompt-injection and PII re-appearance risk;
- dependency and supply-chain risk;
- secrets and environment configuration;
- operational monitoring and incident response.

## Current RR-006 decision

Threat model review complete: true  
Threat model method includes STRIDE: true  
Learner-data risk reviewed: true  
LLM risk reviewed: true  
Dependency/supply-chain risk reviewed: true  
Runtime KG implementation claimed: false

## Required follow-up discipline

Any future public-beta or production-release slice must cite this review and either confirm it remains current or create a new security review record.
