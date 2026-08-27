# Risk-Based Coverage Thresholds

## 1. Global vs Domain-Specific Thresholds
While overall codebase line coverage maintains a baseline threshold of **70%**, high-risk domains require elevated coverage standards:

| Domain / Module Area | Minimum Line Coverage | Minimum Branch Coverage | Rationale |
|---|---|---|---|
| **Authorization & Permissions** (`app/services/auth_*.py`, `app/security/`) | **90%** | **85%** | Prevents unauthorized tenant or learner data access |
| **POPIA & Consent Privacy** (`app/services/consent_*.py`, `app/api/v2/consent.py`) | **90%** | **85%** | Enforces South African statutory child privacy boundaries |
| **Payment Inactive Safeguards** (`app/services/billing_*.py`) | **95%** | **90%** | Guarantees fail-closed disabled billing state |
| **Learner Mastery & Progression** (`app/services/mastery_*.py`, `app/services/study_plan_*.py`) | **85%** | **80%** | Protects pedagogical state consistency and diagnostic integrity |
| **General Application Services** (`app/services/`, `app/api/`) | **70%** | **65%** | Standard application baseline |

## 2. Enforcement
Thresholds are audited continuously during release candidate gate compilation.
