"""
Resume Rewrite API Routes
FastAPI routes for resume bullet point rewriting
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel
from ..utils.logger import logger

router = APIRouter()


class RewriteRequest(BaseModel):
    text: str


@router.post("/rewrite")
async def rewrite_resume(request: RewriteRequest) -> dict:
    """
    Rewrite resume content for improved ATS compatibility and impact
    """
    text = request.text

    if not text or not text.strip():
        return {"success": False, "error": "No text provided"}

    try:
        logger.info(f"Rewriting resume text: {len(text)} characters")

        # Simple improvement logic (placeholder)
        improved = f"Improved version: {text}"

        logger.info("Resume rewrite completed successfully")
        
        return {
            "success": True,
            "original": text,
            "improved": improved
        }

    except Exception as e:
        logger.error(f"Resume rewrite failed: {str(e)}")
        return {"success": False, "error": f"Rewrite failed: {str(e)}"}
