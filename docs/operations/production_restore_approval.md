# Production Restore Approval Guard

## Purpose

Production database restore must be blocked unless an explicit approval record
exists and the restore command is invoked with production override intent.

## Required Approval Fields

- backup artifact ID
- target environment
- approver
- approval ticket
- approval timestamp
- integrity status
- rollback plan

## Guard Rules

- production restore requires `--allow-production-target`
- production restore requires an approval record
- approval record must include backup artifact ID
- approval record must include rollback plan
- staging restore dry-run remains allowed without production approval

## Command

```bash
make production-restore-approval-check
```
