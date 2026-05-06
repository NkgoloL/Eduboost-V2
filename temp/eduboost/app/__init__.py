"""EduBoost SA — AI-powered adaptive learning platform.

This package implements the V2 modular monolith backend for EduBoost SA,
an adaptive learning platform targeting South African learners from Grade R
through Grade 7. The platform is POPIA-compliant and CAPS-aligned.

Modules:
    core: Shared kernel (config, database, security, audit, metrics).
    modules: Domain bounded contexts (diagnostics, lessons, consent, etc.).
    api_v2_routers: Thin HTTP routing layer.
    repositories: Generic async data-access layer.
    models: SQLAlchemy ORM models.

Example:
    Run the development server::

        uvicorn app.api_v2:app --reload --port 8000
"""
