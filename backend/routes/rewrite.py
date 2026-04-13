"""Resume rewrite routes with section-level compare payloads."""

import re
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.resume_rewriter import rewrite_bullet_points
from ..utils.logger import logger

router = APIRouter()


class RewriteRequest(BaseModel):
    text: str
    job_description: Optional[str] = None
    tone: Optional[str] = "professional"
    level: Optional[str] = "mid"
    industry: Optional[str] = "frontend"


SECTION_ORDER = ["summary", "experience", "projects", "skills"]
STRONG_ACTION_TERMS = {
    "developed",
    "engineered",
    "built",
    "designed",
    "implemented",
    "optimized",
    "led",
    "managed",
    "scaled",
    "launched",
    "delivered",
    "improved",
    "automated",
    "analyzed",
    "architected",
    "deployed",
    "collaborated",
    "reduced",
    "increased",
}
ATS_SIGNAL_TERMS = {
    "react",
    "python",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "api",
    "apis",
    "testing",
    "deployment",
    "integration",
    "automation",
    "performance",
    "optimization",
    "scalable",
    "scalability",
    "analysis",
    "analytics",
    "metrics",
    "leadership",
    "collaboration",
    "stakeholder",
    "stakeholders",
    "data",
    "design",
    "development",
}
WEAK_TERMS = {
    "worked",
    "helped",
    "did",
    "made",
    "handled",
    "assisted",
    "responsible",
    "involved",
    "tasked",
    "assigned",
}
TONE_MAP = {
    "professional": "Use formal, polished language",
    "direct": "Be concise and to the point",
    "confident": "Use strong, assertive language",
}
LEVEL_MAP = {
    "junior": "Focus on learning, projects, and foundational skills",
    "mid": "Highlight ownership, contributions, and measurable impact",
    "senior": "Emphasize leadership, strategy, and high-impact results",
}
INDUSTRY_MAP = {
    "frontend": "Focus on UI, performance, and user experience",
    "backend": "Focus on APIs, scalability, and system design",
    "data": "Focus on analysis, models, and data insights",
    "design": "Focus on UX, visual design, and user research",
}
INDUSTRY_CUE_WORDS = {
    "frontend": ["ui", "frontend", "react", "performance", "ux", "user"],
    "backend": ["api", "backend", "scalable", "system", "database", "service"],
    "data": ["data", "analysis", "model", "insight", "sql", "python"],
    "design": ["design", "ux", "visual", "prototype", "research", "usability"],
}


def _normalize_section_text(value: str) -> str:
    cleaned = re.sub(r"\n{3,}", "\n\n", value or "").strip()
    return cleaned


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", (text or "").lower())


def _unique_preserve_order(values: list[str]) -> list[str]:
    unique = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def _normalize_preset(value: Optional[str], allowed: dict, default: str) -> str:
    lowered = (value or default).lower()
    return lowered if lowered in allowed else default


def _append_phrase(text: str, phrase: str) -> str:
    if not text:
        return text
    base = text.strip().rstrip(".")
    return f"{base}, {phrase}."


