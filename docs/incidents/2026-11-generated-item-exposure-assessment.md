# Generated Grade 4 item exposure assessment

**Status: open / unverified**  
**Interim incident coordinator: project owner**  
**Population: 120-row Grade 4 Mathematics launch bank**

The launch bank has been quarantined. Its previous approval labels were created by the generation pipeline and do not establish independent educator approval. The item review identified 14 defective fixed item definitions (42 repeated rows); four definitions contain wrong answer keys. This exposure assessment has not yet established whether any real learner received incorrect feedback.

The item exposure table records an event when a response is submitted, not on every item serve. Its counts are a lower bound. A zero count is not evidence of zero delivery. Run the aggregate exposure query separately against each authorized environment, then reconcile the results with API/session logs and identify whether traffic was test-only or involved non-test learners. Do not copy learner IDs or answers into this report.

If non-test learner exposure to wrong feedback is confirmed, treat it as an incident: preserve evidence, determine affected guardians/educators, and coordinate notification decisions with POPIA counsel. No deployment database, service telemetry, or guardian contact access was used for this record, so exposure remains unknown.

## Evidence to collect

| Target | Query result | Serving-log review | Non-test learner exposure | Owner/reviewer |
| --- | --- | --- | --- | --- |
| Local/dev | Unverified | Unverified | Unknown | Project owner |
| Compose | Unverified | Unverified | Unknown | Project owner |
| Render | Unverified | Unverified | Unknown | Project owner |
| Azure Container Apps | Unverified | Unverified | Unknown | Project owner |

Use python scripts/audit_quarantined_item_exposure.py --environment target with that target's authorized database configuration. Complete the log/session review independently; the script deliberately reports only a database lower bound.
