import json, os
from fastapi import APIRouter

router = APIRouter()

@router.get("/questionnaire")
def get_questionnaire():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "questionnaire_sample.json")
    with open(path, "r") as f:
        return json.load(f)
