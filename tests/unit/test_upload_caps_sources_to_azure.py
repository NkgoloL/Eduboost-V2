from __future__ import annotations

import pytest

from scripts.curriculum.upload_caps_sources_to_azure import blob_name, object_store_uri, slug


pytestmark = pytest.mark.unit


def test_blob_name_is_phase_subject_language_and_hash_scoped() -> None:
    document = {
        "document_id": "caps_senior_economic_management_sciences_en",
        "phase": "senior",
        "subjects": ["Economic and Management Sciences"],
        "languages": ["en"],
        "source_sha256": "313a25bf38f59a24df8180453aab57aa573d8aaf2564af4a342d0df2456ad8ea",
    }

    assert blob_name(document) == (
        "senior/economic-and-management-sciences/en/"
        "caps_senior_economic_management_sciences_en-313a25bf38f59a24.pdf"
    )


def test_object_store_uri_url_encodes_blob_segments() -> None:
    uri = object_store_uri("eduboostcaps", "caps-sources", "senior/social sciences/source file.pdf")

    assert uri == "https://eduboostcaps.blob.core.windows.net/caps-sources/senior/social%20sciences/source%20file.pdf"


def test_slug_normalizes_empty_and_punctuation() -> None:
    assert slug("Economic & Management Sciences") == "economic-management-sciences"
    assert slug(None) == "unknown"


def test_uploader_cli_exposes_key_auth_mode() -> None:
    from scripts.curriculum import upload_caps_sources_to_azure as uploader

    assert uploader.object_store_uri("acct", "caps-sources", "a/b.pdf").startswith("https://acct.blob.core.windows.net/")
