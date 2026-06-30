# Next Execution Queue After TX-001B / code_1431_1470

## Recommended next batch

`TX-002 / code_1471_1510` — wire POPIA lifecycle routes/dependencies through the transactional lifecycle boundary or add production-service rollback proof.

## Scope candidates

1. Find canonical POPIA lifecycle dependency construction.
2. Wrap lifecycle consent service + audit writer in `TransactionalPOPIAConsentLifecycleService`.
3. Add HTTP/runtime tests proving audit failure does not persist consent transition.
4. Keep external legal review and full consent-blocking sweep outside this narrow transaction proof.
