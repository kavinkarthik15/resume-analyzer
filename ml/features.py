import re
from pathlib import Path

# Assuming services are available, but for ML, we might need to duplicate or import
# For now, placeholder functions

def extract_skills(text):
    # Placeholder - should import from backend.services.skills
    return [], {}, {}, {}

def detect_sections(text):
    # Placeholder
    return {}

def calculate_ats(text, skills, sections, skill_freq):
    # Placeholder
    return 0.0

def get_page_count(file_path, file_ext):
    # Placeholder
    return 1

def check_action_verbs(text, bullet_points):
    # Placeholder
    return {"strong_verb_count": 0}

def check_quantified_results(text):
    # Placeholder
    return {"metric_count": 0}

def extract_bullet_points(text):
    # Placeholder
    return []

def extract_experience_years(text: str) -> float:
    """Heuristic: look for patterns like '3 years', '5+ years', '2.5 years'."""
    matches = re.findall(r"(\d+\.?\d*)\s*\+?\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if matches:
        return max(float(m) for m in matches)
    return 0.0

def extract_ml_features(file_path: str, resume_text: str, jd_similarity: float = 0.0, important_sections=None):
    """Extract all 9 ML features from a resume file + text."""
    if important_sections is None:
        important_sections = ["Education", "Experience", "Projects", "Skills", "Certifications",
                              "Summary", "Contact", "Awards", "Languages", "Volunteering"]

    # Skills
    skills_found, skill_categories, skill_frequency, _ = extract_skills(resume_text)
    skill_count = len(skills_found)

    # Sections
    sections = detect_sections(resume_text)
    found_count = sum(1 for s in important_sections if sections.get(s, False))
    section_score = round(found_count / len(important_sections), 3)

    # ATS
    ats_score = calculate_ats(resume_text, skills_found, sections, skill_frequency)

    # Pages
    file_ext = Path(file_path).suffix.lower().lstrip(".")
    pages = get_page_count(file_path, file_ext)

    # Action verbs
    bullet_points = extract_bullet_points(resume_text)
    verb_result = check_action_verbs(resume_text, bullet_points)
    action_verbs = verb_result.get("strong_verb_count", 0)

    # Achievements / quantified results
    quant_result = check_quantified_results(resume_text)
    achievements = quant_result.get("metric_count", 0)

    # Experience years
    experience_years = extract_experience_years(resume_text)

    # Matched role skills (use skill_count as proxy when no JD provided)
    matched_role_skills = skill_count  # will be overridden if JD comparison is used

    return {
        "skill_count": skill_count,
        "matched_role_skills": matched_role_skills,
        "ats_score": float(ats_score),
        "jd_similarity": jd_similarity,
        "experience_years": round(experience_years, 1),
        "action_verbs": action_verbs,
        "achievements": achievements,
        "pages": pages,
        "section_score": section_score,
    }