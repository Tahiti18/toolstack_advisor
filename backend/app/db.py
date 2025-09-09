from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # SQLite fallback for local dev
    DATABASE_URL = "sqlite:///./toolstack.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
