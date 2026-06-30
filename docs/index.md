# EduBoost V2

EduBoost V2 is the active development runtime for EduBoost SA.

This documentation set is meant to stay close to the repository as it exists on
current `master`: architecture notes, operational guidance, compliance
documentation, and generated API references all live together here.

The most useful starting points are:

- [`project_status.md`](project_status.md) for the current repository and docs
  sync snapshot
- [`operations/recommended_operating_model.md`](operations/recommended_operating_model.md)
  for the five-part operating model used to plan, review, and release work
- [`operations/project_assistance_status.md`](operations/project_assistance_status.md)
  for the five project assistance lanes and their current command surface
- [`operations/todo_implementation_plan.md`](operations/todo_implementation_plan.md)
  for the wave-by-wave implementation plan covering every outstanding TODO item
- [`architecture.md`](architecture.md) for the modular-monolith layout
- [`api_v2.md`](api_v2.md) for the public runtime surface
- [`reference/api_v2.md`](reference/api_v2.md) for generated API docs

The repository is V2-first, but a small compatibility boundary still exists for
migration support. When in doubt, prefer the docs that describe the active V2
surface and check the root [`TODO.md`](/TODO.md) for audit-tracked follow-up
work and the current North Star execution state.
