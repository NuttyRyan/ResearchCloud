#!/usr/bin/env bash
#
# ResearchCloud - single Debian VM deploy (git-based).
#
# Run this from a checkout of the repo on a fresh Debian (11/12) VM:
#
#   sudo bash deploy/vm/deploy.sh
#
# It installs system dependencies, builds the frontend, sets up the backend as a
# systemd service, and serves everything behind nginx. Re-run it any time after a
# `git pull` to update in place (it is idempotent).
#
# Optional environment overrides:
#   HTTP_PORT=80                 nginx listen port
#   SERVER_NAME=_                nginx server_name (e.g. researchcloud.example.com)
#   RC_PORT=8000                 internal backend port (localhost only)
#   RC_FORCE_MOCK_NUTANIX=true   set to "false" to talk to real Prism Central
#   GIT_PULL=1                   run `git pull --ff-only` before deploying
#
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root (e.g. sudo bash deploy/vm/deploy.sh)" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_USER="${SUDO_USER:-root}"

HTTP_PORT="${HTTP_PORT:-80}"
SERVER_NAME="${SERVER_NAME:-_}"
RC_PORT="${RC_PORT:-8000}"
RC_FORCE_MOCK_NUTANIX="${RC_FORCE_MOCK_NUTANIX:-true}"
WEB_ROOT="/var/www/researchcloud"

echo "==> ResearchCloud deploy"
echo "    repo:        $REPO_ROOT"
echo "    run user:    $DEPLOY_USER"
echo "    http port:   $HTTP_PORT"
echo "    backend port:$RC_PORT (localhost)"
echo "    mock mode:   $RC_FORCE_MOCK_NUTANIX"

if [ "${GIT_PULL:-0}" = "1" ]; then
  echo "==> Updating source (git pull --ff-only)"
  sudo -u "$DEPLOY_USER" git -C "$REPO_ROOT" pull --ff-only
fi

echo "==> Installing system dependencies"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx curl ca-certificates git

# Ensure Node.js >= 20 (Debian's apt package is often too old); use NodeSource.
NODE_MAJOR=0
if command -v node >/dev/null 2>&1; then
  NODE_MAJOR="$(node -v | sed 's/^v//' | cut -d. -f1)"
fi
if [ "$NODE_MAJOR" -lt 20 ]; then
  echo "==> Installing Node.js 20.x"
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

echo "==> Backend: virtualenv + dependencies"
cd "$REPO_ROOT/backend"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip -q
# Editable install so a `git pull` + service restart picks up backend changes.
./.venv/bin/pip install -e . -q

# Generate a persistent .env on first deploy (kept across re-runs; not in git).
ENV_FILE="$REPO_ROOT/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "==> Generating $ENV_FILE"
  SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > "$ENV_FILE" <<EOF
RC_SECRET_KEY=$SECRET
RC_FORCE_MOCK_NUTANIX=$RC_FORCE_MOCK_NUTANIX
RC_DATABASE_URL=sqlite:////$REPO_ROOT/backend/researchcloud.db
EOF
fi

# The backend runs as DEPLOY_USER, so make sure it owns its runtime files.
chown -R "$DEPLOY_USER" "$REPO_ROOT/backend/.venv" "$ENV_FILE"

echo "==> Frontend: build"
cd "$REPO_ROOT/frontend"
npm install --no-audit --no-fund
npm run build

echo "==> Publishing frontend to $WEB_ROOT"
rm -rf "$WEB_ROOT"
mkdir -p "$WEB_ROOT"
cp -r "$REPO_ROOT/frontend/dist/." "$WEB_ROOT/"
chown -R www-data:www-data "$WEB_ROOT"

echo "==> Installing systemd service (researchcloud-backend)"
cat > /etc/systemd/system/researchcloud-backend.service <<EOF
[Unit]
Description=ResearchCloud backend (FastAPI)
After=network.target

[Service]
User=$DEPLOY_USER
WorkingDirectory=$REPO_ROOT/backend
EnvironmentFile=$REPO_ROOT/backend/.env
ExecStart=$REPO_ROOT/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port $RC_PORT --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable researchcloud-backend
systemctl restart researchcloud-backend

echo "==> Configuring nginx"
cat > /etc/nginx/sites-available/researchcloud <<EOF
server {
    listen $HTTP_PORT;
    server_name $SERVER_NAME;
    root $WEB_ROOT;
    index index.html;

    # API -> backend (localhost).
    location /api/ {
        proxy_pass http://127.0.0.1:$RC_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # SPA fallback.
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/researchcloud /etc/nginx/sites-enabled/researchcloud
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo ""
echo "==> Done. ResearchCloud is deployed."
echo "    Open:    http://<vm-ip>:$HTTP_PORT/"
echo "    Login:   admin / admin  (change RC_ADMIN_PASSWORD in backend/.env and restart)"
echo "    Backend: systemctl status researchcloud-backend"
echo "    Logs:    journalctl -u researchcloud-backend -f"
