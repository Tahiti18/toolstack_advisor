import json, os

DEFAULT_WEIGHTS = {
    "accuracy_score": 1.0,
    "speed_score": 1.0,
    "cost_efficiency_score": 1.2,
    "integrations_score": 1.1,
    "data_control_score": 1.0,
    "learning_curve_score": 0.8,
    "longevity_score": 0.9,
}

def load_weights():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "scoring_weights_default.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_WEIGHTS

def score_row(row, weights=None):
    w = weights or DEFAULT_WEIGHTS
    total = 0.0
    for k, mult in w.items():
        total += float(getattr(row, k, 0) or 0) * float(mult)
    return round(total, 3)
