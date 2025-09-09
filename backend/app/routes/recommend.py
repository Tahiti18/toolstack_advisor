from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..schemas import RecommendRequest, RecommendResponse
from ..services.recommender import recommend

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/recommend", response_model=RecommendResponse)
def get_recommendation(payload: RecommendRequest, db: Session = Depends(get_db)):
    stack, alt, cost, rationale = recommend(
        db,
        answers=payload.answers,
        budget_monthly=payload.budget_monthly,
        must_integrate_with=payload.must_integrate_with,
        prefer_self_hostable=payload.prefer_self_hostable,
        max_tool_count=payload.max_tool_count
    )
    return {
        "tools": [vars_min(t) for t in stack],
        "alternates": {"top": [vars_min(a) for a in alt]},
        "total_monthly_estimate": round(cost, 2),
        "rationale": rationale
    }

def vars_min(t):
    return {"tool_id": t.tool_id, "name": t.name, "category": t.category, "price_low_usd": t.price_low_usd, "total_score": t.total_score}
