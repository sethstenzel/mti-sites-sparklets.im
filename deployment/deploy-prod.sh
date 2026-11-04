#!/usr/bin/env bash
# Build locally and push Sparklets.im to the production VPS.
#
# Usage (from the repo root, in Git Bash / any POSIX shell):
#   ./deployment/deploy-prod.sh
#
# What it does:
#   1. Builds the frontend (npm ci && npm run build)
#   2. Uploads backend code + frontend dist as a tarball over SSH
#   3. Backs up the SQLite DB, installs the new files, runs `uv sync`
#   4. Generates backend/.env with an ADMIN_TOKEN if one doesn't exist
#   5. Restarts the backend (kills uvicorn; systemd Restart=always brings it back,
#      because appsuser has no sudo rights for this service)
#   6. Health-checks the API
#
# Old hashed frontend assets are kept so browsers holding a cached index.html keep working.

set -euo pipefail

# SSH is only open over Tailscale (mti-sites); override with DEPLOY_HOST if needed
HOST="${DEPLOY_HOST:-appsuser@100.120.142.3}"
APP_DIR="/var/www/sparklets.im"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "==> Building frontend"
(cd "$ROOT/frontend" && npm ci --no-audit --no-fund && npm run build)

echo "==> Packaging"
mkdir -p "$TMP/pkg/backend" "$TMP/pkg/frontend"
cp "$ROOT"/backend/{main.py,database.py,models.py,pyproject.toml,uv.lock,README.md,API.md} "$TMP/pkg/backend/"
cp -r "$ROOT/frontend/dist" "$TMP/pkg/frontend/dist"
tar -C "$TMP/pkg" -czf "$TMP/release.tgz" .

echo "==> Uploading to $HOST"
scp -q "$TMP/release.tgz" "$HOST:/tmp/sparklets-release-$STAMP.tgz"

echo "==> Installing on server"
ssh "$HOST" APP_DIR="$APP_DIR" STAMP="$STAMP" 'bash -s' <<'REMOTE'
set -euo pipefail
cd "$APP_DIR"
mkdir -p backups
REL="/tmp/sparklets-release-$STAMP.tgz"
STAGE="$(mktemp -d)"
tar -C "$STAGE" -xzf "$REL"

# backups: database + current code
[ -f backend/sparklets.sqlite ] && cp backend/sparklets.sqlite "backups/sparklets-$STAMP.sqlite"
tar -czf "backups/code-$STAMP.tgz" backend/*.py backend/pyproject.toml frontend/dist 2>/dev/null || true
chmod 640 backups/*-"$STAMP".* 2>/dev/null || true
# keep deploy backups for 30 days (the privacy policy promises this)
find backups -maxdepth 1 -type f \( -name 'sparklets-*.sqlite' -o -name 'code-*.tgz' \) -mtime +30 -delete

# backend code
cp "$STAGE"/backend/* backend/

# frontend: copy the new build (all files and folders) over the old one;
# old hashed assets are kept so browsers holding a cached index.html keep working
mkdir -p frontend/dist
cp -r "$STAGE"/frontend/dist/. frontend/dist/

# secrets in backend/.env: admin token for /manage, key for image file names
for KEY in ADMIN_TOKEN IMAGE_HASH_KEY; do
  if [ ! -f backend/.env ] || ! grep -q "^$KEY=" backend/.env; then
    echo "$KEY=$(head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 40)" >> backend/.env
    chmod 600 backend/.env
    echo "Generated a new $KEY in $APP_DIR/backend/.env"
  fi
done

# dependencies
(cd backend && "$HOME/.local/bin/uv" sync --frozen --no-dev 2>&1 | tail -3)

# restart: systemd restarts uvicorn after it exits (Restart=always, RestartSec=10)
PID="$(pgrep -u "$(id -u)" -f 'sparklets.im/backend/.venv/bin/uvicorn main:app' || true)"
if [ -n "$PID" ]; then
  kill $PID
  while kill -0 $PID 2>/dev/null; do sleep 0.5; done
  echo "Stopped backend (pid $PID); waiting for systemd to restart it"
fi

for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:18002/api/health >/dev/null 2>&1; then
    echo "Backend healthy after ${i}s"
    break
  fi
  sleep 1
  if [ "$i" = 30 ]; then echo "Backend did not come back within 30s" >&2; exit 1; fi
done

rm -rf "$STAGE" "$REL"
REMOTE

echo "==> Public checks"
curl -fsS https://sparklets.im/api/health && echo
curl -fsS -o /dev/null -w "Homepage: HTTP %{http_code}\n" https://sparklets.im/
echo "Done."
