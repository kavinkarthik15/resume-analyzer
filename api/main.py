from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import io
import logging
import re
import json
from typing import Any, Optional

from ml.analyzer_pipeline import CompleteResumeAnalysis as ResumeAnalyzer
from backend.routes.jd_generator import router as jd_router
from backend.routes.rewrite import router as rewrite_router
from backend.services.role_profiles import (
    detect_role,
    get_role_profile,
    detect_experience_level,
    extract_experience_signals,
    experience_level_score,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = ResumeAnalyzer()
# Provide alias for the expected method name
analyzer.analyze_resume = analyzer.analyze_resume_text

app.include_router(jd_router)
app.include_router(rewrite_router)


def error_response(message: str) -> dict:
    return {
        "success": False,
        "error": message
    }


def compute_score_from_confidence(confidence: Any) -> int:
    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError):
        confidence_value = 0.0

    confidence_value = max(0.0, min(1.0, confidence_value))
    return int(confidence_value * 100)


SKILL_SYNONYMS = {
    "js": "javascript",
    "nodejs": "node",
    "node.js": "node",
    "reactjs": "react",
    "react.js": "react",
}

COMMON_SKILLS = [
    "python", "java", "sql", "react", "node", "docker",
    "aws", "excel", "pandas", "machine learning",
    "javascript", "html", "css", "git"
]

STRONG_ACTION_VERBS = {
    "built", "developed", "optimized", "led", "designed", "implemented",
    "delivered", "improved", "launched", "automated", "engineered", "scaled",
}

WEAK_ACTION_VERBS = {"worked", "helped", "did", "made", "handled", "assisted"}


def normalize_text(text: str) -> str:
    normalized = text.lower()
    for source, target in sorted(SKILL_SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = re.sub(rf"\b{re.escape(source)}\b", target, normalized)
    return normalized


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)
    matched = []
    for skill in COMMON_SKILLS:
        if " " in skill:
            if skill in normalized:
                matched.append(skill)
        else:
            if re.search(rf"\b{re.escape(skill)}\b", normalized):
                matched.append(skill)
    return matched


def parse_role_data(raw_role_data: Optional[str]) -> dict:
    if not raw_role_data:
        return {}

    try:
        parsed = json.loads(raw_role_data)
    except json.JSONDecodeError:
        return {}

    return parsed if isinstance(parsed, dict) else {}


def normalize_role_skills(role_data: dict) -> list[str]:
    skills_value = role_data.get("skills", "")
    if isinstance(skills_value, list):
        raw_skills = skills_value
    else:
        raw_skills = [item.strip() for item in str(skills_value).split(",")]

    cleaned = []
    for skill in raw_skills:
        normalized = normalize_text(skill).strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)

    return cleaned


def build_role_prompt(role_type: str, resume_text: str, job_description: str) -> str:
    return f"""
You are a recruiter hiring for a {role_type} role.

Evaluate this resume based on role-specific expectations.

Focus on:
- Relevant skills for {role_type}
- Experience quality
- Missing critical technologies

Resume:
{resume_text}

Job Description:
{job_description}
""".strip()


