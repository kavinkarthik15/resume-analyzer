from typing import List

from fastapi import APIRouter, HTTPException, Body

from ..services.jd_comparison import compare_with_jd
from ..services.role_recommendations import (
    role_skill_recommendation,
    get_available_roles,
    compare_multiple_roles
)
from ..models.api_models import (
    JobDescriptionRequest, JobComparisonResponse,
    RoleRecommendationRequest, RoleRecommendationResponse,
    AvailableRolesResponse, RoleComparisonRequest, RoleComparisonResponse
)
from ..utils.logger import logger, safe_execute

router = APIRouter()

@router.post("/compare-jd", response_model=JobComparisonResponse)
async def compare_job_description(
    resume_id: int,
    job_request: JobDescriptionRequest
) -> JobComparisonResponse:
    """Compare resume with job description"""
    try:
        logger.info(f"JD comparison for resume {resume_id} with job: {job_request.job_title}")

        # Get resume data from database (placeholder - would need database integration)
        # For now, we'll use a placeholder resume text
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

        return JobComparisonResponse(
            status="success",
            job_id=None,  # Would be assigned by database
            resume_id=resume_id,
            similarity_score=comparison_result.get("similarity_score", 0.0),
            matching_skills=comparison_result.get("matching_skills", []),
            missing_skills=comparison_result.get("missing_skills", []),
            recommendations=comparison_result.get("recommendations", [])
        )

    except Exception as error:
        logger.error(f"JD comparison failed: {error}")
        raise HTTPException(status_code=500, detail=f"JD comparison failed: {error}") from error

@router.post("/role-recommendation", response_model=RoleRecommendationResponse)
async def get_role_recommendation(request: RoleRecommendationRequest = Body(...)) -> RoleRecommendationResponse:
    """Get role-specific skill recommendations"""
    try:
        logger.info(f"Role recommendation for {request.target_role}")

        # Use safe execution for role recommendation
        result = safe_execute(
            "role_recommendation",
            role_skill_recommendation,
            request.skills,
            request.target_role,
            fallback_value={
                "skill_match_score": 0.0,
                "matching_skills": [],
                "missing_skills": ["Unable to analyze"],
                "recommendations": ["Please try again later"]
            }
        )

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return RoleRecommendationResponse(
            status="success",
            target_role=request.target_role,
            skill_match_score=result.get("skill_match_score", 0.0),
            matching_skills=result.get("matching_skills", []),
            missing_skills=result.get("missing_skills", []),
            recommendations=result.get("recommendations", [])
        )

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Role recommendation failed: {error}")
        raise HTTPException(status_code=500, detail=f"Role recommendation failed: {error}") from error

@router.get("/available-roles", response_model=AvailableRolesResponse)
async def list_available_roles() -> AvailableRolesResponse:
    """Get list of available roles for recommendations"""
    try:
        logger.info("Fetching available roles")

        # Use safe execution for getting roles
        roles = safe_execute(
            "get_available_roles",
            get_available_roles,
            fallback_value=[]
        )

        return AvailableRolesResponse(
            status="success",
            roles=roles
        )

    except Exception as error:
        logger.error(f"Failed to get roles: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to get roles: {error}") from error

@router.post("/compare-roles", response_model=RoleComparisonResponse)
async def compare_roles(request: RoleComparisonRequest = Body(...)) -> RoleComparisonResponse:
    """Compare user skills across multiple roles"""
    try:
        logger.info(f"Role comparison for {len(request.skills)} skills")

        # Use safe execution for role comparison
        results = safe_execute(
            "compare_multiple_roles",
            compare_multiple_roles,
            request.skills,
            fallback_value=[]
        )

        return RoleComparisonResponse(
            status="success",
            comparisons=results
        )

    except Exception as error:
        logger.error(f"Role comparison failed: {error}")
        raise HTTPException(status_code=500, detail=f"Role comparison failed: {error}") from error