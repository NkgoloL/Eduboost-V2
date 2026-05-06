"""IRT-based adaptive diagnostic engine module.

Implements the Gap-Probe Cascade using a 2-Parameter Logistic (2PL) Item
Response Theory model calibrated against the South African CAPS
curriculum for grades R–7.

Submodules:

* :mod:`~app.modules.diagnostics.irt_engine` — theta estimation,
  Fisher-information item selection, and knowledge-gap identification.
* :mod:`~app.modules.diagnostics.service` — consent-gated diagnostic
  session orchestration with audit logging.
"""
