"""
STEP 7: Resume API Routes
FastAPI routes for resume analysis using the integrated pipeline
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Body

from ..models.api_models import (
    ResumeAnalysisResponse,
    JobComparisonResponse,
    JobDescriptionRequest,
    BenchmarkSummary
)
from ..services.analyzer_pipeline import CompleteResumeAnalysis
from ..services.jd_comparison import compare_with_jd
from ..services.benchmark import run_real_world_benchmarks
from ..utils.logger import logger, safe_execute, create_safe_response

router = APIRouter()

# Initialize the analyzer (single entry point for all operations)
analyzer = CompleteResumeAnalysis()


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Body(None, description="Optional job description for comparison")
) -> ResumeAnalysisResponse:
    """
    STEP 7: Upload and analyze resume
    Single endpoint that handles the complete analysis pipeline
    """
    logger.info(f"Received resume upload request: {file.filename}")

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