def _apply_tone_level_industry(text: str, tone: str, level: str, industry: str) -> str:
    updated = (text or "").strip()
    if not updated:
        return ""

    lowered = updated.lower()

    if tone == "direct":
        updated = re.sub(r"\b(successfully|effectively|various|multiple|several|highly)\b", "", updated, flags=re.IGNORECASE)
        updated = re.sub(r"\butilized\b", "used", updated, flags=re.IGNORECASE)
        updated = re.sub(r"\s{2,}", " ", updated).strip()
    elif tone == "professional":
        updated = re.sub(r"\bused\b", "leveraged", updated, flags=re.IGNORECASE)
    elif tone == "confident":
        updated = re.sub(r"\bhelped\b", "drove", updated, flags=re.IGNORECASE)
        strong_starts = ("led", "built", "developed", "optimized", "architected", "drove")
        if not updated.lower().startswith(strong_starts):
            updated = f"Led {updated[0].lower() + updated[1:]}"

    updated_lower = updated.lower()
    if level == "junior" and "foundational" not in updated_lower and len(updated.split()) < 30:
        updated = _append_phrase(updated, "strengthening foundational skills")
    elif level == "mid" and "ownership" not in updated_lower and len(updated.split()) < 30:
        updated = _append_phrase(updated, "showing ownership and measurable impact")
    elif level == "senior" and "strategy" not in updated_lower and len(updated.split()) < 30:
        updated = _append_phrase(updated, "driving strategy and high-impact outcomes")

    cue_words = INDUSTRY_CUE_WORDS.get(industry, [])
    if cue_words and not any(word in updated.lower() for word in cue_words):
        industry_phrase = {
            "frontend": "with focus on UI performance and user experience",
            "backend": "with focus on APIs, scalability, and system design",
            "data": "with focus on data analysis, models, and actionable insights",
            "design": "with focus on UX, visual design, and user research",
        }.get(industry)
        if industry_phrase and len(updated.split()) < 34:
            updated = _append_phrase(updated, industry_phrase)

    return re.sub(r"\s{2,}", " ", updated).strip()


def _word_count(text: str) -> int:
    return len(_tokenize(text))


def _sentence_count(text: str) -> int:
    sentences = [segment.strip() for segment in re.split(r"[.!?]+", text or "") if segment.strip()]
    return max(len(sentences), 1)


def _quality_clarity(text: str) -> int:
    average_sentence_length = _word_count(text) / _sentence_count(text)
    return max(0, min(100, int(round(100 - (average_sentence_length * 2)))))


def _quality_ats(text: str) -> int:
    lowered = (text or "").lower()
    return 70 if "experience" in lowered else 50


def _quality_keywords(text: str, job_description: Optional[str] = None) -> int:
    if not job_description:
        return 50 if _tokenize(text) else 0

    text_tokens = set(_tokenize(text))
    jd_tokens = [token for token in _tokenize(job_description) if len(token) > 2]
    if not jd_tokens:
        return 0

    unique_jd_tokens = _unique_preserve_order(jd_tokens)
    matched_keywords = [token for token in unique_jd_tokens if token in text_tokens]
    return int(round((len(matched_keywords) / len(unique_jd_tokens)) * 100))


def _quality_action_strength(text: str) -> int:
    lowered = (text or "").lower()
    strong_verbs = ["led", "built", "developed", "optimized"]
    action = sum(1 for verb in strong_verbs if verb in lowered) * 10
    return min(action, 100)


def _compute_quality_metrics(original: str, rewritten: str, job_description: Optional[str] = None) -> dict:
    before = {
        "clarity": _quality_clarity(original),
        "ats": _quality_ats(original),
        "keywords": _quality_keywords(original, job_description),
        "action": _quality_action_strength(original),
    }
    after = {
        "clarity": _quality_clarity(rewritten),
        "ats": _quality_ats(rewritten),
        "keywords": _quality_keywords(rewritten, job_description),
        "action": _quality_action_strength(rewritten),
    }

    return {"before": before, "after": after}


def _extract_section_text(full_text: str, section_name: str) -> str:
    section_aliases = {
        "summary": ["summary", "professional summary", "profile", "objective"],
        "experience": ["experience", "work experience", "employment", "professional experience"],
        "projects": ["projects", "project experience"],
        "skills": ["skills", "technical skills", "core skills"],
    }

    labels = section_aliases.get(section_name, [section_name])
    heading_pattern = r"(?im)^\s*(?:" + "|".join(re.escape(label) for label in labels) + r")\s*:?\s*$"
    heading_match = re.search(heading_pattern, full_text)
    if not heading_match:
        return ""

    remaining_text = full_text[heading_match.end():]
    next_heading = re.search(r"(?im)^\s*[A-Z][A-Za-z\s/&-]{2,30}\s*:?\s*$", remaining_text)
    section_text = remaining_text[:next_heading.start()] if next_heading else remaining_text
    return _normalize_section_text(section_text)


