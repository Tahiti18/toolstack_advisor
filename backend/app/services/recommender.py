# backend/app/services/recommender.py
from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from ..models import Tool
from ..utils.scoring import load_weights, score_row

# Map channels to the categories a viable stack should cover
CHANNEL_CATEGORY_MAP: Dict[str, List[str]] = {
    "SEO": ["SEO", "Copy & Content"],
    "Paid Ads": ["Ads & Creatives", "Image & Design"],
    "Social Organic": ["Social & Scheduling", "Image & Design", "Video Creation & Editing"],
    "YouTube/Video": ["Video Creation & Editing", "Voice & Audio", "Image & Design"],
    "Email": ["CRM, Outreach & Sales Ops", "Copy & Content"],
    "Cold Outreach": ["CRM, Outreach & Sales Ops", "Automation & Agents"],
    "Partnerships": ["CRM, Outreach & Sales Ops"],
}

# Category base weights (all 1.0; boosted by answers)
BASE_CATEGORY_WEIGHTS = {
    "Research & Strategy": 1.0,
    "Copy & Content": 1.0,
    "SEO": 1.0,
    "Ads & Creatives": 1.0,
    "Social & Scheduling": 1.0,
    "Video Creation & Editing": 1.0,
    "Image & Design": 1
