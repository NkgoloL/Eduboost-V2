#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# EduBoost demo/MVP/alpha deployment helper
#
# Targets:
#   Frontend: Cloudflare Pages
#   Backend:  Render Free Web Service
#   DB:       Supabase Free Postgres
#   Cache:    Upstash Redis Free
#
# Assumed EduBoost structure:
#   app/frontend        -> Next.js frontend
#   app/api_v2.py       -> FastAPI app, exposed as app.api_v2:app
#
# This script:
#   1. Generates render.yaml for Render.
#   2. Generates frontend env file for Cloudflare Pages build.
#   3. Builds and deploys static frontend to Cloudflare Pages.
#   4. Prints exact Render/Supabase/Upstash variables to set.
#
# Important:
#   - Cloudflare Pages here assumes static frontend export.
#   - Full SSR Next.js should use Cloudflare Workers/OpenNext instead.
# ============================================================

APP_NAME="${APP_NAME:-eduboost}"
ENVIRONMENT="${ENVIRONMENT:-development}"

FRONTEND_DIR="${FRONTEND_DIR:-app/frontend}"
FRONTEND_PROJECT_NAME="${FRONTEND_PROJECT_NAME:-eduboost-demo}"

BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME:-eduboost-api}"
BACKEND_MODULE="${BACKEND_MODULE:-app.api_v2:app}"
BACKEND_HEALTH_PATH="${BACKEND_HEALTH_PATH:-/health}"
BACKEND_REGION="${BACKEND_REGION:-oregon}"
PYTHON_VERSION="${PYTHON_VERSION:-3.11.9}"

# Render's predictable demo URL once the service is created.
API_BASE_URL="${API_BASE_URL:-https://${BACKEND_SERVICE_NAME}.onrender.com}"

# Cloudflare Pages public URL after deploy.
FRONTEND_PUBLIC_URL="https://${FRONTEND_PROJECT_NAME}.pages.dev"

# CORS origins passed to Render backend.
CORS_ORIGINS="${CORS_ORIGINS:-${FRONTEND_PUBLIC_URL},http://localhost:3000,http://127.0.0.1:3000}"

log() {
  printf "\n\033[1;36m[eduboost-deploy]\033[0m %s\n" "$1"
}

warn() {
  printf "\n\033[1;33m[warning]\033[0m %s\n" "$1"
}

