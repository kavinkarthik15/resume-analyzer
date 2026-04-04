import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

from backend.services.ml_manager import FeatureEngineering

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = SCRIPT_DIR / "dataset.csv"

SKILL_POOL = [
    "Python", "JavaScript", "SQL", "AWS", "Docker", "React",
    "Java", "C#", "Node.js", "TensorFlow", "Kubernetes", "Excel",
    "Power BI", "Tableau", "Agile", "Leadership", "Communication"
]

SECTION_NAMES = [
    "Skills", "Experience", "Education", "Projects", "Summary",
    "Certifications", "Awards", "Volunteering", "Languages"
]

FORMAT_ISSUES = [
    "Inconsistent fonts", "Missing headings", "Bullet formatting problems",
    "Too many colors", "Poor spacing", "No contact section"
]

n_samples = 200

records = []
for _ in range(n_samples):
    skill_count = np.random.randint(4, 18)
    selected_skills = random.sample(SKILL_POOL, min(skill_count, len(SKILL_POOL)))
    skill_categories = {
        category: True
        for category in random.sample(
            ["Languages", "Frameworks", "Tools", "Cloud", "Methodologies", "Soft Skills"],
            k=random.randint(1, 5)
        )
    }
    sections_detected = {
        section: bool(np.random.rand() > 0.2)
        for section in SECTION_NAMES
    }

    if np.random.rand() > 0.3:
        sections_detected["Skills"] = True
    if np.random.rand() > 0.3:
        sections_detected["Experience"] = True
    if np.random.rand() > 0.4:
        sections_detected["Education"] = True

    formatting_issue_count = max(0, int(np.random.normal(1.2, 1.1)))
    formatting_issues = random.sample(FORMAT_ISSUES, min(formatting_issue_count, len(FORMAT_ISSUES)))

    analysis_data = {
        "ats_score": float(np.clip(np.random.normal(65, 18), 20, 100)),
        "skills_found": selected_skills,
        "skill_categories": skill_categories,
        "sections_detected": sections_detected,
        "breakdown": {
            "experience": float(np.clip(np.random.normal(18, 7), 0, 30)),
            "keywords": float(np.clip(np.random.normal(18, 8), 0, 30)),
            "format": float(np.clip(np.random.normal(14, 5), 0, 20)),
        },
        "jd_comparison": {
            "jd_match_score": float(np.round(np.clip(np.random.normal(0.6, 0.25), 0.0, 1.0) * 100, 1))
        },
        "formatting_issues": formatting_issues,
        "action_verbs": int(np.clip(np.random.normal(10, 6), 0, 20)),
        "achievements": int(np.clip(np.random.normal(4, 3), 0, 10)),
        "raw_text": "word " * int(np.clip(np.random.normal(380, 120), 120, 620)),
        "missing_skills": {
            "technical": random.sample(["Python", "SQL", "React", "AWS"], k=np.random.randint(0, 3))
        }
    }

    features = FeatureEngineering.engineer_features(analysis_data)
    shortlist_score = (
        features["ats_score_normalized"] * 0.24
        + features["skill_coverage_normalized"] * 0.18
        + features["jd_match_score"] * 0.18
        + features["essential_sections_completeness"] * 0.14
        + features["bullet_quality_score"] * 0.12
        + features["formatting_quality_score"] * 0.08
        + features["content_length"] * 0.06
        - features["missing_skills_penalty"] * 0.08
    )
    shortlist_score += np.random.normal(0, 0.04)

    features["shortlist_score"] = float(shortlist_score)
    records.append(features)

scores = np.array([record["shortlist_score"] for record in records])
threshold = float(np.percentile(scores, 60))
for record in records:
    record["shortlisted"] = int(record["shortlist_score"] > threshold)
    del record["shortlist_score"]

feature_names = list(records[0].keys()) if records else []
df = pd.DataFrame(records, columns=feature_names)
df.to_csv(OUTPUT_CSV, index=False)

print(f"Generated dataset with {len(df)} samples")
print(f"Positive labels: {df['shortlisted'].sum()}, Negative labels: {(len(df) - df['shortlisted'].sum())}")
print(f"Saved dataset to: {OUTPUT_CSV}")
