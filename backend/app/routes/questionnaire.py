# backend/app/routes/questionnaire.py
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

# File actually lives at: backend/data/questionnaire_sample.json
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "questionnaire_sample.json"

@router.get("/questionnaire")
def get_questionnaire():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
