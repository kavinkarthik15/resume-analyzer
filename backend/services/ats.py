import re


def _skill_score(skill_count: int) -> int:
    if skill_count > 10:
        return 30
    if 5 <= skill_count <= 10:
        return 20
    return 10


def _section_score(sections: dict) -> int:
    score = 0
    for section_name in ["Education", "Experience", "Projects", "Skills", "Certifications"]:
        if sections.get(section_name, False):
            score += 5
    return score


def _keyword_score(total_frequency: int) -> int:
    if total_frequency > 15:
        return 20
    if 10 <= total_frequency <= 15:
        return 15
    if 5 <= total_frequency < 10:
        return 10
    return 5


def _format_score(text: str) -> int:
    score = 0

    if not re.search(r"[^a-z0-9\s]", text):
        score += 5

    if "  " not in text and text.strip() == text:
        score += 5

    words = text.split()
    if len(words) >= 100:
        score += 5

    return score


def _length_score(word_count: int) -> int:
    if 400 <= word_count <= 800:
        return 10
    if 200 <= word_count < 400:
        return 7
    if word_count > 800:
        return 10
    return 4


def calculate_ats_breakdown(text: str, skills: list, sections: dict, skill_frequency: dict) -> dict:
    """Return detailed ATS breakdown with per-category scores and max values."""
    word_count = len(text.split())
    total_frequency = sum(skill_frequency.values())

    breakdown = {
        "skill_score": {"score": _skill_score(len(skills)), "max": 30},
        "section_score": {"score": _section_score(sections), "max": 25},
        "keyword_score": {"score": _keyword_score(total_frequency), "max": 20},
        "format_score": {"score": _format_score(text), "max": 15},
        "length_score": {"score": _length_score(word_count), "max": 10},
    }

    total = sum(part["score"] for part in breakdown.values())
    breakdown["total"] = min(total, 100)
    return breakdown


def calculate_ats(text: str, skills: list, sections: dict, skill_frequency: dict) -> int:
    """
    Calculate ATS score out of 100 based on the Phase 1 rules.

    Args:
        text: cleaned resume text
        skills: list of detected skills
        sections: section detection dictionary
        skill_frequency: skill-frequency dictionary

    Returns:
        int: ATS score from 0 to 100
    """
    breakdown = calculate_ats_breakdown(text, skills, sections, skill_frequency)
    return breakdown["total"]
