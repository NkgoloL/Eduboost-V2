# Runbook: Database Outage

**Last Updated**: 2026-06-12  
**Severity**: Critical  
**SLA Impact**: Service unavailable

---

## Symptoms

- All API endpoints return HTTP 500 errors
- `/health` endpoint fails
- `psql` connection timeouts
- Monitoring alerts: "Database unavailable" or "High connection failures"

---

## Diagnosis

### Step 1: Verify Database Status

```bash
# Check Azure Database for PostgreSQL status
az postgres flexible-server show \
  --resource-group <rg-name> \
  --name <db-server-name>

# Check connection from app
DATABASE_URL="..." python -c "import asyncpg; ..."
```

### Step 2: Check Connection Pool

```bash
# Check Redis (if using connection pooling)
redis-cli -h <redis-host> ping

# Check if pool is exhausted
# (requires db admin access)
```

### Step 3: Review Logs

```bash
# Azure Database logs
az postgres flexible-server log list \
  --resource-group <rg-name> \
  --name <db-server-name> \
  --days 1

# Application logs
kubectl logs -l app=api -n eduboost | grep -i error
```

---

## Resolution

### Scenario A: Database Server Down

**Action**: Failover to standby (if configured)

```bash
# Promote standby (Azure managed)
az postgres flexible-server failover \
  --resource-group <rg-name> \
  --name <db-server-name>
```

**Estimated Recovery Time**: 2–5 minutes

### Scenario B: Connection Exhaustion

**Action**: Scale connection pool or restart app

```bash
# Scale app pods to force new connections
kubectl scale deployment eduboost-v2-api \
  --replicas=0 -n eduboost

kubectl scale deployment eduboost-v2-api \
  --replicas=3 -n eduboost
```

**Estimated Recovery Time**: 30–60 seconds

### Scenario C: Network Issue

**Action**: Check VNet peering and firewall rules

```bash
# Check VNet configuration
az network vnet show \
  --resource-group <rg-name> \
  --name <vnet-name>

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group <rg-name> \
  --server-name <db-server-name>
```

**Estimated Recovery Time**: 5–30 minutes

---

## Communication Template

### Internal Alert

```
🚨 INCIDENT: Database Outage

Status: Investigating
Impact: All API requests failing
Team: Platform Engineering
Contact: @platform on-call
```

### Status Page Update

```
🔴 Service Status: Database Unavailable

We are currently experiencing a database outage affecting all API services.
Our team is investigating and working to restore service.
Next update in 30 minutes.
```

---

## Post-Incident

1. **Document** in incident tracker
2. **Review** Azure cost for emergency failover
3. **Update** runbook with lessons learned
4. **Verify** backup restoration works

---

## Contacts

| Role | Contact |
|------|---------|
| On-call Engineer | Check PagerDuty schedule |
| DBA | dba@eduboost.co.za |
| Azure Support | portal.azure.com |

---

## References

- Azure PostgreSQL Flexible Server documentation
- Internal runbook: `docs/operations/database_backup_contract.md`
- Backup restoration: `scripts/db_restore.sh`