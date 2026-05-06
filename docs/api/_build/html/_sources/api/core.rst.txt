Core — Shared Kernel
====================

The ``app.core`` package provides the shared kernel consumed by all domain
modules.  It includes configuration, database connectivity, security
primitives, the audit trail, Prometheus metrics, and middleware.

.. contents:: Modules
   :local:
   :depth: 1

Configuration
-------------

.. automodule:: app.core.config
   :members:
   :exclude-members: validate_jwt_secret, validate_encryption_key
   :show-inheritance:

Security
--------

.. automodule:: app.core.security
   :members:
   :undoc-members:
   :show-inheritance:

Audit Trail
-----------

.. automodule:: app.core.audit
   :members:
   :undoc-members:
   :show-inheritance:
