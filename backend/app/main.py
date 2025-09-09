from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routes import health, questionnaire, tools, recommend
from .config import get_settings

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

# Routes
app.include_router(health.router)
app.include_router(questionnaire.router)
app.include_router(tools.router)
app.include_router(recommend.router)
