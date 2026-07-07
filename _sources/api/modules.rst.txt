Domain Modules
==============

Domain logic is organised into bounded contexts under ``app.modules``.
Each sub-package owns its own service layer, schemas, and (where needed)
background workers.

.. contents:: Bounded Contexts
   :local:
   :depth: 1

----

Diagnostics — IRT Engine
------------------------

Implements the IRT 2-Parameter Logistic model for adaptive ability
estimation and item selection.

.. automodule:: app.modules.diagnostics.irt_engine
   :members:
   :undoc-members:
   :show-inheritance:

----

Lessons — LLM Gateway
----------------------

Provider-agnostic gateway for AI lesson generation with semantic caching
and automatic Groq → Anthropic fallback.

.. automodule:: app.modules.lessons.llm_gateway
   :members:
   :undoc-members:
   :show-inheritance:

----

Consent — POPIA Service
------------------------

Full lifecycle management of parental consent records in compliance with
the Protection of Personal Information Act.

.. automodule:: app.modules.consent.service
   :members:
   :undoc-members:
   :show-inheritance:

----

Learners
--------

.. automodule:: app.modules.learners
   :members:
   :undoc-members:
   :show-inheritance:

----

Study Plans
-----------

.. automodule:: app.modules.study_plans
   :members:
   :undoc-members:
   :show-inheritance:

----

Gamification
------------

.. automodule:: app.modules.gamification
   :members:
   :undoc-members:
   :show-inheritance:

----

Parent Portal
-------------

.. automodule:: app.modules.parent_portal
   :members:
   :undoc-members:
   :show-inheritance:

----

RLHF Pipeline
-------------

.. automodule:: app.modules.rlhf
   :members:
   :undoc-members:
   :show-inheritance:
