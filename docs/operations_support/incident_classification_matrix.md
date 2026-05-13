# Incident Classification Matrix

## Required Severity Rules

| Severity | Customer Impact | Response Time | Update Interval | Release Blocking |
| --- | --- | --- | --- | --- |
| sev1 | critical | 15 minutes | 30 minutes | yes |
| sev2 | major | 30 minutes | 60 minutes | yes |
| sev3 | moderate | 120 minutes | 240 minutes | no |
| sev4 | minor | 480 minutes | 1440 minutes | no |

## Required Controls

- sev1 requires incident commander
- sev2 requires incident commander
- sev1 requires status update
- major or critical customer impact must block release
- privacy-related incidents require privacy review
- incident evidence must be retained

## Boundary

This matrix records classification readiness. It does not declare or resolve incidents.
