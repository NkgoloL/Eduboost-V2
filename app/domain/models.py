"""Compatibility export for V2 ORM models.

The canonical SQLAlchemy models live in ``app.models``.  Some V2 repository
code still imports ``app.domain.models`` from an earlier consolidation pass, so
this module preserves that boundary without duplicating model definitions.
"""
from app.models import *  # noqa: F401,F403
