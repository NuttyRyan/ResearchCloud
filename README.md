# ResearchCloud

ResearchCloud is a web platform that fronts Nutanix Prism Central services, giving
research teams a self-service portal to manage Nutanix infrastructure. The UI follows
the Nutanix brand (purple `#7855fa`, charcoal, rounded typography) and the platform is
designed to deploy to Nutanix NKP for high availability.

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
| Deploy | Docker + Helm (Nutanix NKP) | [`deploy/`](deploy/) |

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

## Deployment (Nutanix NKP)

Container images and a Helm chart live in [`deploy/`](deploy/):

```bash
helm lint deploy/helm/researchcloud
helm template rc deploy/helm/researchcloud
```

The chart runs two replicas of each tier with a PodDisruptionBudget and topology
spread constraints for high availability.
