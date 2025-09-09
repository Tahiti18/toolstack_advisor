# backend/app/routes/recommend.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.recommender import recommend

router = APIRouter()

class RecommendRequest(BaseModel):
    # answers from /questionnaire (you can add more fields later)
    answers: Dict[str, Any] = Field(default_factory=dict)
    budget_monthly: Optional[float] = None
    must_integrate_with: List[str] = Field(default_factory=list)
    prefer_self_hostable: bool = False
    max_tool_count: int = 8

class RecommendItem(BaseModel):
    tool_id: str
    name: str
    category: Optional[str] = None
    price_low_usd: Optional[float] = None
    total_score: Optional[float] = None

class RecommendResponse(BaseModel):
    tools: List[RecommendItem]
    alternates: List[RecommendItem]
    total_monthly_estimate: float
    rationale: str

@router.post("/recommend", response_model=RecommendResponse)
def get_recommendation(payload: RecommendRequest, db: Session = Depends(get_db)):
    picked, alternates, cost, rationale = recommend(
        db=db,
        answers=payload.answers,
        budget_monthly=payload.budget_monthly,
        must_integrate_with=payload.must_integrate_with,
        prefer_self_hostable=payload.prefer_self_hostable,
        max_tool_count=payload.max_tool_count,
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
