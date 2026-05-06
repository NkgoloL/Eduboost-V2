"""Guardian authentication and account lifecycle module.

Provides :class:`~app.modules.auth.service.AuthService` for guardian
registration, login, email verification, and profile retrieval.

All personally identifiable information (PII) is encrypted at rest via
:func:`~app.core.security.encrypt_pii` and hashed for lookup via
:func:`~app.core.security.hash_email`.  Every authentication event is
recorded in the :mod:`app.core.audit` trail for POPIA compliance.
"""
