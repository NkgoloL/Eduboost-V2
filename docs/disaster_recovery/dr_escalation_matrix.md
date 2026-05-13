# Disaster Recovery Escalation Matrix

## Roles

| Role | Owner |
| --- | --- |
| Incident Commander | release-owner |
| Technical Lead | engineering |
| Privacy Owner | privacy |
| Communications Owner | support |
| Database Owner | database-owner |
| Platform Owner | platform-owner |

## Escalation Rules

- critical database recovery escalates to engineering and release owner
- audit log recovery escalates to privacy owner
- communications impact escalates to support owner
- learner data risk escalates to privacy owner
- production restoration requires release-owner approval

## Boundary

This matrix records escalation ownership. It does not page owners automatically.
