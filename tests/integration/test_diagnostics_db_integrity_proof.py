from __future__ import annotations

import sqlite3

import pytest

from app.services.diagnostic_data_integrity import DiagnosticIntegrityError
from app.services.diagnostic_session_integrity import validate_session_served_item_binding


def _served_rows_for_session(session_id: str):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE diagnostic_sessions (id TEXT PRIMARY KEY, caps_topic TEXT, caps_code TEXT)")
    con.execute("CREATE TABLE diagnostic_served_items (session_id TEXT, item_id TEXT, caps_topic TEXT, caps_code TEXT)")
    con.execute("INSERT INTO diagnostic_sessions VALUES ('s1', 'fractions', 'CAPS-MATH-4-FRAC')")
    con.execute("INSERT INTO diagnostic_sessions VALUES ('s2', 'geometry', 'CAPS-MATH-4-GEO')")
    con.execute("INSERT INTO diagnostic_served_items VALUES ('s1', 'item-a', 'fractions', 'CAPS-MATH-4-FRAC')")
    con.execute("INSERT INTO diagnostic_served_items VALUES ('s2', 'item-b', 'geometry', 'CAPS-MATH-4-GEO')")
    rows = con.execute(
        "SELECT session_id, item_id, caps_topic, caps_code FROM diagnostic_served_items WHERE session_id = ?",
        (session_id,),
    ).fetchall()
    return [
        {"session_id": row[0], "item_id": row[1], "caps_topic": row[2], "caps_code": row[3]}
        for row in rows
    ]


def test_diagnostics_db_proof_accepts_served_item_for_session_caps_binding():
    served = _served_rows_for_session("s1")
    validate_session_served_item_binding(
        {"responses": [{"item_id": "item-a", "answer": "1/2"}]},
        served_items=served,
        session_id="s1",
        caps_topic="fractions",
        caps_code="CAPS-MATH-4-FRAC",
    )


def test_diagnostics_db_proof_rejects_unserved_item_for_session():
    served = _served_rows_for_session("s1")
    with pytest.raises(DiagnosticIntegrityError):
        validate_session_served_item_binding(
            {"responses": [{"item_id": "item-b", "answer": "triangle"}]},
            served_items=served,
            session_id="s1",
            caps_topic="fractions",
            caps_code="CAPS-MATH-4-FRAC",
        )


def test_diagnostics_db_proof_rejects_wrong_caps_binding():
    served = _served_rows_for_session("s1")
    with pytest.raises(DiagnosticIntegrityError):
        validate_session_served_item_binding(
            {"responses": [{"item_id": "item-a", "answer": "1/2"}]},
            served_items=served,
            session_id="s1",
            caps_topic="geometry",
            caps_code="CAPS-MATH-4-GEO",
        )
