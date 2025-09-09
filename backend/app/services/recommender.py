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
}

def recommend(
    session: Session,
    answers: Dict[str, str],
    budget_monthly: int = 0,
    must_integrate_with: List[str] | None = None,
    prefer_self_hostable: bool = False,
    max_tool_count: int = 10
) -> List[Tool]:
    """
    Recommend tools based on survey answers and preferences.

    :param session: SQLAlchemy session
    :param answers: dict of user answers
    :param budget_monthly: budget in USD
    :param must_integrate_with: list of required integrations
    :param prefer_self_hostable: whether to prioritize self-hostable tools
    :param max_tool_count: maximum number of tools to return
    :return: list of Tool objects
    """
    if must_integrate_with is None:
        must_integrate_with = []

    # Load scoring weights
    weights = load_weights(BASE_CATEGORY_WEIGHTS, answers)

    # Fetch all tools from DB
    tools: List[Tool] = session.query(Tool).all()

    # Score each tool
    scored: List[Tuple[Tool, float]] = []
    for tool in tools:
        score = score_row(tool, weights)

        # Apply budget filter
        if budget_monthly and tool.price_low_usd and tool.price_low_usd > budget_monthly:
            continue

        # Apply integration filter
        if must_integrate_with:
            integrations = (tool.integrations_csv or "").split(",")
            if not all(req in integrations for req in must_integrate_with):
                continue

        # Apply self-hostable preference
        if prefer_self_hostable and not getattr(tool, "self_hostable", False):
            score *= 0.8  # penalize non-self-hostable tools

        scored.append((tool, score))

    # Sort by score, highest first
    scored.sort(key=lambda x: x[1], reverse=True)

    # Return top N tools
    return [tool for tool, _ in scored[:max_tool_count]]
