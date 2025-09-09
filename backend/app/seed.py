import csv, os, time
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .models import Tool
from .utils.scoring import load_weights, score_row

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
CSV = os.path.join(BASE, "sample_tools.csv")

def upsert_tool(db: Session, row: dict):
    t = db.query(Tool).filter(Tool.tool_id == row["tool_id"]).first()
    if not t:
        t = Tool(tool_id=row["tool_id"], slug=row["name"].lower().replace(" ","-"))
    # map fields
    for k, v in row.items():
        if k in ["price_low_usd","price_high_usd","accuracy_score","speed_score","cost_efficiency_score","integrations_score","data_control_score","learning_curve_score","longevity_score","total_score"]:
            try: v = float(v) if v!="" else None
            except: v = None
        if k in ["free_tier","api_available","zapier","make","n8n","webhooks","gdpr","soc2","hipaa","oauth","sso","rbac"]:
            v = True if str(v).lower() in ["1","true","yes","y"] else False
        setattr(t, k, v)
    db.add(t)

def main():
    init_db()
    db = SessionLocal()
    with open(CSV, newline="") as f:
        reader = csv.DictReader(f)
        weights = load_weights()
        for row in reader:
            upsert_tool(db, row)
        db.commit()
        # recompute totals
        tools = db.query(Tool).all()
        for t in tools:
            t.total_score = score_row(t, weights)
        db.commit()
    print("Seed complete.")

if __name__ == "__main__":
    main()
