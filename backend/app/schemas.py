from pydantic import BaseModel, Field
from typing import Optional

class ToolIn(BaseModel):
    tool_id: str
    name: str
    homepage_url: Optional[str] = None
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    tags_csv: Optional[str] = None
    pricing_model: Optional[str] = None
    price_low_usd: Optional[float] = None
    price_high_usd: Optional[float] = None
    free_tier: Optional[bool] = False
    trial_days: Optional[int] = None
    plan_notes: Optional[str] = None
    api_available: Optional[bool] = False
    zapier: Optional[bool] = False
    make: Optional[bool] = False
    n8n: Optional[bool] = False
    webhooks: Optional[bool] = False
    integrations_csv: Optional[str] = None
    gdpr: Optional[bool] = False
    soc2: Optional[bool] = False
    hipaa: Optional[bool] = False
    oauth: Optional[bool] = False
    sso: Optional[bool] = False
    rbac: Optional[bool] = False
    accuracy_score: Optional[float] = 0
    speed_score: Optional[float] = 0
    cost_efficiency_score: Optional[float] = 0
    integrations_score: Optional[float] = 0
    data_control_score: Optional[float] = 0
    learning_curve_score: Optional[float] = 0
    longevity_score: Optional[float] = 0
    total_score: Optional[float] = 0
    score_notes: Optional[str] = None
    best_use_cases_csv: Optional[str] = None
    buyer_personas_csv: Optional[str] = None
    ideal_industries_csv: Optional[str] = None
    reviewer_citations_csv: Optional[str] = None
    reviewer_urls_csv: Optional[str] = None
    affiliate_link: Optional[str] = None

class ToolOut(ToolIn):
    pass

class RecommendRequest(BaseModel):
    answers: dict = Field(default_factory=dict)
    budget_monthly: float | None = None
    must_integrate_with: list[str] = Field(default_factory=list)
    prefer_self_hostable: bool = False
    max_tool_count: int = 8

class RecommendResponse(BaseModel):
    tools: list[dict]
    alternates: dict
    total_monthly_estimate: float
    rationale: str
