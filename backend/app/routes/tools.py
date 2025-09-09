from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from slugify import slugify
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tools")
def list_tools(q: str | None = None,
               category: str | None = None,
               min_score: float | None = None,
               page: int = 1, page_size: int = 20,
               db: Session = Depends(get_db)):
    query = db.query(models.Tool)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(models.Tool.name.ilike(like) | models.Tool.description_short.ilike(like))
    if category:
        query = query.filter(models.Tool.category == category)
    if min_score is not None:
        query = query.filter(models.Tool.total_score >= min_score)
    total = query.count()
    items = query.order_by(models.Tool.total_score.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": [tool_to_dict(t) for t in items]}

@router.get("/tools/{tool_id}")
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    t = db.query(models.Tool).filter(models.Tool.tool_id == tool_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool_to_dict(t)

@router.post("/tools", response_model=schemas.ToolOut)
def upsert_tool(payload: schemas.ToolIn, db: Session = Depends(get_db)):
    t = db.query(models.Tool).filter(models.Tool.tool_id == payload.tool_id).first()
    if not t:
        t = models.Tool(tool_id=payload.tool_id, slug=slugify(payload.name))
    for k, v in payload.model_dump().items():
        setattr(t, k, v)
    db.add(t); db.commit(); db.refresh(t)
    return payload

def tool_to_dict(t: models.Tool):
    return {
        "tool_id": t.tool_id, "name": t.name, "slug": t.slug,
        "homepage_url": t.homepage_url,
        "description_short": t.description_short,
        "description_long": t.description_long,
        "category": t.category, "subcategory": t.subcategory,
        "tags_csv": t.tags_csv, "pricing_model": t.pricing_model,
        "price_low_usd": t.price_low_usd, "price_high_usd": t.price_high_usd,
        "free_tier": t.free_tier, "trial_days": t.trial_days, "plan_notes": t.plan_notes,
        "api_available": t.api_available, "zapier": t.zapier, "make": t.make, "n8n": t.n8n, "webhooks": t.webhooks,
        "integrations_csv": t.integrations_csv,
        "gdpr": t.gdpr, "soc2": t.soc2, "hipaa": t.hipaa,
        "oauth": t.oauth, "sso": t.sso, "rbac": t.rbac,
        "accuracy_score": t.accuracy_score, "speed_score": t.speed_score, "cost_efficiency_score": t.cost_efficiency_score,
        "integrations_score": t.integrations_score, "data_control_score": t.data_control_score,
        "learning_curve_score": t.learning_curve_score, "longevity_score": t.longevity_score,
        "total_score": t.total_score, "score_notes": t.score_notes,
        "best_use_cases_csv": t.best_use_cases_csv, "buyer_personas_csv": t.buyer_personas_csv, "ideal_industries_csv": t.ideal_industries_csv,
        "reviewer_citations_csv": t.reviewer_citations_csv, "reviewer_urls_csv": t.reviewer_urls_csv,
        "affiliate_link": t.affiliate_link, "last_verified_at": str(t.last_verified_at)
    }
