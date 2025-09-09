from sqlalchemy.orm import Session
from ..models import Tool
from ..utils.scoring import load_weights, score_row

def recommend(db: Session, answers: dict, budget_monthly: float | None, must_integrate_with: list[str], prefer_self_hostable: bool, max_tool_count: int = 8):
    weights = load_weights()
    q = db.query(Tool)

    # Hard filters by compliance / self-host preference (basic example)
    if prefer_self_hostable:
        q = q.filter(Tool.n8n == True)  # heuristic placeholder for self-hostable capable tools

    tools = q.all()
    # Light filter by integrations
    if must_integrate_with:
        tools = [t for t in tools if t.integrations_csv and any(m.lower() in t.integrations_csv.lower() for m in must_integrate_with)] or tools

    # Score compute (recompute total_score transiently)
    scored = []
    for t in tools:
        total = score_row(t, weights)
        priced = (t.price_low_usd or 0.0)
        scored.append((total, priced, t))

    # Greedy utility-per-dollar subject to budget
    stack, cost = [], 0.0
    for total, price, t in sorted(scored, key=lambda x: (-(x[0]/(x[1] or 1)), -x[0])):
        if len(stack) >= max_tool_count:
            break
        if budget_monthly is None or (cost + (price or 0.0)) <= budget_monthly:
            stack.append(t)
            cost += (price or 0.0)

    # Alternates: top 2 not in stack
    picked_ids = set(s.tool_id for s in stack)
    alt = [t for _,__, t in sorted(scored, key=lambda x: -x[0]) if t.tool_id not in picked_ids][:2]

    return stack, alt, cost, "Ranked by weighted utility and cost-awareness."
