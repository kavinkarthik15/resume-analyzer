from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.ai_service import generate_job_description

router = APIRouter()


class JDRequest(BaseModel):
    role: str = Field(..., description="Target role")
    experience: str = Field(..., description="Required experience")
    workType: str = Field(..., description="Work type")
    location: Optional[str] = Field("", description="Location")
    skills: Optional[str] = Field("", description="Comma-separated key skills")


@router.post("/generate-jd")
def generate_jd(req: JDRequest):
    jd = generate_job_description(req.dict())

    return {
        "success": True,
        "job_description": jd,
    }