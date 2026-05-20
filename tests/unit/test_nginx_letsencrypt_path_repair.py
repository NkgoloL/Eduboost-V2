from __future__ import annotations

from scripts.repair_nginx_letsencrypt_paths import patch_nginx_cert_paths


def test_patch_nginx_cert_paths_replaces_ssl_cert_locations():
    source = """
server {
    listen 443 ssl;
    server_name example.org;
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;
}
"""

    patched, domain = patch_nginx_cert_paths(source)

    assert domain == "example.org"
    assert "ssl_certificate /etc/letsencrypt/live/example.org/fullchain.pem;" in patched
    assert "ssl_certificate_key /etc/letsencrypt/live/example.org/privkey.pem;" in patched
    assert "/etc/ssl/private" not in patched


def test_patch_nginx_cert_paths_inserts_missing_directives():
    source = """
server {
    listen 443 ssl;
    server_name eduboost.example;
}
"""

    patched, domain = patch_nginx_cert_paths(source)

    assert domain == "eduboost.example"
    assert "/etc/letsencrypt/live/eduboost.example/fullchain.pem" in patched
    assert "/etc/letsencrypt/live/eduboost.example/privkey.pem" in patched
