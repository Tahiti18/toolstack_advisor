from fastapi import APIRouter, Depends, Body
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..services.recommender import recommend

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/recommend")
def get_recommendation(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    answers: Dict[str, Any] = payload.get("answers") or {}
    budget_monthly = payload.get("budget_monthly")
    must_integrate_with: List[str] = payload.get("must_integrate_with", []) or []
    prefer_self_hostable = bool(payload.get("prefer_self_hostable", False))
    max_tool_count = int(payload.get("max_tool_count", 8))

    picked, alternates, cost, rationale = recommend(
        db=db,
        answers=answers,
        budget_monthly=budget_monthly,
        must_integrate_with=must_integrate_with,
        prefer_self_hostable=prefer_self_hostable,
        max_tool_count=max_tool_count,
    )

    def to_item(t):
        return {
            "tool_id": t.tool_id,
            "name": t.name,
            "category": t.category,
            "price_low_usd": t.price_low_usd,
            "total_score": t.total_score,
        }

    return {
        "tools": [to_item(t) for t in picked],
        "alternates": [to_item(t) for t in alternates],
        "total_monthly_estimate": cost,
        "rationale": rationale,
    }
