import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "random_forest_model.pkl"

model = joblib.load(MODEL_PATH)
print(f"Loaded model from {MODEL_PATH}")

feature_names = [
    "ats_score_normalized",
    "skill_count",
    "skill_coverage_normalized",
    "skill_diversity",
    "skill_diversity_normalized",
    "sections_completeness",
    "section_completeness_score",
    "essential_sections_completeness",
    "experience_relevance_score",
    "keyword_match_score",
    "jd_match_score",
    "formatting_quality_score",
    "formatting_issues_count",
    "bullet_verb_score",
    "bullet_achievement_score",
    "bullet_quality_score",
    "content_length",
    "word_count",
    "missing_skills_count",
    "missing_skills_penalty",
    "overall_quality_score",
    "readiness_score",
]

example_cases = [
    {
        "label": "Strong Resume",
        "features": [0.92, 14, 0.88, 5, 0.85, 1.0, 0.96, 1.0, 0.9, 0.85, 0.92, 0.9, 0.0, 0.88, 0.95, 0.9, 0.85, 520, 0, 0.0, 0.88, 0.9],
    },
    {
        "label": "Weak Resume",
        "features": [0.35, 3, 0.25, 1, 0.2, 0.5, 0.45, 0.33, 0.2, 0.25, 0.28, 0.35, 0.3, 0.4, 0.8, 0.3, 0.4, 180, 2, 0.5, 0.34, 0.27],
    },
    {
        "label": "Needs Tailoring",
        "features": [0.72, 10, 0.65, 4, 0.6, 0.9, 0.82, 0.8, 0.75, 0.55, 0.35, 0.7, 0.68, 0.75, 0.2, 0.7, 0.75, 420, 1, 0.2, 0.69, 0.61],
    },
]

print(f"{'Label':<20} {'Probability':>12} {'Decision':>10}")
print('-' * 44)
for case in example_cases:
    prob = model.predict_proba([case['features']])[0][1]
    decision = 'Shortlisted' if prob > 0.5 else 'Rejected'
    print(f"{case['label']:<20} {prob:>11.2f} {decision:>10}")
