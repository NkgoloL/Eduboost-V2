#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NGINX_CONF = ROOT / "nginx/nginx.conf"


def _read() -> str:
    if not NGINX_CONF.exists():
        raise FileNotFoundError(NGINX_CONF)
    return NGINX_CONF.read_text(encoding="utf-8")


def _detect_domain(source: str) -> str:
    explicit = os.getenv("SSL_CERT_DOMAIN", "").strip()
    if explicit:
        return explicit

    matches = re.findall(r"(?m)^\s*server_name\s+([^;]+);", source)
    for match in matches:
        for token in match.split():
            token = token.strip()
            if not token or token == "_" or "$" in token or token.startswith("localhost"):
                continue
            return token

    return "localhost"


def patch_nginx_cert_paths(source: str) -> tuple[str, str]:
    domain = _detect_domain(source)
    cert = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
    key = f"/etc/letsencrypt/live/{domain}/privkey.pem"

    changed = source

    if re.search(r"(?m)^\s*ssl_certificate\s+[^;]+;", changed):
        changed = re.sub(
            r"(?m)^(\s*)ssl_certificate\s+[^;]+;",
            rf"\1ssl_certificate {cert};",
            changed,
            count=0,
        )
    else:
        changed = changed.replace(
            "listen 443 ssl;",
            f"listen 443 ssl;\n    ssl_certificate {cert};",
            1,
        )

    if re.search(r"(?m)^\s*ssl_certificate_key\s+[^;]+;", changed):
        changed = re.sub(
            r"(?m)^(\s*)ssl_certificate_key\s+[^;]+;",
            rf"\1ssl_certificate_key {key};",
            changed,
            count=0,
        )
    else:
        changed = changed.replace(
            f"ssl_certificate {cert};",
            f"ssl_certificate {cert};\n    ssl_certificate_key {key};",
            1,
        )

    return changed, domain


def main() -> int:
    source = _read()
    patched, domain = patch_nginx_cert_paths(source)
    if patched != source:
        NGINX_CONF.write_text(patched, encoding="utf-8")
        print(f"Patched nginx certificate paths to /etc/letsencrypt/live/{domain}/")
    else:
        print(f"nginx certificate paths already aligned to /etc/letsencrypt/live/{domain}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
