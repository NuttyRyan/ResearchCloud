# Deploying ResearchCloud on a Debian VM

A single bash script deploys the whole app (backend + frontend) onto one Debian VM
from a git checkout. No Docker, Kubernetes, or Helm required.

## What it sets up

- System packages: `python3`/venv, Node.js 20, and `nginx`.
- Backend: a Python virtualenv and a `systemd` service (`researchcloud-backend`)
  running `uvicorn` on `127.0.0.1:8000`.
- Frontend: built with Vite and published to `/var/www/researchcloud`.
- `nginx`: serves the UI and reverse-proxies `/api` to the backend.
- Database: SQLite by default (file in `backend/researchcloud.db`) - zero extra setup.

## Deploy

On a fresh Debian 11/12 VM:

```bash
git clone https://github.com/NuttyRyan/ResearchCloud.git
cd ResearchCloud
sudo bash deploy/vm/deploy.sh
```

Then open `http://<vm-ip>/` and sign in with `admin` / `admin`.

## Updating (redeploy after changes)

Re-run the script any time; it is idempotent. To pull the latest code first:

```bash
sudo GIT_PULL=1 bash deploy/vm/deploy.sh
```

## Configuration

Override via environment variables when running the script:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HTTP_PORT` | `80` | Port nginx listens on |
| `SERVER_NAME` | `_` | nginx `server_name` (e.g. your domain) |
| `RC_PORT` | `8000` | Internal backend port (localhost only) |
| `RC_FORCE_MOCK_NUTANIX` | `true` | Set `false` to talk to real Prism Central |
| `GIT_PULL` | `0` | Set `1` to `git pull --ff-only` before deploying |

Example:

```bash
sudo SERVER_NAME=researchcloud.example.com RC_FORCE_MOCK_NUTANIX=false \
  bash deploy/vm/deploy.sh
```

Persistent settings (including a generated `RC_SECRET_KEY`) live in `backend/.env`,
which is created on first deploy and preserved across re-runs. Edit it and run
`sudo systemctl restart researchcloud-backend` to apply changes. To change the admin
password, set `RC_ADMIN_PASSWORD` in `backend/.env` before the first deploy (the admin
user is seeded once).

## Operations

```bash
systemctl status researchcloud-backend     # service status
journalctl -u researchcloud-backend -f     # backend logs
sudo systemctl restart researchcloud-backend
```
