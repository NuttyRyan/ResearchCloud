# ResearchCloud

ResearchCloud is a web platform that fronts Nutanix Prism Central services, giving
research teams a self-service portal to manage Nutanix infrastructure. The UI follows
the Nutanix brand (purple `#7855fa`, charcoal, rounded typography) and the platform is
designed to deploy onto a single Debian VM with one bash script.

> Phase 1 (this release) delivers a runnable foundation: Prism Central connection
> management plus a Projects / Files / Objects vertical slice. It runs end-to-end
> locally against a deterministic **mock** Nutanix provider, so no live Prism Central
> is required for development. See [`docs/roadmap.md`](docs/roadmap.md) for what's next.

## Architecture

| Layer | Tech | Location |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite + Mantine | [`frontend/`](frontend/) |
| Backend | Python + FastAPI + SQLAlchemy | [`backend/`](backend/) |
| Provisioning | Nutanix v4 REST APIs, Calm DSL, Terraform | [`backend/app/nutanix`](backend/app/nutanix), [`infra/`](infra/) |
| Deploy | Debian VM (nginx + systemd, git-based) | [`deploy/vm/`](deploy/vm/) |

The backend talks to Nutanix through a `NutanixClient` abstraction with two
implementations: a live v4 REST client and a deterministic mock. The mock is enabled
by default (`RC_FORCE_MOCK_NUTANIX=true`) so the whole app is demoable without hardware.

See [`docs/architecture.md`](docs/architecture.md) for details.

## Prerequisites

- Python 3.11+ (with `python3-venv`)
- Node.js 20+ and npm

## Quick start (development)

Install all dependencies:

```bash
bash scripts/install.sh
```

Run the backend (terminal 1):

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Run the frontend (terminal 2):

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 and sign in with the seeded dev account `admin` / `admin`.
The Vite dev server proxies `/api` to the backend on port 8000.

## Lint, test, build

Backend (run inside `backend/` with the venv activated):

```bash
ruff check .        # lint
pytest              # tests
```

Frontend (run inside `frontend/`):

```bash
npm run lint        # lint
npm run typecheck   # type check
npm run test        # unit tests
npm run build       # production build
```

## Deployment (Debian VM, git-based)

ResearchCloud deploys onto a single Debian VM with one bash script - no Docker or
Kubernetes required. On a fresh Debian 11/12 VM:

```bash
git clone https://github.com/NuttyRyan/ResearchCloud.git
cd ResearchCloud
sudo bash deploy/vm/deploy.sh
```

Then open `http://<vm-ip>/` and sign in with `admin` / `admin`.

The script installs Python, Node.js 20, and nginx; builds the frontend; runs the
backend as a `systemd` service (`uvicorn` on localhost); and configures nginx to serve
the UI and proxy `/api` to the backend. It uses SQLite by default, so there is nothing
else to set up. Re-run it after a `git pull` to update (idempotent); pass `GIT_PULL=1`
to pull first. See [`deploy/vm/README.md`](deploy/vm/README.md) for configuration
options (port, server name, mock vs. live Prism Central) and operations.
