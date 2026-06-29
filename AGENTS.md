# AGENTS.md

ResearchCloud is a Nutanix services portal: a FastAPI backend (`backend/`) and a
React + Vite frontend (`frontend/`), with a single-VM deploy script in `deploy/vm/`
and Terraform skeletons in `infra/`. See `README.md` and `docs/` for full setup,
commands, and architecture.

## Cursor Cloud specific instructions

Dependencies are installed by `scripts/install.sh` (wired via `.cursor/environment.json`).
It creates the backend virtualenv at `backend/.venv` and runs `npm install` in `frontend/`.

Services and how to run them (development):

- Backend (FastAPI): from `backend/`, activate `.venv`, then
  `uvicorn app.main:app --reload --port 8000`. Standard commands are in `README.md`.
- Frontend (Vite): from `frontend/`, `npm run dev` (serves on port 5173).

Non-obvious notes:

- Start the backend before (or alongside) the frontend: the Vite dev server proxies
  `/api` to `http://127.0.0.1:8000`, so frontend API calls 502 until the backend is up.
- The app runs fully against a deterministic **mock** Nutanix provider by default
  (`RC_FORCE_MOCK_NUTANIX=true`), so no live Prism Central is needed to develop or demo.
  Set `RC_FORCE_MOCK_NUTANIX=false` (and supply real connection credentials) for live mode.
- Mock state is in-memory per backend process: created projects/files/objects persist
  until the backend restarts, then reset to seed data. The SQLite DB
  (`backend/researchcloud.db`) persists connections/users across restarts; tables and a
  seeded `admin`/`admin` dev login are created automatically on startup.
- Backend config is environment-driven with the `RC_` prefix (see `backend/.env.example`).
- Production deploy is a single Debian VM via `deploy/vm/deploy.sh` (nginx + systemd,
  SQLite by default); it is idempotent and safe to re-run after a `git pull`.
- `terraform` is not an app dependency and is not installed by the update script; install
  it only when validating the `infra/` skeletons.
