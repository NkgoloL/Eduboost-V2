# Logging and Tracing Contract

## Purpose

This contract defines structured logging and distributed tracing requirements.

## Required Log Fields

- request_id
- trace_id
- span_id
- user_scope
- service
- environment
- route or operation
- status or outcome
- duration where applicable

## Prohibited Log Fields

- password
- raw prompt
- raw AI output
- raw provider payload
- card number
- learner name where not required
- email address before redaction
- phone number before redaction
- South African ID number before redaction

## Required Trace Controls

- API request span
- database query span
- LLM provider request span
- billing webhook span
- notification provider span
- error sampling
- request ID propagation
- trace ID propagation
- PII-safe attributes only

## Boundary

This contract records logging and tracing readiness. It does not configure a live collector or export production traces.