def calculate_jd_match(resume_text: str, job_description: str, role_data: Optional[dict] = None) -> dict:
    role_type = detect_role((role_data or {}).get("role", ""))
    profile = get_role_profile(role_type)
    experience_level = detect_experience_level((role_data or {}).get("experience", ""))
    experience_signals = extract_experience_signals(resume_text)

    jd_skills = extract_skills(job_description)
    jd_skills.extend(profile.get("skills", []))
    jd_skills.extend(normalize_role_skills(role_data or {}))
    jd_skills = list(dict.fromkeys(jd_skills))
    resume_skills = extract_skills(resume_text)

    if not jd_skills:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "breakdown": {
                "skills": 0,
                "keywords": 0,
                "experience": 0,
                "quality": 0,
                "format": 0,
            },
            "verdict": "Low Match",
            "confidence": "Low",
            "role_type": role_type,
        }

    matched_skills = [skill for skill in jd_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

    def compute_skill_score() -> float:
        total = len(jd_skills)
        if total == 0:
            return 0.0
        return (len(matched_skills) / total) * 100

    def compute_keyword_score() -> float:
        tokens = normalize_text(resume_text).split()
        token_count = max(len(tokens), 1)
        keyword_hits = sum(normalize_text(resume_text).count(skill) for skill in jd_skills)
        density = keyword_hits / token_count

        if density > 0.05:
            return 100.0
        if density > 0.02:
            return 70.0
        return 40.0

    def compute_quality_score() -> float:
        text = normalize_text(resume_text)
        score = 100

        if any(word in text for word in ["worked", "helped", "did"]):
            score -= 20
        if not re.search(r"\d", resume_text):
            score -= 20
        if len(resume_text.split()) < 200:
            score -= 20

        return float(max(score, 0))

    def compute_format_score() -> float:
        text = normalize_text(resume_text)
        score = 0

        if "education" in text:
            score += 25
        if "experience" in text:
            score += 25
        if "project" in text:
            score += 25
        if "skills" in text:
            score += 25

        return float(score)

    skill_score = compute_skill_score()
    keyword_score = compute_keyword_score()
    experience_score = float(experience_level_score(experience_level, experience_signals))
    quality_score = compute_quality_score()
    format_score = compute_format_score()

    weights = profile.get("weights", {})
    weighted_total = (
        skill_score * weights.get("skills", 0.4)
        + keyword_score * weights.get("keywords", 0.2)
        + experience_score * weights.get("experience", 0.15)
        + quality_score * weights.get("quality", 0.15)
        + format_score * weights.get("format", 0.1)
    )

    match_score = int(round(weighted_total))
    verdict = "Strong Match" if match_score >= 75 else "Moderate Match" if match_score >= 50 else "Low Match"
    confidence = "High" if len(matched_skills) >= 4 else "Medium" if len(matched_skills) >= 2 else "Low"

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "breakdown": {
            "skills": round(skill_score),
            "keywords": round(keyword_score),
            "experience": round(experience_score),
            "quality": round(quality_score),
            "format": round(format_score),
        },
        "verdict": verdict,
        "confidence": confidence,
        "role_type": role_type,
        "experience_level": experience_level,
        "experience_signals": experience_signals,
    }


