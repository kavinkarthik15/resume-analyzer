from typing import Dict, Any


ROLE_PROFILES: Dict[str, Dict[str, Any]] = {
    "frontend": {
        "skills": ["react", "javascript", "css", "html", "ui"],
        "weights": {
            "skills": 0.5,
            "keywords": 0.2,
            "experience": 0.1,
            "quality": 0.1,
            "format": 0.1,
        },
    },
    "backend": {
        "skills": ["node", "python", "java", "sql", "api", "database"],
        "weights": {
            "skills": 0.45,
            "keywords": 0.2,
            "experience": 0.15,
            "quality": 0.1,
            "format": 0.1,
        },
    },
    "data": {
        "skills": ["python", "machine learning", "pandas", "sql", "statistics"],
        "weights": {
            "skills": 0.5,
            "keywords": 0.2,
            "experience": 0.15,
            "quality": 0.1,
            "format": 0.05,
        },
    },
    "general": {
        "skills": ["communication", "problem solving"],
        "weights": {
            "skills": 0.4,
            "keywords": 0.2,
            "experience": 0.15,
            "quality": 0.15,
            "format": 0.1,
        },
    },
}


def detect_role(role_name: str) -> str:
    role_name = (role_name or "").lower()

    if "front" in role_name or "ui" in role_name:
        return "frontend"
    if "back" in role_name or "api" in role_name:
        return "backend"
    if "data" in role_name or "ml" in role_name or "analyst" in role_name:
        return "data"
    return "general"


def get_role_profile(role_type: str) -> Dict[str, Any]:
    return ROLE_PROFILES.get(role_type, ROLE_PROFILES["general"])


def detect_experience_level(exp_text: str) -> str:
    text = (exp_text or "").lower()

    if "fresher" in text or "entry" in text or "intern" in text:
        return "junior"

    if "senior" in text or "lead" in text or "principal" in text or "staff" in text:
        return "senior"

    if any(token in text for token in ["0", "1"]):
        return "junior"
    if any(token in text for token in ["2", "3", "4"]):
        return "mid"
    if any(token in text for token in ["5", "6", "7", "8", "9"]):
        return "senior"

    return "mid"


def extract_experience_signals(resume_text: str) -> Dict[str, Any]:
    text = (resume_text or "").lower()

    return {
        "has_projects": "project" in text,
        "has_numbers": any(char.isdigit() for char in text),
        "has_experience_section": "experience" in text,
        "has_leadership": any(word in text for word in ["led", "managed", "mentor", "owned", "owner"]),
        "word_count": len(text.split()),
    }


def experience_level_score(level: str, signals: Dict[str, Any]) -> int:
    score = 0

    if level == "junior":
        if signals.get("has_projects"):
            score += 40
        if signals.get("has_numbers"):
            score += 20
        if signals.get("word_count", 0) > 200:
            score += 20
        if signals.get("has_experience_section"):
            score += 20

    elif level == "mid":
        if signals.get("has_projects"):
            score += 25
        if signals.get("has_numbers"):
            score += 30
        if signals.get("has_experience_section"):
            score += 25
        if signals.get("word_count", 0) > 300:
            score += 20

    elif level == "senior":
        if signals.get("has_leadership"):
            score += 30
        if signals.get("has_numbers"):
            score += 30
        if signals.get("has_experience_section"):
            score += 20
        if signals.get("word_count", 0) > 400:
            score += 20

    return min(score, 100)