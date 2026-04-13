"""
STEP 7: Resume API Routes
FastAPI routes for resume analysis using the integrated pipeline
"""

import re
import os
import json
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Body, Form

from ..models.api_models import (
    ResumeAnalysisResponse,
    JobComparisonResponse,
    JobDescriptionRequest,
    BenchmarkSummary
)
from ..services.analyzer_pipeline import CompleteResumeAnalysis
from ..services.jd_comparison import compare_with_jd
from ..services.benchmark import run_real_world_benchmarks
from ..services.role_profiles import (
    detect_role,
    get_role_profile,
    detect_experience_level,
    extract_experience_signals,
    experience_level_score,
)
from ..utils.logger import logger, safe_execute, create_safe_response

router = APIRouter()

# Initialize the analyzer (single entry point for all operations)
analyzer = CompleteResumeAnalysis()

COMMON_SKILLS = [
    "python", "java", "sql", "react", "node", "docker",
    "aws", "excel", "pandas", "machine learning",
    "javascript", "html", "css", "git"
]
PRIORITY_SKILLS = ["python", "sql", "react", "aws", "docker"]

SYNONYMS = {
    "js": "javascript",
    "javascript": "javascript",
    "nodejs": "node",
    "node.js": "node",
    "reactjs": "react",
    "react.js": "react",
    "ml": "machine learning",
    "ai": "machine learning",
}

STOPWORDS = {"and", "or", "the", "a", "an", "with", "to", "for", "in", "on", "of"}


def prioritize_missing(missing_skills):
    priority = [skill for skill in PRIORITY_SKILLS if skill in missing_skills]
    others = [skill for skill in missing_skills if skill not in priority]
    return priority + others


def get_verdict(score):
    if score >= 75:
        return "Strong Match"
    if score >= 50:
        return "Moderate Match"
    return "Low Match"


def normalize_text(text: str):
    text = (text or "").lower()
    for key, value in sorted(SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        text = re.sub(rf"\b{re.escape(key)}\b", value, text)
    return text


def _skill_in_text(skill: str, text: str) -> bool:
    if " " in skill:
        return skill in text
    return re.search(rf"\b{re.escape(skill)}\b", text) is not None


def extract_keywords(text: str):
    normalized = normalize_text(text)
    return [skill for skill in COMMON_SKILLS if _skill_in_text(skill, normalized)]


def extract_resume_skills(text: str):
    normalized = normalize_text(text)
    return [skill for skill in COMMON_SKILLS if _skill_in_text(skill, normalized)]


def parse_role_data(raw_role_data: Optional[str]) -> dict:
    if not raw_role_data:
        return {}

    try:
        parsed = json.loads(raw_role_data)
    except json.JSONDecodeError:
        logger.warning("Invalid role_data payload received")
        return {}

    return parsed if isinstance(parsed, dict) else {}


def normalize_role_skills(role_data: dict) -> list[str]:
    skills_value = role_data.get("skills", "")
    if isinstance(skills_value, list):
        values = skills_value
    else:
        values = [item.strip() for item in str(skills_value).split(",")]

    cleaned = []
    for value in values:
        normalized = value.strip().lower()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)

    return cleaned


def infer_required_level(experience_text: str) -> str:
    text = (experience_text or "").lower()

    if any(keyword in text for keyword in ["senior", "lead", "principal", "staff"]):
        return "senior"
    if any(keyword in text for keyword in ["junior", "entry", "fresher", "graduate"]):
        return "junior"

    years_match = re.search(r"(\d+(?:\.\d+)?)", text)
    if years_match:
        years = float(years_match.group(1))
        if years <= 2:
            return "junior"
        if years <= 5:
            return "mid"
        return "senior"

    return "mid"


def build_role_prompt(role_data: dict, job_description: Optional[str], resume_text: str) -> str:
    return f"""
You are a recruiter.

Role:
{role_data.get('role', 'Not specified')}

Experience Required:
{role_data.get('experience', 'Not specified')}

Work Type:
{role_data.get('workType', 'Not specified')}

Location:
{role_data.get('location', 'Not specified')}

Key Skills:
{role_data.get('skills', 'Not specified')}

Job Description:
{job_description or 'Not provided'}

Resume:
{resume_text}

Give a professional evaluation.
""".strip()


