# Alertmanager Deployment Contract

**Owner:** Platform / Operations
**Last updated:** 2026-05-27 (Phase 0 T030–T032)
**Authoritative source:** `alertmanager/alertmanager.yml`

This document defines how `alertmanager/alertmanager.yml` is deployed and how
secrets are supplied. The checked-in YAML is the *exact* artifact loaded by
Alertmanager — there is no template-rendering step.

---

## Secret loading via `*_url_file`

The Slack webhook URL is loaded from a file at runtime using Alertmanager's
native `api_url_file` directive:

```yaml
receivers:
  - name: slack-default
    slack_configs:
      - api_url_file: /etc/alertmanager/secrets/slack_webhook_url
```

The orchestrator (Docker Compose / Render / Kubernetes) is responsible for
mounting a file containing the webhook URL at exactly that path. The file
contents are a single line: the webhook URL with no trailing newline noise.

### Why `api_url_file` and not `${VAR}`

Alertmanager itself does **not** expand `${ENV_VAR}` syntax in its YAML. A
config with `api_url: ${SOMETHING}` will fail `amtool check-config` and will
fail at Alertmanager startup. `api_url_file` is the supported, native
mechanism for keeping secrets out of source control.

---

## Per-environment deployment

### Docker Compose (development / staging)

Add a bind-mount or secret to the Alertmanager service:

```yaml
services:
  alertmanager:
    image: prom/alertmanager:v0.27.0
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - /run/secrets/alertmanager_slack_webhook:/etc/alertmanager/secrets/slack_webhook_url:ro
```

The file at `/run/secrets/alertmanager_slack_webhook` on the host (created
out-of-band, never committed) contains the webhook URL.

### Render

Alertmanager is not currently deployed on Render. If it is added in the
future, attach the webhook as a Render *secret file* with mount path
`/etc/alertmanager/secrets/slack_webhook_url`.

### Kubernetes (future)

Provision a Kubernetes Secret with key `slack_webhook_url` and mount it on
the Alertmanager pod at `/etc/alertmanager/secrets/`:

```yaml
volumes:
  - name: alertmanager-secrets
    secret:
      secretName: alertmanager-webhooks
volumeMounts:
  - name: alertmanager-secrets
    mountPath: /etc/alertmanager/secrets
    readOnly: true
```

---

## Validation

`alertmanager/alertmanager.yml` is validated on every push and PR by
`.github/workflows/observability_check.yml`:

```bash
amtool check-config alertmanager/alertmanager.yml
```

Rule files under `alertmanager/rules/*.yml` and `prometheus/*.yml` are
validated by the same workflow:

```bash
promtool check rules <file>
```

Failure on either tool blocks merge.

To validate locally before pushing:

```bash
amtool check-config alertmanager/alertmanager.yml
for f in prometheus/*.yml alertmanager/rules/*.yml; do
  promtool check rules "$f"
done
```

Expected output (clean repository):

```text
Checking 'alertmanager/alertmanager.yml'  SUCCESS
Found:
 - global config
 - route
 - 0 inhibit rules
 - 1 receivers
 - 0 templates

Checking prometheus/alerts.yml
  SUCCESS: 10 rules found

Checking alertmanager/rules/item_bank_coverage.yml
  SUCCESS: 3 rules found
```

---

## Adding a new receiver

1. Add the receiver block under `receivers:` in `alertmanager/alertmanager.yml`.
2. If the receiver has a URL secret, use `*_url_file` (never inline `${VAR}`)
   and update this document with the canonical mount path.
3. Update the routing table under `route:` to point relevant alerts at the
   new receiver.
4. Run the local validation block above. If anything fails, fix before
   pushing — the CI gate will reject it.
5. Update every orchestrator config (Docker Compose, Render, k8s) so the
   new secret file is mounted in every environment.

A PR that adds a receiver but does not update orchestrator configs in the
same change is invalid and must be rejected.
