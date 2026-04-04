import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# ML Model path
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "random_forest_model.pkl"

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# ML Feature columns (must match training order)
ML_FEATURE_COLUMNS = [
    "skill_count", "matched_role_skills", "ats_score", "jd_similarity",
    "experience_years", "action_verbs", "achievements", "pages", "section_score"
]

# Important sections for scoring
IMPORTANT_SECTIONS = ["Education", "Experience", "Projects", "Skills", "Certifications",
                      "Summary", "Contact", "Awards", "Languages", "Volunteering"]