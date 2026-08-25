"""
Unit tests for app/api_v2_routers/0005_irt_seed.py migration functions and item list structure.
"""
from __future__ import annotations

import importlib


def test_irt_seed_items_structure():
    # Import migration module via importlib
    mod = importlib.import_module("app.api_v2_routers.0005_irt_seed")
    assert hasattr(mod, "_ITEMS")
    assert len(mod._ITEMS) > 50

    for item in mod._ITEMS[:10]:
        # (grade, subject, topic, question, options, correct, a, b, lang)
        assert isinstance(item[0], int)  # grade
        assert isinstance(item[1], str)  # subject
        assert isinstance(item[2], str)  # topic
        assert isinstance(item[3], str)  # question
        assert isinstance(item[4], dict)  # options
        assert isinstance(item[5], str)  # correct
        assert isinstance(item[6], (float, int))  # a_param
        assert isinstance(item[7], (float, int))  # b_param


def test_irt_seed_helper_make():
    mod = importlib.import_module("app.api_v2_routers.0005_irt_seed")
    res = mod._make(1, "Math", "Topic", "Q?", {"A": "1"}, "A", 1.0, 0.0, "en")
    assert res == (1, "Math", "Topic", "Q?", {"A": "1"}, "A", 1.0, 0.0, "en")
