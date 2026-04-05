"""
STEP 7: API Models
Pydantic models for request/response validation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: Optional[str] = Field(None, description="Response timestamp")


class ResumeUploadRequest(BaseModel):
    """Resume upload request"""
    filename: str = Field(..., description="Original filename")


class ResumeAnalysisResponse(BaseModel):
    """Complete resume analysis response"""
    success: bool = Field(True, description="Whether the analysis completed successfully")
    status: str = Field(..., description="Analysis status: success, partial, failed")
    message: Optional[str] = Field(None, description="Human-readable status message")
    resume_id: Optional[int] = Field(None, description="Database resume ID")
    analysis_id: Optional[int] = Field(None, description="Database analysis ID")

    # Job match results
    match_score: int = Field(0, description="Resume vs job description match score")
    confidence: str = Field("Low", description="Match confidence level")
    matched_skills: List[str] = Field(default_factory=list, description="Matched skills")
    missing_skills: List[str] = Field(default_factory=list, description="Missing skills")
    suggestions: List[str] = Field(default_factory=list, description="Match suggestions")

    # Parsing results
    parsing: Dict[str, Any] = Field(default_factory=dict, description="Resume parsing results")

    # ATS analysis
    ats_analysis: Dict[str, Any] = Field(default_factory=dict, description="ATS scoring analysis")

    # Chat context
    chat_ready: bool = Field(False, description="Whether chat is ready")
    chat_context_summary: str = Field("", description="Chat context summary")

    # Progress tracking
    progress: Dict[str, Any] = Field(default_factory=dict, description="Progress metrics")

    # ML prediction
    ml_prediction: Dict[str, Any] = Field(default_factory=dict, description="ML prediction results")

    # Validation results
    ml_validation: Dict[str, Any] = Field(default_factory=dict, description="ML validation results")
    ats_ml_alignment: Dict[str, Any] = Field(default_factory=dict, description="ATS-ML alignment results")

    # Error details
    error: Optional[str] = Field(None, description="Error message if failed")


class JobDescriptionRequest(BaseModel):
    """Job description for comparison"""
    job_title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description")
    requirements: Optional[str] = Field(None, description="Specific requirements")


class JobComparisonResponse(BaseModel):
    """Job description comparison response"""
    status: str = Field(..., description="Comparison status")
    job_id: Optional[int] = Field(None, description="Database job ID")
    resume_id: Optional[int] = Field(None, description="Resume ID used for comparison")

    # Comparison results
    similarity_score: float = Field(..., description="Overall similarity score (0-1)")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills not found")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

    error: Optional[str] = Field(None, description="Error message if failed")


class RoleRecommendationRequest(BaseModel):
    """Role recommendation request"""
    skills: List[str] = Field(..., description="User's current skills")
    target_role: str = Field(..., description="Target role to analyze")


class RoleRecommendationResponse(BaseModel):
    """Role recommendation response"""
    status: str = Field(..., description="Recommendation status")
    target_role: str = Field(..., description="Target role analyzed")
    skill_match_score: float = Field(..., description="Skill match score (0-1)")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match the role")
    missing_skills: List[str] = Field(default_factory=list, description="Skills needed for the role")
    recommendations: List[str] = Field(default_factory=list, description="Skill development recommendations")

    error: Optional[str] = Field(None, description="Error message if failed")


class AvailableRolesResponse(BaseModel):
    """Available roles response"""
    status: str = Field(..., description="Response status")
    roles: List[str] = Field(default_factory=list, description="List of available roles")

    error: Optional[str] = Field(None, description="Error message if failed")


class RoleComparisonRequest(BaseModel):
    """Role comparison request"""
    skills: List[str] = Field(..., description="User's current skills")


class RoleComparisonResponse(BaseModel):
    """Role comparison response"""
    status: str = Field(..., description="Comparison status")
    comparisons: List[Dict[str, Any]] = Field(default_factory=list, description="Role comparison results")

    error: Optional[str] = Field(None, description="Error message if failed")


class ChatRequest(BaseModel):
    """Chat interaction request"""
    resume_id: int = Field(..., description="Resume ID to chat about")
    question: str = Field(..., description="User question")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat interaction response"""
    status: str = Field(..., description="Chat status")
    resume_id: int = Field(..., description="Resume ID")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI response")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")

    error: Optional[str] = Field(None, description="Error message if failed")


class BulletRewriteRequest(BaseModel):
    """Bullet point rewrite request"""
    bullet_points: List[str] = Field(..., description="List of bullet points to rewrite")


class BulletRewriteResponse(BaseModel):
    """Bullet point rewrite response"""
    status: str = Field(..., description="Rewrite status")
    original_count: int = Field(..., description="Number of original bullet points")
    rewritten_count: int = Field(..., description="Number of rewritten bullet points")
    rewritten_bullets: List[str] = Field(default_factory=list, description="Rewritten bullet points")

    error: Optional[str] = Field(None, description="Error message if failed")


class MLPredictionRequest(BaseModel):
    """ML prediction request"""
    resume_id: int = Field(..., description="Resume ID to predict for")


class MLPredictionResponse(BaseModel):
    """ML prediction response"""
    status: str = Field(..., description="Prediction status")
    resume_id: int = Field(..., description="Resume ID")
    probability: float = Field(..., description="Shortlist probability (0-1)")
    decision: str = Field(..., description="Prediction decision")
    confidence: Optional[str] = Field(None, description="Confidence level")
    reasoning: List[str] = Field(default_factory=list, description="Prediction reasoning")

    error: Optional[str] = Field(None, description="Error message if failed")


class BenchmarkResult(BaseModel):
    """Benchmark test result"""
    test_name: str = Field(..., description="Name of the test case")
    resume_type: str = Field(..., description="Type of resume tested")
    ats_score: int = Field(..., description="ATS score achieved")
    ml_probability: float = Field(..., description="ML prediction probability")
    skills_found: int = Field(..., description="Number of skills detected")
    verdict: str = Field(..., description="Pass/fail verdict")
    notes: Optional[str] = Field(None, description="Additional notes")


class BenchmarkSummary(BaseModel):
    """Benchmark summary"""
    total_tests: int = Field(..., description="Total number of tests")
    passed_tests: int = Field(..., description="Number of passed tests")
    average_ats_score: float = Field(..., description="Average ATS score")
    average_ml_probability: float = Field(..., description="Average ML probability")
    overall_quality: str = Field(..., description="Overall system quality assessment")
    results: List[BenchmarkResult] = Field(default_factory=list, description="Individual test results")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")