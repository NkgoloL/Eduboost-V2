# Notification Audit and Observability Contract

## Purpose

This contract defines audit and observability requirements for notification lifecycle events.

## Required Audit Fields

- event ID
- recipient ID
- audience
- purpose
- channel
- delivery status
- request ID
- idempotency key
- provider message ID where available
- occurred at UTC
- redacted metadata only

## Required Metrics

- queued count by channel
- sent count by channel
- delivered count by channel
- failed count by channel
- suppressed count by channel
- dead-letter count by channel
- bounce count
- complaint count
- unsubscribe count
- retry count

## Required Alerts

- provider outage alert
- delivery failure spike alert
- dead-letter spike alert
- bounce spike alert
- complaint spike alert
- notification backlog alert

## Boundary

This contract records notification audit and observability readiness. It does not create dashboards, send alerts, or contact users.
