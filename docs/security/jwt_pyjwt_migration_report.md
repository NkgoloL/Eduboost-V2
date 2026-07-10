# JWT PyJWT Migration Report

PRD-10.0-10.4 removes the runtime dependency on `python-jose` and places
JWT handling behind `app.core.jwt_compat`, backed by PyJWT.

Regression controls cover keyring round-trip behaviour, `kid` based previous
key decoding, tampered-token rejection, and requirements checks confirming
`python-jose` is no longer declared for runtime or dev installs.

This migration does not authorise live learner traffic.
