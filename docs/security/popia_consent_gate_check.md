# POPIA Consent Gate Check

## Purpose

`popia-consent-gate-check` prevents new learner-related functions from being
added without either:

1. an explicit consent-gate marker, or
2. a deliberate baseline allowlist entry.

## Baseline Allowlist

```text
docs/security/popia_consent_gate_allowlist.txt
```

The allowlist captures the current inventory candidates. Remove entries from
the allowlist as explicit consent gates are wired.

## Commands

```bash
python3 scripts/generate_consent_gate_inventory.py
python3 scripts/check_consent_gate_inventory.py
make popia-consent-gate-check
```

To refresh the baseline deliberately:

```bash
python3 scripts/check_consent_gate_inventory.py --write-baseline
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_gate_inventory_check.py -q --no-cov
make popia-consent-gate-check
```


## Baseline Refresh After Gate Wiring

When a learner-data route receives an explicit consent gate, its old allowlist
entry becomes stale and must be removed by refreshing the baseline:

```bash
python3 scripts/check_consent_gate_inventory.py --write-baseline
```
