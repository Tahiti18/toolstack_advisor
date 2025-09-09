from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os, asyncio, urllib.request

from .config import get_settings
from .db import init_db
from .routes import health, questionnaire, tools, recommend, ingest

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

# CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")] if settings.ALLOWED_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB
init_db()

# Static + favicon
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(Path("backend/app/static/favicon.ico"))

# Routes
app.include_router(health.router)
app.include_router(questionnaire.router)
app.include_router(tools.router)
app.include_router(recommend.router)
app.include_router(ingest.router)

# Keep-alive (prevents Railway auto-sleep) — uses stdlib only
async def _keepalive_loop():
    port = int(os.getenv("PORT", "8000"))
    url = f"http://127.0.0.1:{port}/health"
    while True:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass
        await asyncio.sleep(240)  # every 4 minutes

@app.on_event("startup")
async def _startup():
    app.state._keepalive_task = asyncio.create_task(_keepalive_loop())

@app.on_event("shutdown")
async def _shutdown():
    t = getattr(app.state, "_keepalive_task", None)
    if t:
        t.cancel()
