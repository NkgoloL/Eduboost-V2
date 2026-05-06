"""CAPS-aligned lesson generation module.

Orchestrates the end-to-end lesson lifecycle: consent validation, learner
context construction, AI lesson generation via the
:class:`~app.modules.lessons.llm_gateway.LLMGateway`, persistence, and
audit logging.

The module enforces that every lesson request passes through the POPIA
consent gate before any learner data is accessed or sent to an external
LLM provider.

Submodules:

* :mod:`~app.modules.lessons.service` — high-level lesson orchestration.
* :mod:`~app.modules.lessons.llm_gateway` — provider-agnostic LLM
  abstraction with Groq primary / Anthropic fallback routing.
"""