def _extract_sections(full_text: str) -> dict:
    text = full_text or ""
    sections = {name: _extract_section_text(text, name) for name in SECTION_ORDER}

    if not sections["summary"]:
        first_block = text.split("\n\n", 1)[0].strip()
        sections["summary"] = _normalize_section_text(first_block)

    if not sections["skills"]:
        skill_lines = [line.strip() for line in text.splitlines() if "," in line and len(line) < 120]
        sections["skills"] = _normalize_section_text("\n".join(skill_lines[:3]))

    for name in SECTION_ORDER:
        sections[name] = _normalize_section_text(sections.get(name, ""))

    return sections


def _rewrite_free_text(text: str, tone: str, level: str, industry: str) -> tuple[str, dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "", {"changes": [], "why": [], "keywords_added": []}

    rewritten_rows = rewrite_bullet_points(lines, add_metrics_suggestions=True)
    rewritten_lines = []
    changes = []
    why = []
    keyword_pool: list[str] = []
    original_text = _normalize_section_text("\n".join(lines))
    rewritten_text = ""

    for row in rewritten_rows:
        original_line = row.get("original", "").strip()
        improved_line = row.get("improved", row.get("original", "")).strip()
        improved_line = _apply_tone_level_industry(improved_line, tone=tone, level=level, industry=industry)
        if original_line:
            rewritten_lines.append(f"- {improved_line}")

        original_terms = set(_tokenize(original_line))
        improved_terms = _tokenize(improved_line)
        if any(term in original_terms for term in WEAK_TERMS) and improved_line != original_line:
            changes.append("Replaced weak verbs with action verbs")
            why.append("Improves recruiter scan speed and makes achievements feel more direct")

        if len(improved_line.split()) < len(original_line.split()):
            changes.append("Shortened sentences for clarity")
            why.append("Keeps the section easier to skim on both ATS and recruiter review")

        if any(char.isdigit() for char in improved_line) and not any(char.isdigit() for char in original_line):
            changes.append("Added measurable impact cues")
            why.append("Quantified outcomes increase credibility and impact perception")

        keyword_pool.extend(
            term for term in improved_terms if term not in original_terms and (term in STRONG_ACTION_TERMS or term in ATS_SIGNAL_TERMS)
        )

    rewritten_text = _normalize_section_text("\n".join(line for line in rewritten_lines if line.strip("- ")))

    if original_text and rewritten_text and original_text != rewritten_text and not changes:
        changes.append("Refined the section for stronger ATS readability")
        why.append("Makes the section clearer and easier to compare during recruiter review")

    changes.extend(
        [
            f"Applied {tone} tone preset",
            f"Aligned messaging for {level} level",
            f"Adjusted emphasis for {industry} industry",
        ]
    )
    why.extend(
        [
            TONE_MAP.get(tone, ""),
            LEVEL_MAP.get(level, ""),
            INDUSTRY_MAP.get(industry, ""),
        ]
    )

    return rewritten_text, {
        "changes": _unique_preserve_order(changes),
        "why": _unique_preserve_order(why),
        "keywords_added": _unique_preserve_order(keyword_pool)[:6],
    }


def _rewrite_skills(
    text: str,
    job_description: Optional[str] = None,
    tone: str = "professional",
    level: str = "mid",
    industry: str = "frontend",
) -> tuple[str, dict]:
    if not text:
        return "", {"changes": [], "why": [], "keywords_added": []}

    cleaned = re.sub(r"\s+", " ", text.replace("\n", ", ")).strip().strip(",")
    raw_skills = [token.strip(" -•") for token in re.split(r",|\||/", cleaned) if token.strip()]
    unique_skills = []
    for skill in raw_skills:
        lowered = skill.lower()
        if lowered not in [item.lower() for item in unique_skills]:
            unique_skills.append(skill)

    industry_priority = {
        "frontend": ["react", "javascript", "typescript", "css", "html", "ui"],
        "backend": ["python", "java", "node", "api", "sql", "docker"],
        "data": ["python", "sql", "pandas", "machine", "analytics", "model"],
        "design": ["figma", "ux", "ui", "research", "prototype", "design"],
    }
    priorities = industry_priority.get(industry, [])
    unique_skills = sorted(
        unique_skills,
        key=lambda value: 0 if any(priority in value.lower() for priority in priorities) else 1,
    )

    original_tokens = set(_tokenize(text))
    rewritten_text = ", ".join(unique_skills)
    rewritten_tokens = _tokenize(rewritten_text)

    keywords_added = _unique_preserve_order(
        [token for token in rewritten_tokens if token not in original_tokens and (token in ATS_SIGNAL_TERMS or token in STRONG_ACTION_TERMS)]
    )

    if job_description:
        jd_tokens = set(_tokenize(job_description))
        keywords_added = _unique_preserve_order(keywords_added + [token for token in rewritten_tokens if token in jd_tokens])[:8]

    changes = ["Removed duplicate skills and normalized formatting"] if rewritten_text != text else []
    changes.append(f"Applied {industry} industry prioritization")
    why = ["Keeps high-signal keywords easy to scan for ATS and recruiters"] if rewritten_text != text else []
    why.extend(
        [
            TONE_MAP.get(tone, ""),
            LEVEL_MAP.get(level, ""),
            INDUSTRY_MAP.get(industry, ""),
        ]
    )

    return rewritten_text, {
        "changes": changes,
        "why": why,
        "keywords_added": keywords_added[:8],
    }


def build_section_rewrites(
    text: str,
    job_description: Optional[str] = None,
    tone: str = "professional",
    level: str = "mid",
    industry: str = "frontend",
) -> dict:
    tone = _normalize_preset(tone, TONE_MAP, "professional")
    level = _normalize_preset(level, LEVEL_MAP, "mid")
    industry = _normalize_preset(industry, INDUSTRY_MAP, "frontend")

    sections = _extract_sections(text)
    rewrites = {}

    for section in SECTION_ORDER:
        original = sections.get(section, "")
        if section == "skills":
            rewritten, explanation = _rewrite_skills(
                original,
                job_description=job_description,
                tone=tone,
                level=level,
                industry=industry,
            )
        else:
            rewritten, explanation = _rewrite_free_text(original, tone=tone, level=level, industry=industry)
        rewrites[section] = {
            "original": original,
            "rewritten": rewritten or original,
            "explanation": explanation,
            "quality": _compute_quality_metrics(original, rewritten or original, job_description=job_description),
        }

    return rewrites


@router.post("/rewrite")
async def rewrite_resume(request: RewriteRequest) -> dict:
    """Rewrite resume content and return section-wise compare payload."""
    text = request.text

    if not text or not text.strip():
        return {"success": False, "error": "No text provided"}

    try:
        logger.info(f"Rewriting resume text: {len(text)} characters")
        rewrites = build_section_rewrites(
            text,
            job_description=request.job_description,
            tone=request.tone,
            level=request.level,
            industry=request.industry,
        )

        logger.info("Resume rewrite completed successfully")

        return {
            "success": True,
            "rewrites": rewrites,
            "preset": {
                "tone": _normalize_preset(request.tone, TONE_MAP, "professional"),
                "level": _normalize_preset(request.level, LEVEL_MAP, "mid"),
                "industry": _normalize_preset(request.industry, INDUSTRY_MAP, "frontend"),
            },
        }

    except Exception as e:
        logger.error(f"Resume rewrite failed: {str(e)}")
        return {"success": False, "error": f"Rewrite failed: {str(e)}"}
