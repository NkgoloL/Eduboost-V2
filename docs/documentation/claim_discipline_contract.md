# Claim Discipline Contract

## Purpose

This contract defines claim boundaries for production-readiness evidence.

## Required Claim Types

- repository evidence
- manual approval
- external system
- production runtime
- legal review
- security review

## Required Confidence Values

- verified
- verify pending
- manual only
- unsupported

## Required Rules

- verified claims require evidence paths
- external claims require external dependency note
- manual approval claims require external dependency note
- legal review claims require external dependency note
- security review claims require external dependency note
- unsupported claims are not allowed in production readiness evidence
- production claims must be verified or clearly excluded
- broad production claims require boundary wording

## Prohibited Unbounded Phrases

- fully complete
- guaranteed
- launch approved
- production ready

## Required Boundary Phrase

This repository-side evidence does not authorize production launch.

## Boundary

This contract records claim-discipline readiness. It does not validate external/manual approvals.
