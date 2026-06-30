# Test Strategy Matrix Contract

## Purpose

This contract defines the test strategy matrix for production readiness.

## Required Matrix Fields

- test layer
- command
- owner
- required for pull request
- required for staging
- required for production
- deterministic execution
- artifact path

## Required Layer Rules

- production tests must also gate staging
- pull request tests must be deterministic
- security tests require evidence artifacts
- accessibility tests require evidence artifacts
- performance tests require evidence artifacts
- E2E tests require evidence artifacts
- OpenAPI contract tests must detect drift
- smoke tests must be retained for release evidence

## Boundary

This contract records test strategy readiness. It does not execute tests.