def generate_warnings(
    resume_text: str,
    jd_text: Optional[str],
    matched_skills: list[str],
    missing_skills: list[str],
    role_type: str = "general",
    level: str = "mid",
    signals: Optional[dict] = None,
) -> list[dict]:
    warnings: list[dict] = []
    normalized = normalize_text(resume_text)
    words = re.findall(r"\b[a-zA-Z]+\b", resume_text)
    lower_words = [word.lower() for word in words]

    def add_warning(
        warning_type: str,
        message: str,
        suggestion: str,
        priority: str,
        category: str,
        icon: str,
    ) -> None:
        warnings.append(
            {
                "id": f"{warning_type}-{len(warnings) + 1}",
                "type": warning_type,
                "message": message,
                "suggestion": suggestion,
                "priority": priority,
                "category": category,
                "icon": icon,
            }
        )

    # 1) Missing sections.
    if not re.search(r"\bprojects?\b", normalized):
        add_warning(
            warning_type="section",
            message="Missing Projects section.",
            suggestion="Add 1-3 projects with stack, impact, and links.",
            priority="high",
            category="Sections",
            icon="📁",
        )

    if not re.search(r"\beducation\b", normalized):
        add_warning(
            warning_type="section",
            message="Missing Education section.",
            suggestion="Add degree, institution, and graduation year.",
            priority="medium",
            category="Sections",
            icon="🎓",
        )

    # 2) Quantified impact.
    if not re.search(r"\d", resume_text):
        add_warning(
            warning_type="impact",
            message="No measurable achievements found.",
            suggestion="Use numbers like 'Improved performance by 30%' or 'Reduced costs by 15%'.",
            priority="high",
            category="Impact",
            icon="📊",
        )

    # 3) Weak action verbs.
    weak_found = sorted({word for word in lower_words if word in WEAK_ACTION_VERBS})
    strong_count = sum(1 for word in lower_words if word in STRONG_ACTION_VERBS)
    if weak_found and strong_count < 3:
        add_warning(
            warning_type="writing",
            message=f"Weak action verbs detected: {', '.join(weak_found[:4])}.",
            suggestion="Replace with stronger verbs like Built, Developed, Optimized, or Led.",
            priority="medium",
            category="Writing",
            icon="✍️",
        )

    # 4) Resume length.
    word_count = len(resume_text.split())
    if word_count > 800:
        add_warning(
            warning_type="length",
            message="Resume is too long for most ATS screens.",
            suggestion="Keep it concise, usually 1-2 pages (~400-800 words).",
            priority="medium",
            category="Length",
            icon="📄",
        )
    elif word_count < 200:
        add_warning(
            warning_type="length",
            message="Resume is too short and may look incomplete.",
            suggestion="Add more detail on projects, impact, and technical depth.",
            priority="high",
            category="Length",
            icon="📄",
        )

    # 5) Missing JD skills.
    if jd_text and jd_text.strip() and missing_skills:
        add_warning(
            warning_type="skills",
            message=f"Missing key skills from job description: {', '.join(missing_skills[:5])}.",
            suggestion="Add relevant experience, projects, or tools for these skills if you have them.",
            priority="high",
            category="Skills",
            icon="🧩",
        )

    # 6) Role-specific critical technologies.
    if role_type == "frontend" and "react" not in normalized:
        add_warning(
            warning_type="skills",
            message="React is highly recommended for frontend roles.",
            suggestion="Add React-based project experience and component-level accomplishments.",
            priority="high",
            category="Skills",
            icon="🧩",
        )

    if role_type == "backend" and "api" not in normalized:
        add_warning(
            warning_type="skills",
            message="Backend roles require API experience.",
            suggestion="Include REST/GraphQL API design, integration, or optimization work.",
            priority="high",
            category="Skills",
            icon="🧩",
        )

    if role_type == "data" and "machine learning" not in normalized and "pandas" not in normalized:
        add_warning(
            warning_type="skills",
            message="Data roles strongly prefer Python data-stack experience.",
            suggestion="Add examples using Python, pandas, SQL, and ML workflows.",
            priority="high",
            category="Skills",
            icon="🧩",
        )

    signals = signals or extract_experience_signals(resume_text)

    # 7) Experience-level expectations.
    if level == "junior" and not signals.get("has_projects"):
        add_warning(
            warning_type="experience",
            message="Add at least 2 projects to strengthen your profile.",
            suggestion="Show practical hands-on work with tech stack and outcomes.",
            priority="high",
            category="Experience",
            icon="📈",
        )

    if level == "mid" and not signals.get("has_numbers"):
        add_warning(
            warning_type="experience",
            message="Add measurable impact (e.g., improved performance by 30%).",
            suggestion="Quantify outcomes for projects and production work.",
            priority="high",
            category="Experience",
            icon="📈",
        )

    if level == "senior" and not signals.get("has_leadership"):
        add_warning(
            warning_type="experience",
            message="Highlight leadership or ownership experience.",
            suggestion="Include examples where you led teams, mentored others, or owned delivery.",
            priority="high",
            category="Experience",
            icon="📈",
        )

    return warnings


def generate_suggestions(
    resume_text: str,
    missing_skills: list[str],
    warnings: list[dict],
) -> list[dict]:
    suggestions: list[dict] = []

    for skill in missing_skills[:5]:
        suggestions.append(
            {
                "type": "skill",
                "message": f"Add projects or experience demonstrating {skill}.",
                "example": f"Built a project using {skill} to solve a real-world problem.",
            }
        )

    warning_types = {warning.get("type") for warning in warnings if isinstance(warning, dict)}

    if "writing" in warning_types:
        suggestions.append(
            {
                "type": "writing",
                "message": "Use stronger action verbs for impact.",
                "example": "Replace 'worked on' with 'Developed', 'Built', or 'Optimized'.",
            }
        )

    if "impact" in warning_types:
        suggestions.append(
            {
                "type": "impact",
                "message": "Add measurable achievements to prove outcomes.",
                "example": "Improved application performance by 40% and reduced load time by 1.2s.",
            }
        )

    if "section" in warning_types:
        suggestions.append(
            {
                "type": "section",
                "message": "Include missing core sections like Projects or Education.",
                "example": "Add a 'Projects' section with 2-3 strong, relevant projects.",
            }
        )

    if "summary" not in normalize_text(resume_text):
        suggestions.append(
            {
                "type": "summary",
                "message": "Add a professional summary aligned to your target role.",
                "example": "Frontend Developer with 2+ years building scalable React and JavaScript applications.",
            }
        )

    priority_order = {
        "skill": 1,
        "impact": 2,
        "writing": 3,
        "section": 4,
        "summary": 5,
    }
    suggestions.sort(key=lambda item: priority_order.get(item.get("type"), 99))

    return suggestions


