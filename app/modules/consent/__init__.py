"""POPIA parental consent management module.

Provides the :class:`~app.modules.consent.service.ConsentService` for
granting, revoking, renewing, and querying parental consent records.
All consent state changes are audit-logged for South African POPIA
compliance reporting.

Key responsibilities:

* Enforce the consent gate as a FastAPI ``Depends`` function so no route
  can bypass it.
* Record every lifecycle event (grant, revoke, renew, erasure) in the
  :mod:`app.core.audit` trail.
* Expose expiring-consent queries for the ARQ renewal-reminder
  background job.
"""
