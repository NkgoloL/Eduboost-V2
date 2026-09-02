import importlib
from unittest.mock import MagicMock, patch
import pytest


def test_0005_irt_seed_upgrade_and_downgrade():
    irt_seed = importlib.import_module("scripts.migrations.0005_irt_seed")


    assert len(irt_seed._ITEMS) > 10
    assert irt_seed.revision == "0005_irt_seed"

    with patch.object(irt_seed, "op") as mock_op:
        irt_seed.upgrade()
        assert mock_op.bulk_insert.called

        irt_seed.downgrade()
        assert mock_op.execute.called
