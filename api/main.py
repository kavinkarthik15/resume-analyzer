from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import io
import logging
import re
from typing import Any, Optional

from ml.analyzer_pipeline import CompleteResumeAnalysis as ResumeAnalyzer

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


def calculate_jd_match(resume_text: str, job_description: str) -> dict:
    jd_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)

    if not jd_skills:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "verdict": "Low Match",
            "confidence": "Low",
        }

    matched_skills = [skill for skill in jd_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

    match_score = int((len(matched_skills) / len(jd_skills)) * 100)
    verdict = "Strong Match" if match_score >= 75 else "Moderate Match" if match_score >= 50 else "Low Match"
    confidence = "High" if len(matched_skills) >= 4 else "Medium" if len(matched_skills) >= 2 else "Low"

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "verdict": verdict,
        "confidence": confidence,
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
            response = success_response(result)

            # Return explicit JD match fields consumed by the frontend results page.
            if job_description and job_description.strip():
                jd_match = calculate_jd_match(text, job_description)
                response.update(jd_match)
                response["job_description_provided"] = True
                response["score"] = jd_match["match_score"]
            else:
                response.setdefault("match_score", response.get("score", 0))
                response.setdefault("matched_skills", [])
                response.setdefault("missing_skills", [])
                response.setdefault("verdict", "Low Match")
                response["job_description_provided"] = False

            return response

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return error_response(str(e))