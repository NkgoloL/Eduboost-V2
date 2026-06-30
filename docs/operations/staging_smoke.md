# Staging Smoke Checks

The staging smoke script validates the public operational endpoints after deploy:

```bash
python scripts/staging_smoke.py --base-url https://staging.example.com --json-output reports/staging_smoke.json
```

Checked endpoints:

| Endpoint | Expected |
|---|---|
| `/health` | `200` and status payload |
| `/ready` | `200` when critical dependencies are available |
| `/metrics` | `200` and Prometheus metrics |
| `/docs` | Swagger UI rendered |
| `/openapi.json` | OpenAPI schema available |

A failed staging smoke blocks production promotion.
