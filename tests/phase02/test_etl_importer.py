from __future__ import annotations

import sqlite3

from scripts.phase2_import_etl_corpus import load_documents


def test_importer_reads_only_approved_documents(tmp_path) -> None:
    path = tmp_path / "etl.db"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE documents (
            document_id TEXT PRIMARY KEY,
            source_id TEXT,
            title TEXT,
            document_type TEXT,
            subject TEXT,
            grade INTEGER,
            curriculum TEXT,
            language TEXT,
            version TEXT,
            license_status TEXT,
            source_url TEXT,
            checksum TEXT,
            processing_status TEXT,
            quality_score REAL,
            publisher TEXT
        );
        CREATE TABLE document_chunks (
            chunk_id TEXT PRIMARY KEY,
            document_id TEXT,
            chunk_type TEXT,
            chunk_index INTEGER,
            parent_chunk_id TEXT,
            heading TEXT,
            content TEXT,
            token_count INTEGER,
            page_start INTEGER,
            page_end INTEGER,
            section_path TEXT,
            curriculum_code TEXT
        );
        """
    )
    connection.executemany(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            ("approved", "s1", "Approved", "policy", "MATH", 4, "CAPS", "en", "1", "government_open", None, "h1", "approved", 0.9, "DBE"),
            ("draft", "s2", "Draft", "policy", "MATH", 4, "CAPS", "en", "1", "government_open", None, "h2", "draft", 0.9, "DBE"),
        ],
    )
    connection.executemany(
        "INSERT INTO document_chunks VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            ("a1", "approved", "text", 0, None, "Whole numbers", "Whole numbers and place value", 5, 1, 1, "One", "4.M.1.1"),
            ("d1", "draft", "text", 0, None, "Draft", "Draft text", 2, 1, 1, "One", "4.M.1.1"),
        ],
    )
    connection.commit()
    connection.close()

    payload = load_documents(path)
    assert len(payload) == 1
    document, chunks = payload[0]
    assert document["document_id"] == "approved"
    assert [chunk["chunk_id"] for chunk in chunks] == ["a1"]
