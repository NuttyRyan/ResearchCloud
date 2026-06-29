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
spread constraints for high availability, and bundles a PostgreSQL instance so it
deploys out of the box.

Before installing on NKP, set these so the cluster can actually run it:

```bash
# 1. Build and push the images to a registry your NKP nodes can reach.
docker build -f deploy/docker/backend.Dockerfile  -t <registry>/researchcloud/backend:0.1.0 .
docker build -f deploy/docker/frontend.Dockerfile -t <registry>/researchcloud/frontend:0.1.0 .
docker push <registry>/researchcloud/backend:0.1.0
docker push <registry>/researchcloud/frontend:0.1.0

# 2. Install, pointing at your registry, pull secret, and IngressClass.
#    NKP uses Traefik by default - check `kubectl get ingressclass`.
helm install rc deploy/helm/researchcloud \
  --namespace researchcloud --create-namespace \
  --set global.imageRegistry=<registry> \
  --set imagePullSecrets[0].name=<regcred> \
  --set ingress.className=<your-ingressclass> \
  --set ingress.host=researchcloud.<your-domain> \
  --set secrets.RC_SECRET_KEY=<random-strong-secret>
```

For production HA, disable the bundled Postgres and use a managed/HA database:
`--set postgres.enabled=false --set externalDatabaseUrl=postgresql+psycopg://user:pass@host:5432/db`.

Common deploy failures: `ImagePullBackOff` (images not pushed / registry or pull
secret unset), backend `CrashLoopBackOff` (database unreachable or
`externalDatabaseUrl` unset when `postgres.enabled=false`), and an Ingress with no
ADDRESS (`ingress.className` does not match an existing IngressClass). The chart's
post-install NOTES print this checklist too.
