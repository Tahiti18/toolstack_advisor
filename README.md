# ToolStack Advisor — Backend Foundation (FastAPI + Postgres)

This is a production-ready **server foundation** for your AI Tool Recommendation platform.
It includes: FastAPI app, Postgres models, scoring engine, questionnaire, CSV ingestion, and clean REST API.

Deploy target: **Railway (web service)**. Local run works with SQLite by default; in production use Postgres via `DATABASE_URL`.

## Key Endpoints
- GET `/health` — service status
- GET `/questionnaire` — current adaptive questionnaire (JSON)
- GET `/tools` — list tools with filters (`q`, `category`, `min_score`, pagination)
- POST `/tools` — ingest/update a tool (idempotent by `tool_id`)
- GET `/tools/{tool_id}` — fetch by id
- POST `/recommend` — returns a ranked stack for given answers + constraints

## Quick Start (Local)
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) `cp .env.example .env`  (edit if needed; SQLite default is fine)
4) `python backend/app/seed.py`  (loads sample tools + builds scores)
5) `uvicorn backend.app.main:app --reload` → open http://127.0.0.1:8000/health

## Railway Deploy (one step at a time)
Step 1 — **Create** new service from this repo.
• Railway → Architecture → + New → **Service** → Deploy from GitHub (connect repo).

(Stop here; I’ll give you the next step after you confirm Step 1 is done.)

## Environment Variables
See `.env.example`. On Railway set:
- `DATABASE_URL` (Reference your Postgres if you create one; SQLite will be ignored if this is set)
- `ALLOWED_ORIGINS` (comma-separated; e.g., `https://your-frontend.netlify.app,http://localhost:5173`)
- `DEFAULT_TIMEZONE` (e.g., `Asia/Nicosia`)

## Notes
- Scoring weights and questionnaire are editable without redeploy (`backend/data/*.json` + `/admin/reindex` to refresh later).
- CSV schema included at `backend/data/ai_tools_schema_template.csv`.
