#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNIP = """    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.10'
          memory: 128M
"""

def patch_compose(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r"\s+--reload\b", "", text)
    text = text.replace("${GRAFANA_ADMIN_PASSWORD:-admin}", "${GRAFANA_ADMIN_PASSWORD:?GRAFANA_ADMIN_PASSWORD must be set}")
    for svc in ["api", "frontend", "postgres", "redis", "nginx", "grafana", "prometheus", "alertmanager", "docs", "certbot"]:
        pattern = re.compile(rf"(^  {svc}:\n)(.*?)(?=^  [A-Za-z0-9_.-]+:\n|\Z)", re.M | re.S)
        match = pattern.search(text)
        if match and "deploy:" not in match.group(2):
            text = text[:match.start()] + match.group(1) + SNIP + match.group(2) + text[match.end():]
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def main() -> int:
    changed = [str(path.name) for path in [ROOT / "docker-compose.yml", ROOT / "docker-compose.prod.yml"] if patch_compose(path)]

    env = ROOT / ".env.example"
    env_text = env.read_text(encoding="utf-8") if env.exists() else ""
    if "GRAFANA_ADMIN_PASSWORD" not in env_text:
        env.write_text(env_text.rstrip() + "\nGRAFANA_ADMIN_PASSWORD=\n", encoding="utf-8")

    override = ROOT / "docker-compose.override.example.yml"
    if not override.exists():
        override.write_text(
            "# Development-only override example. Copy to docker-compose.override.yml.\n"
            "services:\n"
            "  api:\n"
            "    command: uvicorn app.api_v2:app --host 0.0.0.0 --port 8000 --reload\n"
            "    environment:\n"
            "      APP_ENV: development\n"
            "  frontend:\n"
            "    command: npm run dev\n",
            encoding="utf-8",
        )

    gitignore = ROOT / ".gitignore"
    gitignore_text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if "docker-compose.override.yml" not in gitignore_text:
        gitignore.write_text(gitignore_text.rstrip() + "\ndocker-compose.override.yml\n", encoding="utf-8")

    nginx = ROOT / "nginx/nginx.conf"
    if not nginx.exists():
        nginx.parent.mkdir(parents=True, exist_ok=True)
        nginx.write_text(
            "events { worker_connections 1024; }\n"
            "http {\n"
            "  upstream api { server api:8000; }\n"
            "  upstream frontend { server frontend:3050; }\n"
            "  server {\n"
            "    listen 80;\n"
            "    server_name _;\n"
            "    location /health { return 200 'ok'; add_header Content-Type text/plain; }\n"
            "    location /api/ { proxy_pass http://api; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; }\n"
            "    location / { proxy_pass http://frontend; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; }\n"
            "  }\n"
            "}\n",
            encoding="utf-8",
        )

    print("Docker hardening patch complete.", changed)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
