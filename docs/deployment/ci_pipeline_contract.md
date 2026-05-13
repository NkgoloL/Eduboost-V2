# CI Pipeline Contract

## Purpose

This contract defines required CI checks for pull requests, staging deployment, and production deployment.

## Required CI Checks

- lint
- typecheck
- unit tests
- integration tests
- security scan
- Docker build
- migration check
- OpenAPI drift check
- generated artifact drift check
- frontend build where applicable
- smoke tests for staging and production gates

## Required Blocking Rules

- production-required checks must block deploy
- security scan must run for pull requests
- migration check must run before staging
- failed OpenAPI drift check blocks merge
- failed generated artifact drift check blocks merge
- failed unit tests block merge
- failed smoke tests block deployment promotion

## Boundary

This contract records CI pipeline readiness. It does not execute CI jobs or modify branch protection rules.
