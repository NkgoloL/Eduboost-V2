# AI Refusal Regression Fixtures

## Purpose

Refusal fixtures validate that unsafe, privacy-invasive, or hidden-prompt
requests produce safe refusal records without live model calls.

## Fixture Categories

- unsafe instruction
- privacy leakage
- hidden prompt disclosure

## Required Refusal Fields

- case ID
- category
- safety status
- refusal reason
- safe educational redirection
- no unsafe operational detail
- no hidden prompt disclosure

## Command

```bash
make ai-refusal-fixture-check
```
