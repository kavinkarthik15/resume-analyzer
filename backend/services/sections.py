import re

SECTION_KEYWORDS = {
    "Education": [
        "education", "degree", "bachelor", "btech", "b.tech", "b.e", "m.tech",
        "college", "university", "cgpa", "gpa", "master", "phd", "diploma",
        "school", "academic", "coursework", "graduation", "mba", "mca",
        "bca", "bsc", "msc", "b.sc", "m.sc",
    ],
    "Experience": [
        "experience", "internship", "company", "work", "employment",
        "professional experience", "work experience", "job", "employer",
        "role", "position", "tenure", "worked at", "intern",
    ],
    "Projects": [
        "project", "developed", "created", "built", "designed",
        "personal project", "academic project", "side project",
        "capstone", "portfolio", "implemented", "mini project",
    ],
    "Skills": [
        "skills", "technical skills", "tools", "technologies",
        "programming languages", "frameworks", "competencies",
        "proficiency", "expertise", "tech stack", "core skills",
    ],
    "Certifications": [
        "certification", "certifications", "certificate", "certified",
        "credential", "license", "accreditation", "coursera", "udemy",
        "aws certified", "google certified",
    ],
    "Summary": [
        "summary", "objective", "about me", "profile", "career objective",
        "professional summary", "personal statement", "overview",
    ],
    "Contact": [
        "email", "phone", "linkedin", "github", "portfolio",
        "contact", "address", "mobile",
    ],
    "Awards": [
        "awards", "honors", "achievements", "recognition",
        "accomplishments", "scholarship",
    ],
    "Languages": [
        "languages", "fluent", "proficient in", "native speaker",
        "english", "hindi", "french", "spanish",
    ],
    "Volunteering": [
        "volunteer", "volunteering", "community service", "social work",
        "ngo", "non-profit",
    ],
}


def _keyword_exists(text: str, keyword: str) -> bool:
    pattern = rf"\b{re.escape(keyword)}\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def detect_sections(text: str):
    """
    Detect section availability in the resume using keyword matching.

    Returns:
        dict[str, bool] where True means section found.
    """
    sections_dictionary = {}

    for section_name, keywords in SECTION_KEYWORDS.items():
        found = any(_keyword_exists(text, keyword) for keyword in keywords)
        sections_dictionary[section_name] = found

    return sections_dictionary


def get_section_details(text: str) -> dict:
    """
    Get detailed section info with match count and confidence.

    Returns:
        dict with section name -> {found, match_count, confidence}
    """
    details = {}

    for section_name, keywords in SECTION_KEYWORDS.items():
        matched_keywords = [kw for kw in keywords if _keyword_exists(text, kw)]
        match_count = len(matched_keywords)
        found = match_count > 0

        if match_count >= 3:
            confidence = "High"
        elif match_count >= 1:
            confidence = "Medium"
        else:
            confidence = "None"

        details[section_name] = {
            "found": found,
            "match_count": match_count,
            "confidence": confidence,
            "matched_keywords": matched_keywords[:5],
        }

    return details
