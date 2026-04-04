"""
PHASE 6: Resume Parsing Engine
Converts raw resume → structured, reliable data
"""

import re
from pathlib import Path
from typing import Optional

from .extraction import extract_text, _extract_from_pdf, _extract_from_docx
from .sections import detect_sections, get_section_details, SECTION_KEYWORDS
from .skills import extract_skills
from ..utils.logger import logger, safe_execute, SafeOperation, create_safe_response


class ResumeParsedData:
    """Structured resume data output"""
    
    def __init__(self):
        self.raw_text: str = ""
        self.skills: list = []
        self.skill_categories: dict = {}
        self.experience: str = ""
        self.education: str = ""
        self.projects: str = ""
        self.sections_detected: dict = {}
        self.section_details: dict = {}
        self.skill_frequency: dict = {}
        self.missing_skills: dict = {}
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "raw_text": self.raw_text[:500],  # Limit to first 500 chars
            "skills": self.skills,
            "skill_categories": self.skill_categories,
            "experience": self.experience[:500] if self.experience else "",
            "education": self.education[:500] if self.education else "",
            "projects": self.projects[:500] if self.projects else "",
            "sections_detected": self.sections_detected,
            "section_details": self.section_details,
            "skill_frequency": dict(list(self.skill_frequency.items())[:10]),
            "missing_skills": {k: v[:5] for k, v in self.missing_skills.items()},
        }


def _extract_section_text(text: str, section_name: str) -> str:
    """Extract text for a specific section using regex patterns"""
    keywords = SECTION_KEYWORDS.get(section_name, [])
    if not keywords:
        return ""
    
    # Build regex pattern for section header
    keywords_pattern = "|".join(re.escape(kw) for kw in keywords)
    pattern = rf"(?i)({keywords_pattern})[\s\S]*?(?=(?:{keywords_pattern})|$)"
    
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        # Try to extract text after the section keyword
        section_pattern = rf"(?i)({keywords_pattern})\s*\n([\s\S]*?)(?=\n(?:{keywords_pattern})|$)"
        match = re.search(section_pattern, text, re.IGNORECASE)
        if match:
            return match.group(2).strip()
    
    return ""


def _normalize_text(text: str, preserve_format: bool = False) -> str:
    """
    Normalize resume text while preserving structure if needed
    """
    if not preserve_format:
        # Basic cleaning: lowercase, remove special chars
        text = text.lower()
        text = re.sub(r"[^\w\s\.\,\-\@\:]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
    else:
        # Preserve some structure
        text = re.sub(r"\s+", " ", text).strip()
    
    return text


def _extract_experience_section(text: str) -> str:
    """Extract and structure experience section"""
    section_text = _extract_section_text(text, "Experience")
    if not section_text:
        return ""
    
    # Extract bullet points or job entries
    lines = section_text.split('\n')
    experiences = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:  # Filter out very short lines
            experiences.append(line)
    
    return " ".join(experiences[:3])  # Top 3 experiences


def _extract_education_section(text: str) -> str:
    """Extract and structure education section"""
    section_text = _extract_section_text(text, "Education")
    if not section_text:
        return ""
    
    # Look for degree keywords
    degree_keywords = [
        "bachelor", "master", "phd", "diploma", "btech", "mtech",
        "bca", "mca", "bsc", "msc", "mba"
    ]
    
    lines = section_text.split('\n')
    degrees = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in degree_keywords):
            degrees.append(line.strip())
    
    return " ".join(degrees[:2])  # Top 2 degrees


def _extract_projects_section(text: str) -> str:
    """Extract and structure projects section"""
    section_text = _extract_section_text(text, "Projects")
    if not section_text:
        return ""
    
    lines = section_text.split('\n')
    projects = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:
            projects.append(line)
    
    return " ".join(projects[:2])  # Top 2 projects


def parse_resume(file_path: str) -> ResumeParsedData:
    """
    MAIN PHASE 6 FUNCTION
    Parse complete resume file and return structured data

    Args:
        file_path: Path to PDF or DOCX file

    Returns:
        ResumeParsedData with all extracted and normalized information
    """
    import time
    start_time = time.time()
    logger.info(f"Starting resume parsing for file: {Path(file_path).name}")

    parsed = ResumeParsedData()

    with SafeOperation("text_extraction"):
        # Step 1: Extract raw text
        raw_text = safe_execute(
            "text_extraction",
            extract_text,
            file_path,
            fallback_value=""
        )
        parsed.raw_text = raw_text

        if not raw_text or len(raw_text.strip()) < 10:
            logger.warning(f"Very little text extracted from {file_path}")
            return parsed

    with SafeOperation("section_detection"):
        # Step 2: Detect sections
        sections_detected = safe_execute(
            "section_detection",
            detect_sections,
            raw_text,
            fallback_value={}
        )
        parsed.sections_detected = sections_detected

        section_details = safe_execute(
            "section_details_extraction",
            get_section_details,
            raw_text,
            fallback_value={}
        )
        parsed.section_details = section_details

    with SafeOperation("skill_extraction"):
        # Step 3: Extract skills
        skill_result = safe_execute(
            "skill_extraction",
            extract_skills,
            raw_text,
            fallback_value=([], {}, {}, {})
        )

        if isinstance(skill_result, tuple) and len(skill_result) == 4:
            parsed.skills = skill_result[0]
            parsed.skill_categories = skill_result[1]
            parsed.skill_frequency = skill_result[2]
            parsed.missing_skills = skill_result[3]
        else:
            logger.warning("Skill extraction returned unexpected format")

    with SafeOperation("section_content_extraction"):
        # Step 4: Extract specific sections
        parsed.experience = safe_execute(
            "experience_extraction",
            _extract_experience_section,
            raw_text,
            fallback_value=""
        )

        parsed.education = safe_execute(
            "education_extraction",
            _extract_education_section,
            raw_text,
            fallback_value=""
        )

        parsed.projects = safe_execute(
            "projects_extraction",
            _extract_projects_section,
            raw_text,
            fallback_value=""
        )

    duration = time.time() - start_time
    logger.info(f"Resume parsing completed in {duration:.2f}s")
    logger.info(f"Extracted {len(parsed.skills)} skills, {len(parsed.sections_detected)} sections detected")

    return parsed


def validate_parsed_resume(parsed: ResumeParsedData) -> dict:
    """
    Validate parsed resume and return quality metrics
    """
    issues = []
    warnings = []
    
    # Check for essential components
    if not parsed.skills or len(parsed.skills) < 3:
        issues.append("Very few skills detected")
    
    if not parsed.sections_detected.get("Experience"):
        warnings.append("Experience section not detected")
    
    if not parsed.sections_detected.get("Education"):
        warnings.append("Education section not detected")
    
    if len(parsed.raw_text.split()) < 100:
        issues.append("Resume seems too short")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "quality_score": max(0, 100 - len(issues) * 20 - len(warnings) * 10),
    }