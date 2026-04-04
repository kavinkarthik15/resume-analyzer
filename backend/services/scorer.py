"""
PHASE 7: ATS Scoring System (LOGIC LAYER)
Generate meaningful, explainable scores
"""

import re
from typing import Optional, List

from ..utils.logger import logger, safe_execute, SafeOperation


class ATSScoreBreakdown:
    
    def __init__(self):
        self.keyword_match: int = 0  # 30%
        self.section_completeness: int = 0  # 20%
        self.formatting_score: int = 0  # 20%
        self.experience_relevance: int = 0  # 30%
        self.total_score: int = 0
        self.missing_skills: List[str] = []
        self.missing_sections: List[str] = []
        self.formatting_issues: List[str] = []
        
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "ats_score": self.total_score,
            "breakdown": {
                "keywords": self.keyword_match,
                "sections": self.section_completeness,
                "format": self.formatting_score,
                "experience": self.experience_relevance,
            },
            "missing_skills": self.missing_skills[:5],
            "missing_sections": self.missing_sections,
            "formatting_issues": self.formatting_issues,
        }


STRONG_ACTION_VERBS = {
    "achieved", "built", "created", "designed", "developed", "directed",
    "discovered", "eliminated", "established", "expanded", "generated",
    "improved", "increased", "initiated", "implemented", "invented",
    "led", "launched", "optimized", "organized", "pioneered",
    "produced", "reduced", "restructured", "streamlined", "transformed",
    "accelerated", "coordinated", "enhanced", "facilitated", "formulated",
    "influenced", "managed", "modernized", "partnered", "promoted",
    "revamped", "scaled", "simplified", "spearheaded", "strengthened",
}

QUANTIFIABLE_PATTERNS = [
    r"\d+%",  # Percentages
    r"\$[\d,]+",  # Money
    r"\d+\s*(?:hours?|days?|weeks?|months?|years?)",  # Time
    r"\d+x",  # Multipliers
    r"top\s+\d+",  # Rankings
]

IMPORTANT_SECTIONS = [
    "Skills", "Experience", "Education", "Projects", "Certifications",
    "Summary", "Contact", "Awards", "Languages"
]


def _calculate_keyword_match(resume_text: str, skills_found: List[str], 
                             skill_frequency: dict) -> int:
    """
    Component 1: Keyword Match (30%)
    Match resume skills and count frequency
    """
    if not skills_found:
        return 0
    
    total_skill_occurrences = sum(skill_frequency.values())
    
    # Score based on skill count and frequency
    skill_score = min(len(skills_found) * 2, 20)  # Max 20
    frequency_score = min(total_skill_occurrences, 10)  # Max 10
    
    return min(skill_score + frequency_score, 30)


def _calculate_section_completeness(sections_detected: dict) -> int:
    """
    Component 2: Section Completeness (20%)
    Check if all important sections exist
    """
    found_count = sum(1 for section in IMPORTANT_SECTIONS 
                     if sections_detected.get(section, False))
    
    # 5 points per essential section
    essential_sections = ["Skills", "Experience", "Education"]
    essential_found = sum(1 for section in essential_sections 
                         if sections_detected.get(section, False))
    
    essential_score = essential_found * 6  # Max 18
    other_score = min((found_count - essential_found) * 1, 2)  # Max 2
    
    return min(essential_score + other_score, 20)


def _calculate_formatting_score(resume_text: str) -> tuple[int, List[str]]:
    """
    Component 3: Formatting Score (20%)
    Check for proper formatting and structure
    """
    issues = []
    score = 20  # Start with max
    
    # Check for bullet points
    bullet_count = len(re.findall(r"[-•·]", resume_text))
    if bullet_count < 5:
        issues.append("Few bullet points - use bullets for better formatting")
        score -= 5
    else:
        pass  # Good use of bullets
    
    # Check for excessive length
    word_count = len(resume_text.split())
    if word_count < 200:
        issues.append("Resume too short - should be 250-500 words minimum")
        score -= 5
    elif word_count > 1000:
        issues.append("Resume too long - keep under 1000 words")
        score -= 3
    
    # Check for clean structure (no excessive special characters that indicate poor formatting)
    special_char_ratio = len(re.findall(r"[^a-zA-Z0-9\s\.,-]", resume_text)) / max(len(resume_text), 1)
    if special_char_ratio > 0.15:
        issues.append("Too many special characters - clean up formatting")
        score -= 5
    
    # Check for proper spacing
    if re.search(r"\n\n\n+", resume_text):  # Multiple blank lines
        issues.append("Inconsistent spacing - use consistent formatting")
        score -= 3
    
    return max(score, 0), issues


