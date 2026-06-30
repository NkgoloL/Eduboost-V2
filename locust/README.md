# EduBoost V2 Load Testing with Locust

## Overview

This directory contains Locust load test scenarios for the EduBoost V2 API. The tests simulate realistic user journeys including authentication, diagnostics, lesson generation, and parent portal access.

## Quick Start

### Prerequisites

- Python 3.12+
- Locust installed: `pip install locust`
- Backend running (Docker Compose or local)

### Running Tests

**Against local development server:**

```bash
# Start the backend
docker-compose up -d

# Run Locust (web UI on http://localhost:8089)
locust -f locust/locustfile.py --host=http://localhost:8000

# Or run headless with specified users
locust -f locust/locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 60s --headless
```

**Against staging (requires permission):**

```bash
locust -f locust/locustfile.py --host=https://api.staging.eduboost.co.za \
    --users 200 --spawn-rate 20 --run-time 5m --headless
```

## User Scenarios

| Scenario | Weight | Description |
|----------|--------|-------------|
| `LearnerUser` | 60% | Full learner journey: login → diagnostics → study plan → lesson |
| `ParentUser` | 20% | Parent portal: login → view learners → check consent |
| `AnonymousUser` | 20% | Public endpoints: health, docs, OpenAPI |

## Target Metrics

| Metric | Target | Threshold |
|--------|--------|-----------|
| Concurrent Users | 500 | - |
| Requests/sec | 100 | - |
| p50 Latency | <500ms | Alert if >1s |
| p95 Latency | <2s | Alert if >5s |
| Error Rate | <1% | Alert if >5% |

## Distributed Load Testing

For higher load, run in distributed mode:

```bash
# Terminal 1: Start master
locust -f locust/locustfile.py --master --port 8089

# Terminal 2-4: Start workers
locust -f locust/locustfile.py --worker --master-host=localhost
```

## CI Integration

To run as part of CI (non-blocking):

```bash
# Run with report output
locust -f locust/locustfile.py --host=$API_URL \
    --headless --users 50 --spawn-rate 10 --run-time 2m \
    --html=locust-report.html --csv=locust-results
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check test credentials in `locustfile.py` |
| Rate limited (429) | Reduce spawn rate, increase wait times |
| Connection refused | Ensure backend is running on correct port |
| High latency | Check database and Redis connection pools |

## Files

- `locustfile.py` — Test scenarios and user definitions
- `README.md` — This file