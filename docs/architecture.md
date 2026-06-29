# ResearchCloud Architecture

## Overview

ResearchCloud is split into a React single-page app and a FastAPI backend. The backend
is the integration point with Nutanix: it stores Prism Central connections (credentials
encrypted at rest) and talks to Nutanix via a pluggable client abstraction.

```
Browser (React + Mantine)
   |  HTTPS + JWT
   v
FastAPI backend
   |-- API routers (auth, connections, resources)
   |-- service layer
   |-- NutanixClient  --->  real v4 REST client  ---> Prism Central
   |                  \-->  mock client (dev/CI/demo)
   |-- provisioners (Calm DSL, Terraform)  [Phase 2+]
   |-- SQLAlchemy (SQLite dev / Postgres prod)
```

## Backend layout (`backend/app`)

- `core/` - configuration (`config.py`), JWT + password hashing (`security.py`),
  Fernet credential encryption (`crypto.py`).
- `db/` - SQLAlchemy engine, session, declarative base.
- `models/` - ORM models: `User`, `PrismConnection`.
- `schemas/` - Pydantic request/response models.
- `nutanix/` - the `NutanixClient` abstraction (`base.py`), `mock.py`, `real.py`,
  and a `factory.py` that picks the implementation per connection.
- `services/` - business logic (e.g. `connection_service.py`).
- `api/` - FastAPI routers and dependencies.

## Deployment

ResearchCloud deploys onto a single Debian VM via `deploy/vm/deploy.sh` (git-based,
no containers): the backend runs as a `systemd` service behind nginx, which also serves
the built frontend and proxies `/api`. SQLite is used by default. See
[`deploy/vm/README.md`](../deploy/vm/README.md).

## Nutanix client abstraction

`NutanixClient` (in `nutanix/base.py`) defines the operations the app needs
(clusters, projects, file servers, object stores). Two implementations:

- `RealNutanixClient` - calls the Nutanix v4 REST APIs (`clustermgmt`, `files`,
  `objects`) and the v3 API for Projects (full v4 Projects support lands mid-2026).
- `MockNutanixClient` - deterministic in-memory data so the app runs end-to-end with
  no hardware. Selected when `RC_FORCE_MOCK_NUTANIX=true` (default in dev).

`factory.get_client(connection)` returns the right client. Switching to live mode is
a config change (`RC_FORCE_MOCK_NUTANIX=false`) plus valid stored credentials.

### Live v4 request requirements

The Nutanix v4 REST APIs require specifics that `RealNutanixClient` handles:

- **`Ntnx-Request-Id`** (a fresh UUID) on every POST/PUT/DELETE for idempotency -
  omitting it returns `400 BAD REQUEST`.
- **`$objectType`** discriminator in create/update bodies (e.g. `vmm.v4.ahv.config.Vm`).
- **`If-Match`** (resource ETag) on updates/actions such as VM power operations - the
  client first GETs the resource to read its ETag.
- Create calls are asynchronous (`202 ACCEPTED` returning a task); the new entity
  appears on the next list refresh.

On any live error the client surfaces the Nutanix response body so schema/permission
issues are visible in the UI notification.

## Security

- Auth is JWT bearer tokens (`/api/auth/login`). A dev admin is seeded on startup.
- Prism Central secrets are encrypted with Fernet before storage and never returned
  by the API.
- AD-linked identity and RBAC are scoped for Phase 4.

## Frontend layout (`frontend/src`)

- `api/` - typed API client and shared types.
- `auth/` - auth context (token + current user).
- `state/` - active Prism Central connection context.
- `components/` - app shell, shared UI.
- `pages/` - Dashboard, Connections, Projects, Files, Objects, Login.
