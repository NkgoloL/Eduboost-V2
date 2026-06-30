# Phase 0 — Domain D — Alertmanager / Observability Evidence

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Scope:** T030, T031, T032
**Tools used:** `amtool 0.27.0`, `promtool 3.11.3`.

---

## T030 — Audit Alertmanager URLs and placeholders

**Status:** Done.

| Receiver | Field | Pre-fix value | Strategy decision |
|---|---|---|---|
| `slack-default` | `slack_configs[0].api_url` | `${ALERTMANAGER_SLACK_WEBHOOK}` (literal placeholder; rejected by raw `amtool`) | Replace with `api_url_file` pointing at an orchestrator-mounted secret file. |

The audit baseline noted "every empty URL value, unsupported literal
placeholder (`${VAR}` syntax)". The actual repository contains exactly one
URL and exactly one unsupported placeholder. No empty URLs, no other env
tokens.

Reproduction of the pre-fix failure:

```text
$ amtool check-config alertmanager/alertmanager.yml
Checking 'alertmanager/alertmanager.yml'  FAILED: unsupported scheme "" for URL
amtool: error: failed to validate 1 file(s)
```

**AC met.** Every receiver URL has an explicit deployment strategy decided
and documented in this file and in `docs/operations/alertmanager.md`.

---

## T031 — Fix Alertmanager config render strategy

**Status:** Done. Strategy chosen: **(c) native `api_url_file` (no template
rendering)**.

The TODO offered two strategies. I selected a third, cleaner option that
Alertmanager supports natively: the checked-in YAML is the exact deployed
artifact, and the secret is mounted into the container by the orchestrator.
This avoids a fragile template-rendering pipeline and avoids smuggling
secrets through environment variables.

### Changes applied

- `alertmanager/alertmanager.yml` — `api_url: ${ALERTMANAGER_SLACK_WEBHOOK}` →
  `api_url_file: /etc/alertmanager/secrets/slack_webhook_url`. Added a
  documentation header pointing at the new operations doc.
- `alertmanager/rules/item_bank_coverage.yml` — repaired a Go-template syntax
  error in the `ItemBankCoverageRatioBelowThreshold` alert annotation
  (`{{ printf "%.0f" ($value * 40) }}` — inline arithmetic is not supported
  by Prometheus templates). Replaced with a simpler description that uses
  only supported `printf` directives. No semantic change to the alert: it
  still fires when `item_bank_coverage_ratio < 0.8` for 10m.
- `docs/operations/alertmanager.md` — new authoritative deployment contract
  doc covering: why `api_url_file` is chosen, per-environment mount
  configuration (Docker Compose, Render, k8s), local + CI validation, and
  the procedure for adding new receivers.

### Validation

```text
$ amtool check-config alertmanager/alertmanager.yml
Checking 'alertmanager/alertmanager.yml'  SUCCESS
Found:
 - global config
 - route
 - 0 inhibit rules
 - 1 receivers
 - 0 templates
```

Full log: `audits/phase0/domain_d_amtool_check.txt`.

**AC met.** Exit code 0 against the exact artifact that will be deployed to
Alertmanager.

---

## T032 — Add observability config CI check

**Status:** Done.

Added new workflow `.github/workflows/observability_check.yml`. It:

1. Installs `promtool` (Prometheus v3.1.0) and `amtool` (Alertmanager
   v0.27.0) — pinned versions for reproducibility.
2. Runs `promtool check rules` against every rules file discovered under
   `prometheus/*.yml` and `alertmanager/rules/*.yml`. New rule files are
   picked up automatically without editing the workflow.
3. Runs `amtool check-config alertmanager/alertmanager.yml` against the
   exact deployed artifact.

Failure on either tool blocks merge per the AC. Workflow triggers on push
and PR for any changes under `alertmanager/`, `prometheus/`, or the
workflow itself.

Workflow validated:

```text
$ python -c "import yaml; yaml.safe_load(open('.github/workflows/observability_check.yml').read()); print('OK')"
OK
```

Local equivalent of the CI checks (the same commands the workflow runs):

```text
$ amtool check-config alertmanager/alertmanager.yml
SUCCESS  (1 receiver, 0 inhibit rules, 0 templates)

$ promtool check rules prometheus/alerts.yml
SUCCESS: 10 rules found

$ promtool check rules alertmanager/rules/item_bank_coverage.yml
SUCCESS: 3 rules found
```

Full logs: `audits/phase0/domain_d_amtool_check.txt`,
`audits/phase0/domain_d_promtool_check.txt`.

**AC met.** CI job runs both checks against deployable artifacts; failure
on either blocks merge.

---

## Outcome

- Alertmanager URL audit complete (T030) ✅
- Render strategy chosen and applied; `amtool check-config` is clean (T031) ✅
- Observability CI gate added; runs promtool + amtool on every relevant PR
  (T032) ✅
- One incidental fix made along the way: Prometheus template syntax bug in
  `item_bank_coverage.yml`. Pre-existing; would have blocked any future
  promtool gate. Documented above.
