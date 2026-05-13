# Security Test Strategy Contract

## Purpose

This contract defines required security tests for pull request, staging, and production gates.

## Required Security Tests

- SAST
- dependency scan
- secret scan
- container scan
- DAST
- API fuzzing
- config audit
- threat model review

## Required Gate Rules

- SAST must run for pull requests
- dependency scan must run for pull requests
- secret scan must run for pull requests
- production security tests must also gate staging
- production security tests must block release
- security test artifacts must be retained under controlled paths

## Boundary

This contract records security-test readiness. It does not execute security tests.