def build_role_context(role_data: dict, match_result: dict, job_description: Optional[str], resume_text: str) -> dict:
    role_skills = normalize_role_skills(role_data)
    role_type = detect_role(role_data.get("role", ""))
    required_level = detect_experience_level(role_data.get("experience", ""))
    signals = extract_experience_signals(resume_text)
    prompt = build_role_prompt(role_data, job_description, resume_text)

    score = match_result.get("match_score", 0)
    if score >= 75:
        review = "Strong alignment for the target role. The resume covers the core skills and reads like a credible recruiter-ready profile."
    elif score >= 50:
        review = "Moderate alignment for the target role. The resume shows a workable fit, but it would benefit from more role-specific proof and keyword coverage."
    else:
        review = "Low alignment for the target role. The resume needs more role-specific skills, stronger experience signals, and clearer tailoring before it would be competitive."

    if role_skills:
        review = f"{review} Target skills emphasized: {', '.join(role_skills[:6])}."

    return {
        "role": role_data.get("role", ""),
        "experience": role_data.get("experience", ""),
        "workType": role_data.get("workType", ""),
        "location": role_data.get("location", ""),
        "skills": role_skills,
        "role_type": role_type,
        "required_level": required_level,
        "experience_level": required_level,
        "experience_signals": signals,
        "professional_review": review,
        "analysis_prompt": prompt,
    }


def match_resume_to_jd(resume_text: str, jd_text: str, role_data: Optional[dict] = None):
    role_type = detect_role((role_data or {}).get("role", ""))
    profile = get_role_profile(role_type)
    experience_level = detect_experience_level((role_data or {}).get("experience", ""))
    signals = extract_experience_signals(resume_text)

    resume_text = normalize_text(resume_text)
    jd_text = normalize_text(jd_text)

    jd_keywords = extract_keywords(jd_text)
    jd_keywords.extend(profile.get("skills", []))
    if role_data:
        jd_keywords.extend(normalize_role_skills(role_data))
        jd_keywords = list(dict.fromkeys(jd_keywords))
    resume_skills = extract_resume_skills(resume_text)

    matched = [skill for skill in resume_skills if skill in jd_keywords]
    missing = [keyword for keyword in jd_keywords if keyword not in resume_skills][:5]

    score, breakdown = calculate_match_score(resume_text, jd_text, matched, jd_keywords, profile, experience_level, signals)
    confidence = "High" if len(matched) >= 4 else "Medium" if len(matched) >= 2 else "Low"

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "confidence": confidence,
        "role_type": role_type,
        "experience_level": experience_level,
        "experience_signals": signals,
        "breakdown": breakdown,
    }


def generate_suggestions(missing_skills):
    suggestions = []

    for skill in missing_skills:
        suggestions.append(
            f"Add {skill} experience or projects to better match the job description"
        )

    if not missing_skills:
        suggestions.append("Great match! Consider improving formatting and clarity.")

    return suggestions


def calculate_match_score(resume_text, jd_text, matched, jd_keywords, profile, experience_level, signals):
    if not jd_keywords:
        return 0, {
            "skills": 0,
            "keywords": 0,
            "experience": 0,
            "quality": 0,
            "format": 0,
        }

    skill_score = (len(matched) / len(jd_keywords)) * 100

    tokens = normalize_text(resume_text).split()
    token_count = max(len(tokens), 1)
    keyword_hits = sum(normalize_text(resume_text).count(skill) for skill in jd_keywords)
    density = keyword_hits / token_count
    if density > 0.05:
        keyword_score = 100.0
    elif density > 0.02:
        keyword_score = 70.0
    else:
        keyword_score = 40.0

    text = normalize_text(resume_text)
    experience_score = float(experience_level_score(experience_level, signals))

    quality_score = 100.0
    if any(word in text for word in ["worked", "helped", "did"]):
        quality_score -= 20
    if not re.search(r"\d", resume_text):
        quality_score -= 20
    if len(resume_text.split()) < 200:
        quality_score -= 20
    quality_score = max(quality_score, 0)

    format_score = 0.0
    if "education" in text:
        format_score += 25
    if "experience" in text:
        format_score += 25
    if "project" in text:
        format_score += 25
    if "skills" in text:
        format_score += 25

    weights = profile.get("weights", {})
    weighted_total = (
        skill_score * weights.get("skills", 0.4)
        + keyword_score * weights.get("keywords", 0.2)
        + experience_score * weights.get("experience", 0.15)
        + quality_score * weights.get("quality", 0.15)
        + format_score * weights.get("format", 0.1)
    )

    return min(int(round(weighted_total)), 100), {
        "skills": round(skill_score),
        "keywords": round(keyword_score),
        "experience": round(experience_score),
        "quality": round(quality_score),
        "format": round(format_score),
    }


