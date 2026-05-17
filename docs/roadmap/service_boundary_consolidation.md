# Service Boundary Consolidation

**Status:** pending targeted refactor

Do not delete `app/services/` wholesale. After post-530 runtime facades, `app/services/` contains active cross-cutting runtime code.

Only delete files proven unused by import/call-site scan and full tests.
