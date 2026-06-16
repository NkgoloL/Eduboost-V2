#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${PHASE02R_MINIO_CONTAINER:-phase02r-minio-gate}"
MINIO_IMAGE="${PHASE02R_MINIO_IMAGE:-minio/minio:RELEASE.2025-04-22T22-12-26Z}"
MC_IMAGE="${PHASE02R_MC_IMAGE:-minio/mc:RELEASE.2025-04-16T18-13-26Z}"
ENDPOINT="${S3_ENDPOINT_URL:-http://127.0.0.1:19000}"
ROOT_USER="${PHASE02R_MINIO_ROOT_USER:-phase02rroot}"
ROOT_PASSWORD="${PHASE02R_MINIO_ROOT_PASSWORD:-phase02rrootsecret}"
SCOPED_USER="${AWS_ACCESS_KEY_ID:-phase02rscoped}"
SCOPED_PASSWORD="${AWS_SECRET_ACCESS_KEY:-phase02rscopedsecret}"
BUCKET="${PHASE02R_OBJECT_STORAGE_BUCKET:-phase02r-gate}"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    docker start "$CONTAINER" >/dev/null
  else
    docker run -d \
      --name "$CONTAINER" \
      -p 19000:9000 \
      -p 19001:9001 \
      -e "MINIO_ROOT_USER=$ROOT_USER" \
      -e "MINIO_ROOT_PASSWORD=$ROOT_PASSWORD" \
      "$MINIO_IMAGE" \
      server /data --console-address ":9001" >/dev/null
  fi
fi

for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  if curl -fsS "$ENDPOINT/minio/health/ready" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "$ENDPOINT/minio/health/ready" >/dev/null

policy_file="$(mktemp)"
cat > "$policy_file" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetBucketLocation", "s3:GetBucketVersioning", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::$BUCKET"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::$BUCKET/phase02r/gate-2r0/*"]
    }
  ]
}
JSON

docker run --rm --network host --entrypoint sh -v "$policy_file:/tmp/phase02r-minio-policy.json:ro" "$MC_IMAGE" -lc "
  mc alias set local '$ENDPOINT' '$ROOT_USER' '$ROOT_PASSWORD' >/dev/null &&
  mc mb --ignore-existing local/'$BUCKET' >/dev/null &&
  mc version enable local/'$BUCKET' >/dev/null &&
  (mc admin user add local '$SCOPED_USER' '$SCOPED_PASSWORD' >/dev/null || true) &&
  (mc admin policy create local phase02r-gate-policy /tmp/phase02r-minio-policy.json >/dev/null || true) &&
  mc admin policy attach local phase02r-gate-policy --user '$SCOPED_USER' >/dev/null
"

rm -f "$policy_file"

cat <<EOF
PHASE02R MinIO probe ready
endpoint=$ENDPOINT
bucket=$BUCKET
scoped_user_configured=true
credentials_redacted=true
EOF