fail() {
  printf "\n\033[1;31m[error]\033[0m %s\n" "$1" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

ensure_repo_root() {
  [[ -d ".git" ]] || warn "No .git directory found. Run this from the EduBoost repo root."
  [[ -d "$FRONTEND_DIR" ]] || fail "Frontend directory not found: $FRONTEND_DIR"
  [[ -f "requirements.txt" ]] || warn "requirements.txt not found at repo root. Render buildCommand assumes root requirements.txt."
}

write_render_yaml() {
  log "Writing render.yaml for Render Free Web Service..."

  cat > render.yaml <<EOF
services:
  - type: web
    name: ${BACKEND_SERVICE_NAME}
    runtime: python
    plan: free
    region: ${BACKEND_REGION}
    branch: main
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn ${BACKEND_MODULE} --host 0.0.0.0 --port \$PORT
    healthCheckPath: ${BACKEND_HEALTH_PATH}
    autoDeployTrigger: commit
    envVars:
      - key: PYTHON_VERSION
        value: "${PYTHON_VERSION}"

      - key: ENVIRONMENT
        value: "${ENVIRONMENT}"

      - key: APP_NAME
        value: "${APP_NAME}"

      - key: API_BASE_URL
        value: "${API_BASE_URL}"

      - key: FRONTEND_URL
        value: "${FRONTEND_PUBLIC_URL}"

      - key: CORS_ORIGINS
        value: "${CORS_ORIGINS}"

      # Supabase Postgres connection string.
      # Paste this during Render Blueprint creation.
      - key: DATABASE_URL
        sync: false

      # Secret key for JWT/session/signing.
      # Render will generate one during initial Blueprint creation.
      - key: SECRET_KEY
        generateValue: true

      # Use whichever Redis variables EduBoost currently reads.
      # For Upstash REST SDK:
      - key: UPSTASH_REDIS_REST_URL
        sync: false
      - key: UPSTASH_REDIS_REST_TOKEN
        sync: false

      # For normal Redis clients, if your backend uses redis:// or rediss://:
      - key: REDIS_URL
        sync: false
EOF
}

write_backend_env_example() {
  log "Writing .env.render.example..."

  cat > .env.render.example <<EOF
# Paste these into Render when creating the ${BACKEND_SERVICE_NAME} Blueprint/Web Service.

ENVIRONMENT=${ENVIRONMENT}
APP_NAME=${APP_NAME}
API_BASE_URL=${API_BASE_URL}
FRONTEND_URL=${FRONTEND_PUBLIC_URL}
CORS_ORIGINS=${CORS_ORIGINS}

# Supabase:
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

# Upstash REST SDK:
UPSTASH_REDIS_REST_URL=https://YOUR-UPSTASH-ENDPOINT
UPSTASH_REDIS_REST_TOKEN=YOUR-UPSTASH-TOKEN

# Upstash Redis protocol, if EduBoost uses redis-py / aioredis:
REDIS_URL=rediss://default:PASSWORD@HOST:PORT

# Render can generate this from render.yaml, but keep here for local dev:
SECRET_KEY=replace-with-a-long-random-string
EOF
}

write_frontend_env() {
  log "Writing frontend production env file..."

  cat > "${FRONTEND_DIR}/.env.production.local" <<EOF
NEXT_PUBLIC_API_URL=${API_BASE_URL}
NEXT_PUBLIC_ENVIRONMENT=${ENVIRONMENT}
NEXT_PUBLIC_APP_NAME=${APP_NAME}
EOF
}

build_frontend() {
  log "Installing and building frontend..."

  pushd "$FRONTEND_DIR" >/dev/null

  if [[ -f package-lock.json ]]; then
    npm ci
  else
    npm install
  fi

  npm run build

  popd >/dev/null
}

detect_static_output_dir() {
  local candidates=(
    "${FRONTEND_DIR}/out"
    "${FRONTEND_DIR}/dist"
    "${FRONTEND_DIR}/build"
  )

  for dir in "${candidates[@]}"; do
    if [[ -d "$dir" ]]; then
      echo "$dir"
      return 0
    fi
  done

  return 1
}

deploy_frontend_cloudflare_pages() {
  log "Deploying frontend to Cloudflare Pages..."

  local output_dir
  if ! output_dir="$(detect_static_output_dir)"; then
    cat <<EOF

No static frontend output directory found.

Expected one of:
  - ${FRONTEND_DIR}/out
  - ${FRONTEND_DIR}/dist
  - ${FRONTEND_DIR}/build

For a static Next.js export, ensure next.config.js or next.config.mjs contains:

  const nextConfig = {
    output: "export",
    images: {
      unoptimized: true,
    },
  };

  export default nextConfig;

Then rerun:

  npm run build

EOF
    fail "Cloudflare Pages needs a static output directory."
  fi

  npx wrangler pages deploy "$output_dir" \
    --project-name "$FRONTEND_PROJECT_NAME" \
    --branch main
}

print_manual_provider_steps() {
  cat <<EOF

============================================================
EduBoost demo deployment config generated
============================================================

1. Supabase Free Postgres
   - Create a Supabase project.
   - Copy the Postgres connection string.
   - Use it as DATABASE_URL in Render.

2. Upstash Redis Free
   - Create one free Redis database.
   - Copy:
       UPSTASH_REDIS_REST_URL
       UPSTASH_REDIS_REST_TOKEN
     and/or:
       REDIS_URL
   - Paste them into Render.

3. Render Free Web Service
   - Push render.yaml to GitHub.
   - In Render:
       New -> Blueprint
       Select the EduBoost repo
       Confirm render.yaml
   - When prompted, paste:
       DATABASE_URL
       UPSTASH_REDIS_REST_URL
       UPSTASH_REDIS_REST_TOKEN
       REDIS_URL, if EduBoost uses Redis protocol clients

4. Cloudflare Pages
   - Frontend project:
       ${FRONTEND_PROJECT_NAME}
   - Expected URL:
       ${FRONTEND_PUBLIC_URL}
   - Backend API URL baked into frontend:
       ${API_BASE_URL}

5. Local override examples

   APP_NAME=eduboost \\
   FRONTEND_PROJECT_NAME=eduboost-demo \\
   BACKEND_SERVICE_NAME=eduboost-api \\
   API_BASE_URL=https://eduboost-api.onrender.com \\
   ./deploy-eduboost-demo.sh

============================================================

EOF
}

main() {
  need_cmd node
  need_cmd npm
  need_cmd npx
  need_cmd git

  ensure_repo_root
  write_render_yaml
  write_backend_env_example
  write_frontend_env
  build_frontend
  deploy_frontend_cloudflare_pages
  print_manual_provider_steps
}

main "$@"