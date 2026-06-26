Changelog
=========

v2.0.0 (May 2026)
------------------

* Complete V1 → V2 architectural migration to modular monolith.
* IRT 2PL adaptive engine implemented in ``app.modules.diagnostics``.
* LLM gateway with Groq primary / Anthropic fallback and semantic cache.
* POPIA consent gate enforced as FastAPI ``Depends``.
* Append-only PostgreSQL audit trail replacing RabbitMQ.
* Alembic-managed schema with 8 core tables + RLHF pipeline tables.
* Azure Container Apps Bicep IaC (fully parameterised).
* Grafana Cloud observability stack provisioned.

.. todo::

   Add v2.1.0 entry once AES-GCM migration (SEC-002) ships.
