from .ats import calculate_ats, calculate_ats_breakdown
from .extraction import extract_text
from .sections import detect_sections
from .skills import extract_skills, SKILL_DATABASE


def _to_title(skills: list[str]) -> list[str]:
    return [skill.title() for skill in skills]


def _build_suggestions(skills: list[str], sections: dict, text: str) -> list[str]:
    suggestions = []

    if not sections.get("Projects", False):
        suggestions.append("Add projects section")

    if len(skills) < 8:
        suggestions.append("Add more relevant skills")

    word_count = len(text.split())
    if word_count < 200:
        suggestions.append("Increase resume length (target at least 200 words)")

    if not sections.get("Certifications", False):
        suggestions.append("Include certifications if available")

    if not suggestions:
        suggestions.append("Resume looks good. Fine-tune keywords for your target role.")

    return suggestions


def analyze_resume(file_path: str) -> dict:
    """
    Main Phase 1 function.

    Steps:
    1) Extract and clean resume text
    2) Extract skills and categories
    3) Detect sections
    4) Calculate ATS score
    5) Build suggestions
    """
    text = extract_text(file_path)
    skills_found, skill_categories, skill_frequency, missing_skills = extract_skills(text)
    sections = detect_sections(text)
    ats_score = calculate_ats(text, skills_found, sections, skill_frequency)
    score_breakdown = calculate_ats_breakdown(text, skills_found, sections, skill_frequency)
    suggestions = _build_suggestions(skills_found, sections, text)

    # Calculate skill percentage per category
    skill_percentage = {}
    for category, category_skills in SKILL_DATABASE.items():
        found_count = len([s for s in category_skills if s in [sf.lower() for sf in skills_found]])
        total_count = len(category_skills)
        skill_percentage[category] = round((found_count / total_count) * 100) if total_count > 0 else 0

    # Overall skill coverage
    total_all = sum(len(v) for v in SKILL_DATABASE.values())
    found_all = len(skills_found)
    overall_skill_pct = round((found_all / total_all) * 100) if total_all > 0 else 0

    result = {
        "ats_score": ats_score,
        "skills_found": _to_title(skills_found),
        "skill_categories": {
            category: _to_title(skill_list) for category, skill_list in skill_categories.items()
        },
        "skill_frequency": {skill.title(): count for skill, count in skill_frequency.items()},
        "missing_skills": {
            category: _to_title(skill_list) for category, skill_list in missing_skills.items()
        },
        "skill_percentage": skill_percentage,
        "overall_skill_percentage": overall_skill_pct,
        "sections": {name: ("Found" if found else "Missing") for name, found in sections.items()},
        "score_breakdown": score_breakdown,
        "suggestions": suggestions,
    }

    return result


def format_analysis(result: dict) -> str:
    """Create a readable report string from analyze_resume output."""
    lines = [f"ATS SCORE: {result['ats_score']}/100", ""]

    lines.append("Skills Found:")
    if result["skills_found"]:
        lines.extend(result["skills_found"])
    else:
        lines.append("No skills detected")

    lines.append("")
    lines.append("Skill Categories:")
    if result["skill_categories"]:
        for category, skills in result["skill_categories"].items():
            lines.append(f"{category}: {', '.join(skills)}")
    else:
        lines.append("No skill categories matched")

    lines.append("")
    lines.append("Sections:")
    for section_name, status in result["sections"].items():
        lines.append(f"{section_name}: {status}")

    lines.append("")
    lines.append("Suggestions:")
    lines.extend(result["suggestions"])

    return "\n".join(lines)