def calculate_interview_probability(final_score: int, missing_skills: list[str], warnings: list[dict], level: str) -> dict:
    penalty = 0

    if len(missing_skills) >= 5:
        penalty += 15
    elif len(missing_skills) >= 3:
        penalty += 10

    penalty += len(warnings) * 2

    if level == "senior":
        penalty += 5

    adjusted_score = max(0, int(final_score) - penalty)

    if adjusted_score >= 80:
        label = "High"
    elif adjusted_score >= 60:
        label = "Medium"
    else:
        label = "Low"

    return {
        "score": adjusted_score,
        "label": label,
    }


def success_response(payload: dict) -> dict:
    response = dict(payload)
    response["score"] = compute_score_from_confidence(response.get("confidence", 0.0))
    response.setdefault("success", True)
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    role_data: Optional[str] = Form(None),
):
    try:
        contents = await file.read()

        # File validation
        if not file.filename.endswith((".pdf", ".txt")):
            return error_response("Only PDF or TXT files allowed")

        # File size limit (2MB)
        if len(contents) > 2 * 1024 * 1024:
            return error_response("File too large")

        logger.info("Processing resume")

        if file.filename.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(contents))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        else:
            text = contents.decode("utf-8", errors="ignore")

        if not text.strip():
            return error_response("No text extracted from file")

        result = analyzer.analyze_resume(text)

        if isinstance(result, dict):
            parsed_role_data = parse_role_data(role_data)
            detected_role_type = detect_role(parsed_role_data.get("role", ""))
            detected_experience_level = detect_experience_level(parsed_role_data.get("experience", ""))
            parsed_experience_signals = extract_experience_signals(text)
            response = success_response(result)

            # Return explicit JD match fields consumed by the frontend results page.
            matched_skills: list[str] = []
            missing_skills: list[str] = []
            if job_description and job_description.strip():
                jd_match = calculate_jd_match(text, job_description, role_data=parsed_role_data)
                response.update(jd_match)
                response["job_description_provided"] = True
                response["score"] = jd_match["match_score"]
                matched_skills = jd_match["matched_skills"]
                missing_skills = jd_match["missing_skills"]
                detected_role_type = jd_match.get("role_type", detected_role_type)
                detected_experience_level = jd_match.get("experience_level", detected_experience_level)
                parsed_experience_signals = jd_match.get("experience_signals", parsed_experience_signals)
            else:
                response.setdefault("match_score", response.get("score", 0))
                response.setdefault("matched_skills", [])
                response.setdefault("missing_skills", [])
                response.setdefault("verdict", "Low Match")
                response["job_description_provided"] = False
                matched_skills = response["matched_skills"]
                missing_skills = response["missing_skills"]

            response["warnings"] = generate_warnings(
                resume_text=text,
                jd_text=job_description,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                role_type=detected_role_type,
                level=detected_experience_level,
                signals=parsed_experience_signals,
            )
            response["suggestions"] = generate_suggestions(
                resume_text=text,
                missing_skills=missing_skills,
                warnings=response["warnings"],
            )
            response["interview_probability"] = calculate_interview_probability(
                final_score=response.get("match_score", response.get("score", 0)),
                missing_skills=missing_skills,
                warnings=response.get("warnings", []),
                level=detected_experience_level,
            )
            response["role_data"] = parsed_role_data
            response["experience_level"] = detected_experience_level
            response["role_context"] = {
                "role": parsed_role_data.get("role", ""),
                "experience": parsed_role_data.get("experience", ""),
                "workType": parsed_role_data.get("workType", ""),
                "location": parsed_role_data.get("location", ""),
                "skills": normalize_role_skills(parsed_role_data),
                "role_type": detected_role_type,
                "experience_level": detected_experience_level,
                "experience_signals": parsed_experience_signals,
                "analysis_prompt": build_role_prompt(detected_role_type, text, job_description or "Not provided"),
            }

            return response

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return error_response(str(e))