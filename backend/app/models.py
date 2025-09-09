from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from .db import Base

class Tool(Base):
    __tablename__ = "tools"
    tool_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    homepage_url = Column(String)
    description_short = Column(String)
    description_long = Column(String)
    category = Column(String, index=True)
    subcategory = Column(String, index=True)
    tags_csv = Column(String)
    pricing_model = Column(String)
    price_low_usd = Column(Float)
    price_high_usd = Column(Float)
    free_tier = Column(Boolean, default=False)
    trial_days = Column(Integer)
    plan_notes = Column(String)

    api_available = Column(Boolean, default=False)
    zapier = Column(Boolean, default=False)
    make = Column(Boolean, default=False)
    n8n = Column(Boolean, default=False)
    webhooks = Column(Boolean, default=False)

    integrations_csv = Column(String)
    gdpr = Column(Boolean, default=False)
    soc2 = Column(Boolean, default=False)
    hipaa = Column(Boolean, default=False)

    oauth = Column(Boolean, default=False)
    sso = Column(Boolean, default=False)
    rbac = Column(Boolean, default=False)

    accuracy_score = Column(Float, default=0)
    speed_score = Column(Float, default=0)
    cost_efficiency_score = Column(Float, default=0)
    integrations_score = Column(Float, default=0)
    data_control_score = Column(Float, default=0)
    learning_curve_score = Column(Float, default=0)
    longevity_score = Column(Float, default=0)
    total_score = Column(Float, default=0)
    score_notes = Column(String)

    best_use_cases_csv = Column(String)
    buyer_personas_csv = Column(String)
    ideal_industries_csv = Column(String)

    reviewer_citations_csv = Column(String)
    reviewer_urls_csv = Column(String)
    affiliate_link = Column(String)

    last_verified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