def _calculate_experience_relevance(resume_text: str, skill_frequency: dict) -> tuple[int, List[str]]:
    """
    Component 4: Experience Relevance (30%)
    Check for strong action verbs and quantifiable achievements
    """
    issues = []
    score = 0
    
    # Action verbs score (15 points max)
    action_verb_count = 0
    text_lower = resume_text.lower()
    
    for verb in STRONG_ACTION_VERBS:
        action_verb_count += len(re.findall(rf"\b{verb}\b", text_lower))
    
    verb_score = min(action_verb_count * 1.5, 15)
    score += verb_score
    
    if action_verb_count < 5:
        issues.append("Use more action verbs (achieved, built, created, etc.)")
    
    # Quantifiable results score (15 points max)
    quantifiable_count = 0
    for pattern in QUANTIFIABLE_PATTERNS:
        quantifiable_count += len(re.findall(pattern, resume_text, re.IGNORECASE))
    
    quant_score = min(quantifiable_count * 2, 15)
    score += quant_score
    
    if quantifiable_count < 3:
        issues.append("Add quantifiable metrics (%, $, numbers) to achievements")
    
    return min(score, 30), issues


def calculate_ats_score(resume_text: str, skills_found: List[str],
                       skill_frequency: dict, sections_detected: dict) -> ATSScoreBreakdown:
    """
    PHASE 7 MAIN FUNCTION
    Calculate comprehensive ATS score with all components
    """
    import time
    start_time = time.time()
    logger.info("Starting ATS score calculation")

    breakdown = ATSScoreBreakdown()

    with SafeOperation("keyword_match_calculation"):
        # Component 1: Keyword Match (30%)
        breakdown.keyword_match = safe_execute(
            "keyword_match",
            _calculate_keyword_match,
            resume_text, skills_found, skill_frequency,
            fallback_value=15  # Default middle score
        )
        logger.info(f"Keyword match score: {breakdown.keyword_match}/30")

    with SafeOperation("section_completeness_calculation"):
        # Component 2: Section Completeness (20%)
        breakdown.section_completeness = safe_execute(
            "section_completeness",
            _calculate_section_completeness,
            sections_detected,
            fallback_value=10  # Default middle score
        )
        logger.info(f"Section completeness score: {breakdown.section_completeness}/20")

        # Identify missing sections
        breakdown.missing_sections = safe_execute(
            "missing_sections_identification",
            lambda: [s for s in IMPORTANT_SECTIONS if not sections_detected.get(s, False)],
            fallback_value=[]
        )

    with SafeOperation("formatting_score_calculation"):
        # Component 3: Formatting Score (20%)
        formatting_result = safe_execute(
            "formatting_analysis",
            _calculate_formatting_score,
            resume_text,
            fallback_value=(10, ["Formatting analysis failed"])
        )

        if isinstance(formatting_result, tuple) and len(formatting_result) == 2:
            breakdown.formatting_score = formatting_result[0]
            breakdown.formatting_issues = formatting_result[1]
        else:
            breakdown.formatting_score = 10
            breakdown.formatting_issues = ["Formatting analysis failed"]

        logger.info(f"Formatting score: {breakdown.formatting_score}/20")

    with SafeOperation("experience_relevance_calculation"):
        # Component 4: Experience Relevance (30%)
        experience_result = safe_execute(
            "experience_relevance",
            _calculate_experience_relevance,
            resume_text, skill_frequency,
            fallback_value=(15, ["Experience analysis failed"])
        )

        if isinstance(experience_result, tuple) and len(experience_result) == 2:
            breakdown.experience_relevance = experience_result[0]
            breakdown.formatting_issues.extend(experience_result[1])
        else:
            breakdown.experience_relevance = 15
            breakdown.formatting_issues.append("Experience analysis failed")

        logger.info(f"Experience relevance score: {breakdown.experience_relevance}/30")

    # Calculate total weighted score
    breakdown.total_score = (
        breakdown.keyword_match +  # 30% weighted included
        breakdown.section_completeness +  # 20%
        breakdown.formatting_score +  # 20%
        breakdown.experience_relevance  # 30%
    )

    # Cap at 100
    breakdown.total_score = min(breakdown.total_score, 100)

    duration = time.time() - start_time
    logger.info(f"ATS scoring completed in {duration:.2f}s - Final Score: {breakdown.total_score}/100")

    return breakdown


def get_ats_improvement_tips(breakdown: ATSScoreBreakdown) -> List[str]:
    """
    Generate specific improvement tips based on ATS breakdown
    """
    tips = []
    
    if breakdown.keyword_match < 20:
        tips.append("Add more relevant technical skills to match job requirements")
    
    if breakdown.section_completeness < 15:
        tips.append("Include all important sections: Skills, Experience, Education")
    
    if breakdown.formatting_issues:
        tips.extend(breakdown.formatting_issues[:3])
    
    if breakdown.experience_relevance < 20:
        tips.append("Use more action verbs and quantifiable achievements")
    
    return tips