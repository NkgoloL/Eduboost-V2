from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.api_v2 import app
from app.modules.diagnostics.item_bank_service import ItemBankService


def test_phase4_routes_are_registered_under_both_prefixes():
    paths = {route.path for route in app.routes}
    expected = {
        "/api/v2/admin/irt-quality/runs",
        "/v2/admin/irt-quality/runs",
        "/api/v2/admin/irt-quality/items/{item_id}",
        "/api/v2/admin/irt-quality/items/{item_id}/override",
    }
    assert expected <= paths


class _Repo:
    def __init__(self, items): self.items = items
    async def get_unexposed_items(self, **kwargs): return self.items


def _item(state):
    return SimpleNamespace(
        item_id=uuid4(), irt_quality_state=state,
        discrimination_a=1.0, difficulty_b=0.0, guessing_c=0.25,
    )


async def test_item_selection_excludes_quarantined_retired_and_review_items():
    healthy = _item("healthy")
    service = ItemBankService(_Repo([
        _item("quarantined"), _item("retired"), _item("review_required"), healthy
    ]))
    selected = await service.select_item_for_learner("4.M.1", uuid4())
    assert selected.item_id == healthy.item_id
