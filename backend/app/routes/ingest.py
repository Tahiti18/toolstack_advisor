from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import csv, io

from ..db import SessionLocal
from ..models import Tool

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tools/ingest")
async def ingest_tools(csv_file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not csv_file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    content = await csv_file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8", errors="ignore")))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="CSV is empty.")

    created = 0
    updated = 0
    for r in rows:
        tool_id = (r.get("tool_id") or r.get("id") or "").strip()
        if not tool_id:
            continue

        obj = db.query(Tool).filter(Tool.tool_id == tool_id).first()
        fields = {
            "name": r.get("name"),
            "slug": r.get("slug"),
            "homepage_url": r.get("homepage_url"),
            "description_short": r.get("description_short"),
            "description_long": r.get("description_long"),
            "category": r.get("category"),
            "subcategory": r.get("subcategory"),
            "tags_csv": r.get("tags_csv"),
            "pricing_model": r.get("pricing_model"),
            "price_low_usd": float(r.get("price_low_usd") or 0) if r.get("price_low_usd") else None,
            "price_high_usd": float(r.get("price_high_usd") or 0) if r.get("price_high_usd") else None,
            "free_tier": (r.get("free_tier") or "").strip().lower() in ("1","true","yes"),
            "trial_days": int(r.get("trial_days") or 0) if r.get("trial_days") else None,
            "api_available": (r.get("api_available") or "").strip().lower() in ("1","true","yes"),
            "make": (r.get("make") or "").strip().lower() in ("1","true","yes"),
            "n8n": (r.get("n8n") or "").strip().lower() in ("1","true","yes"),
            "webhooks": (r.get("webhooks") or "").strip().lower() in ("1","true","yes"),
            "integrations_csv": r.get("integrations_csv"),
            "gdpr": (r.get("gdpr") or "").strip().lower() in ("1","true","yes"),
            "soc2": (r.get("soc2") or "").strip().lower() in ("1","true","yes"),
            "hipaa": (r.get("hipaa") or "").strip().lower() in ("1","true","yes"),
            "rba": (r.get("rba") or "").strip().lower() in ("1","true","yes"),
            "accuracy_score": float(r.get("accuracy_score") or 0) if r.get("accuracy_score") else None,
            "speed_score": float(r.get("speed_score") or 0) if r.get("speed_score") else None,
            "cost_efficiency_score": float(r.get("cost_efficiency_score") or 0) if r.get("cost_efficiency_score") else None,
            "integrations_score": float(r.get("integrations_score") or 0) if r.get("integrations_score") else None,
            "data_control_score": float(r.get("data_control_score") or 0) if r.get("data_control_score") else None,
            "learning_curve_score": float(r.get("learning_curve_score") or 0) if r.get("learning_curve_score") else None,
            "longevity_score": float(r.get("longevity_score") or 0) if r.get("longevity_score") else None,
            "total_score": float(r.get("total_score") or 0) if r.get("total_score") else None,
        }

        if obj:
            for k, v in fields.items():
                setattr(obj, k, v)
            updated += 1
        else:
            db.add(Tool(tool_id=tool_id, **fields))
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "total_processed": len(rows)}
