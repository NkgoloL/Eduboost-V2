# Deployment Gate and Rollback Contract

## Purpose

This contract defines staging and production deployment gates, smoke tests, and rollback expectations.

## Required Staging Gate

- lint check
- unit test check
- security scan check
- Docker build check
- migration check
- staging smoke test
- rollback plan
- release notes

## Required Production Gate

- lint check
- typecheck check
- unit test check
- integration test check
- security scan check
- Docker build check
- migration check
- smoke test
- release notes
- manual production approval
- rollback plan

## Required Rollback Controls

- rollback command is documented
- database rollback policy is documented
- feature flag rollback is supported
- previous image is retained
- post-rollback smoke test is required
- rollback incident record is required

## Boundary

This contract records deployment-gate and rollback readiness. It does not deploy or rollback services.
