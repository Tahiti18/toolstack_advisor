import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

# Resolve to /backend/data/questionnaire_sample.json (two levels up from /backend/app/routes)
DATA_PATH = (Path(__file__).resolve().parents[2] / "backend" / "data" / "questionnaire_sample.json")

@router.get("/questionnaire")
def get_questionnaire():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
