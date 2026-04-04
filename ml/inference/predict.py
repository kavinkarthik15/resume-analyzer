import joblib
import pandas as pd
from pathlib import Path

from .features import extract_ml_features

# Load model
MODEL_PATH = Path(__file__).parent / "models" / "random_forest_model.pkl"
FEATURE_COLUMNS = [
    "skill_count", "matched_role_skills", "ats_score", "jd_similarity",
    "experience_years", "action_verbs", "achievements", "pages", "section_score"
]

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print("Warning: ML model not found. Please train the model first.")

def predict_shortlist_probability(features: dict) -> float:
    """Predict shortlist probability from features dict."""
    if model is None:
        raise RuntimeError("ML model not loaded")

    input_data = pd.DataFrame([list(features.values())], columns=FEATURE_COLUMNS)
    probability = model.predict_proba(input_data)[0][1]
    return float(probability)

def predict_shortlist_decision(features: dict) -> str:
    """Predict shortlist decision."""
    prob = predict_shortlist_probability(features)
    return "Shortlisted" if prob > 0.5 else "Rejected"

def predict_from_resume(file_path: str, resume_text: str, jd_similarity: float = 0.0):
    """Full prediction from resume file and text."""
    features = extract_ml_features(file_path, resume_text, jd_similarity)
    prob = predict_shortlist_probability(features)
    decision = "Shortlisted" if prob > 0.5 else "Rejected"
    return {
        "probability": round(prob, 2),
        "decision": decision,
        "features": features
    }