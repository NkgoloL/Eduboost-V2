# V2 Handoff Guide for Less Capable Agents

This page explains how to continue the V2 work safely.

## Most important rule

Work in V2 first:

- `app/api_v2.py`
- `app/api_v2_routers/`
- `app/services/`
- `app/repositories/`

Do **not** start new work in legacy runtime files unless the V2 path truly has no equivalent.

## Simple checklist

1. Read `audits/roadmaps/V2_Outstanding_Task_Roadmap.md`
2. Pick one outstanding task only
3. Add or improve tests first if possible
4. Make the code change
5. Update docs/tracking files
6. Commit

## Good task examples

- move DB logic from a V2 service into a repository
- add a unit test for a V2 router request model
- improve a V2 service to use DB-backed data
- improve V2 docs or startup instructions

## Bad task examples

- deleting legacy runtime without replacement
- rewriting multiple architectures at once
- changing audit files by guessing old text
