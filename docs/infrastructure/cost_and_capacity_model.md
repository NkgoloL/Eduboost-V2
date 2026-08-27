# EduBoost V2: Cost, Token & Capacity Scaling Model

**Control ID**: `TSR-13.7`  
**Release Gate**: `RG-6`  
**Status**: Authoritative  
**Domain**: Infrastructure / FinOps / DevOps  

---

## 1. Capacity Baselines & Resource Limits

| Resource Component | Allocation per Node | Max Concurrent Learners | Scaling Tripwire |
| :--- | :--- | :--- | :--- |
| **FastAPI Backend (Worker)** | 2 vCPU / 4 GB RAM | 250 active connections | $> 70\%$ CPU utilization over 5 min |
| **PostgreSQL Database** | 4 vCPU / 16 GB RAM (SSD) | 1,000 active connections | $> 75\%$ IOPS capacity or connection pool $> 80\%$ |
| **Redis Cache / Broker** | 2 vCPU / 4 GB RAM | 5,000 ops/sec | $> 80\%$ memory allocation |

---

## 2. LLM Token Cost Forecasting & Budget Caps

- **Average Practice Session**: ~1,500 input tokens + ~400 output tokens.
- **Cost per Learner Session**: ~$0.003 USD (utilizing optimized prompt templates and caching).
- **Hard Daily Budget Ceiling**: $50.00 USD per 1,000 active learners.
- **Fail-Closed Budget Interceptor**: `AIBudgetGuard` halts LLM requests when 90% of daily quota is reached, switching to pre-generated static hints.
