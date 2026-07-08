# PRD-0.6 Workflow Command Hygiene and CI Inventory Schema

The generated `workflow_command_hygiene_ci_inventory.json` file must contain:

- `schema_version`: `prd-workflow-command-hygiene-ci-inventory/v1`
- `prd_id`: `PRD-0.6`
- workflow counts
- direct pytest command inventory
- module pytest command inventory
- requirements/dev install inventory
- per-workflow SHA-256 entries
- authority boundaries
- command hygiene policy

Final PRD-0.6 validity requires `direct_pytest_command_count` to be `0` after the workflow hygiene rewrite.
