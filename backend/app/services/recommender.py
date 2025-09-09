# backend/app/services/recommender.py
from __future__ import annotations
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from ..models import Tool
from ..utils.scoring import load_weights, score_row

# Channels → categories to prioritize (not hard requirements)
CHANNEL_CATEGORY_MAP: Dict[str, List[str]] = {
    "SEO": ["SEO", "Copy & Content"],
    "Paid Ads": ["Ads & Creatives", "Image & Design"],
    "Social Organic": ["Social & Scheduling", "Image & Design", "Video Creation & Editing"],
    "YouTube/Video": ["Video Creation & Editing", "Voice & Audio", "Image & Design"],
    "Email": ["CRM, Outreach & Sales Ops", "Copy & Content"],
    "Cold Outreach": ["CRM, Outreach & Sales Ops", "Automation & Agents"],
    "Partnerships": ["CRM, Outreach & Sales Ops"],
    # catch-alls
    "Research": ["Research & Strategy", "Copy & Content"],
}

def _preferred_categories(answers: dict) -> List[str]:
    cats: List[str] = []
    channels = answers.get("channels") or answers.get("gtm_title") or []
    if isinstance(channels, str):
        channels = [channels]
    for ch in channels:
        cats.extend(CHANNEL_CATEGORY_MAP.get(ch, []))
    # Always allow a few general categories
    cats.extend(["Research & Strategy", "Copy & Content", "Automation & Agents"])
    # de-dup, preserve order
    seen = set(); ordered = []
    for c in cats:
        if c and c not in seen:
            ordered.append(c); seen.add(c)
    return ordered

def _category_boost(category: str, preferred: List[str]) -> float:
    # Early categories get a slightly higher boost
    if category in preferred:
        idx = preferred.index(category)
        return max(1.05, 1.30 - 0.03 * idx)  # 1.30 → 1.05
    return 1.0

def recommend(
    db: Session,
    answers: dict,
    budget_monthly: float | None,
    must_integrate_with: List[str],
    prefer_self_hostable: bool,
    max_tool_count: int = 8
) -> Tuple[List[Tool], List[Tool], float, str]:

    weights = load_weights()  # uses backend/data/scoring_weights_default.json

    # 1) START from all tools
    q = db.query(Tool)

    # 2) Hard filters
    if prefer_self_hostable:
        # Cheap heuristic: keep tools that expose webhooks or n8n support
        q = q.filter((Tool.n8n == True) | (Tool.webhooks == True))  # noqa: E712

    tools = q.all()

    if must_integrate_with:
        miw = [m.lower() for m in must_integrate_with if m]
        filtered = []
        for t in tools:
            blob = (t.integrations_csv or "").lower()
            if any(m in blob for m in miw):
                filtered.append(t)
        tools = filtered or tools  # if nothing matched, fall back to all

    if not tools:
        return [], [], 0.0, "No tools matched the constraints."

    # 3) Compute scores with category boosts
    preferred = _preferred_categories(answers or {})
    scored: List[tuple[float, float, Tool]] = []
    for t in tools:
        base = score_row(t, weights)  # uses numeric fields already on row
        boost = _category_boost(t.category or "", preferred)
        total = round(base * boost, 4)
        price = float(t.price_low_usd or 0.0)
        scored.append((total, price, t))

    # 4) Assemble within budget (utility-per-dollar, then raw score)
    picked: List[Tool] = []
    cost = 0.0
    for total, price, t in sorted(scored, key=lambda x: (-(x[0] / (x[1] or 1.0)), -x[0])):
        if len(picked) >= max_tool_count:
            break
        next_cost = cost + (price or 0.0)
        if (budget_monthly is None) or (next_cost <= budget_monthly):
            picked.append(t)
            cost = next_cost

    if not picked:
        # If budget prevented everything, pick the single best free/cheapest tool
        t = sorted(scored, key=lambda x: (-x[0], x[1]))[0][2]
        picked = [t]
        cost = float(t.price_low_usd or 0.0)

    # 5) Alternates = top-scoring not picked (2)
    picked_ids = {p.tool_id for p in picked}
    alternates = [t for _, __, t in sorted(scored, key=lambda x: -x[0]) if t.tool_id not in picked_ids][:2]

    rationale = "Ranked by weighted utility with category boosts and budget-awareness."
    return picked, alternates, round(cost, 2), rationale
