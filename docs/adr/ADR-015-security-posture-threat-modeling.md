# ADR-015: Security Posture and Threat Modeling Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will maintain a documented security posture using threat modeling, secure defaults, vulnerability management, secret scanning, dependency and supply-chain controls, security testing, risk acceptance, and incident response evidence.

## Rationale

EduBoost handles learner, parent, assessment, privacy, AI, billing, and communication workflows. These domains require explicit security controls, documented threat assumptions, release-blocking vulnerability policy, and auditable risk ownership.

## Required Controls

- threat model is required
- secure defaults are required
- vulnerability management is required
- secret scanning is required
- dependency scanning is required
- supply-chain controls are required
- security headers are required
- incident response runbooks are required
- risk acceptance register is required
- high and critical vulnerabilities must block release unless formally accepted according to policy
- critical risks cannot be accepted for production by default

## Boundary

This ADR records security posture and threat-modeling decision evidence. It does not run a live penetration test, configure cloud security posture, or authorize production launch.