def experience_level_warnings(level: str, signals: dict) -> list[str]:
    warnings = []

    if level == "junior" and not signals.get("has_projects"):
        warnings.append("Add at least 2 projects to strengthen your profile")
    if level == "mid" and not signals.get("has_numbers"):
        warnings.append("Add measurable impact (e.g., improved performance by 30%)")
    if level == "senior" and not signals.get("has_leadership"):
        warnings.append("Highlight leadership or ownership experience")

    return warnings


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


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None, description="Optional job description for comparison"),
    role_data: Optional[str] = Form(None, description="Structured role details for targeted analysis")
) -> ResumeAnalysisResponse:
    """
    STEP 7: Upload and analyze resume
    Single endpoint that handles the complete analysis pipeline
    """
    logger.info(f"Received resume upload request: {file.filename}")
    parsed_role_data = parse_role_data(role_data)

    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        logger.warning(f"Unsupported file type: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"File saved temporarily: {temp_file_path}")

        # Run complete analysis using the integrated pipeline
        result = analyzer.analyze_resume_complete(temp_file_path, job_description)

        if job_description:
            resume_text = result.get("raw_text", "")
            match_result = match_resume_to_jd(resume_text, job_description, role_data=parsed_role_data)
            role_context = build_role_context(parsed_role_data, match_result, job_description, resume_text) if parsed_role_data else {}
            result["success"] = True
            result["match_score"] = match_result["match_score"]
            result["matched_skills"] = match_result["matched_skills"]
            result["missing_skills"] = match_result["missing_skills"]
            result["suggestions"] = generate_suggestions(match_result["missing_skills"])
            result["confidence"] = match_result["confidence"]
            result["breakdown"] = match_result.get("breakdown", {})
            result["experience_level"] = match_result.get("experience_level", detect_experience_level(parsed_role_data.get("experience", "")))
            result["experience_signals"] = match_result.get("experience_signals", extract_experience_signals(resume_text))
            extra_warnings = experience_level_warnings(result["experience_level"], result["experience_signals"])
            result["warnings"] = [
                {
                    "type": "experience",
                    "message": warning,
                    "priority": "high",
                }
                for warning in extra_warnings
            ]
            if extra_warnings:
                result["suggestions"] = [*result["suggestions"], *extra_warnings]
            result["interview_probability"] = calculate_interview_probability(
                final_score=result.get("match_score", 0),
                missing_skills=result.get("missing_skills", []),
                warnings=result.get("warnings", []),
                level=result.get("experience_level", "mid"),
            )
            result["role_data"] = parsed_role_data
            result["role_context"] = role_context
            result["job_description_provided"] = True
            result["verdict"] = get_verdict(match_result["match_score"])
        else:
            result["success"] = True
            result["match_score"] = 0
            result["matched_skills"] = []
            result["missing_skills"] = []
            result["suggestions"] = []
            result["confidence"] = "Low"
            result["warnings"] = []
            result["interview_probability"] = {
                "score": 0,
                "label": "Low",
            }
            result["role_data"] = parsed_role_data
            result["role_context"] = build_role_context(parsed_role_data, {"match_score": 0}, None, result.get("raw_text", "")) if parsed_role_data else {}
            result["job_description_provided"] = False
            result["verdict"] = "Low Match"

        # Clean up temp file
        os.unlink(temp_file_path)

        # Convert to Pydantic response
        response = ResumeAnalysisResponse(**result)

        logger.info(f"Resume analysis completed successfully for {file.filename}")
        return response

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        logger.error(f"Resume analysis failed for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-existing/{resume_id}", response_model=ResumeAnalysisResponse)
async def analyze_existing_resume(
    resume_id: int,
    job_description: Optional[str] = Body(None)
) -> ResumeAnalysisResponse:
    """
    STEP 7: Re-analyze an existing resume from database
    """
    logger.info(f"Re-analysis request for resume ID: {resume_id}")

    try:
        # For now, return a placeholder - would need database integration
        # to retrieve the file path from resume_id
        response_data = create_safe_response(
            status="partial",
            message="Re-analysis feature not fully implemented yet",
            data={"resume_id": resume_id}
        )

        return ResumeAnalysisResponse(**response_data)

    except Exception as e:
        logger.error(f"Re-analysis failed for resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Re-analysis failed: {str(e)}")


@router.post("/compare-job", response_model=JobComparisonResponse)
async def compare_with_job_description(
    resume_id: int,
    job_request: JobDescriptionRequest
) -> JobComparisonResponse:
    """
    STEP 7: Compare resume with job description
    """
    logger.info(f"Job comparison request for resume {resume_id}")

    try:
        # Get resume data from database (placeholder - would need database integration)
        # For now, we'll use placeholder data
        resume_text = "Placeholder resume text - would be retrieved from database"
        skills = ["Python", "JavaScript", "React"]  # Placeholder skills

        # Use safe execution for JD comparison
        comparison_result = safe_execute(
            "jd_comparison",
            compare_with_jd,
            resume_text,
            job_request.description,
            skills,
            fallback_value={
                "similarity_score": 0.0,
                "matching_skills": [],
                "missing_skills": ["Unable to analyze"],
                "recommendations": ["Please try again later"]
            }
        )

        response_data = {
            "status": "success",
            "job_id": None,  # Would be assigned by database
            "resume_id": resume_id,
            "similarity_score": comparison_result.get("similarity_score", 0.0),
            "matching_skills": comparison_result.get("matching_skills", []),
            "missing_skills": comparison_result.get("missing_skills", []),
            "recommendations": comparison_result.get("recommendations", [])
        }

        return JobComparisonResponse(**response_data)

    except Exception as e:
        logger.error(f"Job comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/benchmark", response_model=BenchmarkSummary)
async def run_benchmarks() -> BenchmarkSummary:
    """
    STEP 8: Run real-world system benchmarks
    """
    logger.info("Running real-world system benchmarks")

    try:
        # Run comprehensive benchmarking
        benchmark_results = safe_execute(
            "real_world_benchmarks",
            run_real_world_benchmarks,
            fallback_value={
                "benchmark_results": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "average_ats_score": 0.0,
                    "average_ats_accuracy": 0.0,
                    "average_skills_accuracy": 0.0,
                    "average_ml_probability": 0.0,
                    "average_analysis_time": 0.0,
                    "overall_quality": "Benchmarking failed",
                    "results": [],
                    "recommendations": ["Benchmarking service unavailable"]
                },
                "industry_comparison": {},
                "overall_industry_readiness": False
            }
        )

        # Extract benchmark data for API response
        benchmark_data = benchmark_results["benchmark_results"]

        # Convert results to BenchmarkResult format
        formatted_results = []
        for result in benchmark_data.get("results", []):
            formatted_results.append({
                "test_name": result["test_name"],
                "resume_type": result["resume_type"],
                "ats_score": result["ats_score"],
                "ml_probability": result["ml_probability"],
                "skills_found": result["skills_found"],
                "verdict": result["verdict"],
                "notes": result["notes"]
            })

        response_data = {
            "total_tests": benchmark_data["total_tests"],
            "passed_tests": benchmark_data["passed_tests"],
            "average_ats_score": benchmark_data["average_ats_score"],
            "average_ml_probability": benchmark_data["average_ml_probability"],
            "overall_quality": benchmark_data["overall_quality"],
            "results": formatted_results,
            "recommendations": benchmark_data.get("recommendations", [])
        }

        return BenchmarkSummary(**response_data)

    except Exception as e:
        logger.error(f"Benchmarking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Benchmarking failed: {str(e)}")


@router.get("/health")
async def resume_health_check():
    """
    STEP 7: Resume service health check
    """
    try:
        # Quick health check - try to initialize analyzer
        test_analyzer = CompleteResumeAnalysis()
        return {"status": "healthy", "service": "resume_analysis"}
    except Exception as e:
        logger.error(f"Resume service health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Resume service unhealthy")

