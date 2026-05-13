# Documentation Inventory Contract

## Required Inventory Fields

- path
- title
- audience
- status
- owner
- reviewed-on date
- review interval days
- source-of-truth flag
- supersedes reference where applicable

## Required Audiences

- developer
- operator
- reviewer
- support
- privacy
- security
- product
- end user

## Required Rules

- documentation path must live under docs/
- documentation owner is required
- active operator docs must identify source-of-truth status
- active security docs must identify source-of-truth status
- active privacy docs must identify source-of-truth status
- superseded documentation must identify replacement or successor

## Boundary

This contract records documentation inventory readiness. It does not publish documentation.
