from typing import List

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from ..services.resume_rewriter import rewrite_bullet_points
from ..services.analyzer_pipeline import CompleteResumeAnalysis
from ..models.api_models import ChatRequest, ChatResponse, BulletRewriteRequest, BulletRewriteResponse
from ..utils.logger import logger, safe_execute

router = APIRouter()

# Initialize analyzer pipeline
analyzer = CompleteResumeAnalysis()

@router.post("/rewrite-bullets", response_model=BulletRewriteResponse)
async def rewrite_bullets(request: BulletRewriteRequest = Body(...)) -> BulletRewriteResponse:
    """Rewrite bullet points for better ATS optimization"""
    try:
        if not request.bullet_points:
            raise HTTPException(status_code=400, detail="No bullet points provided")

        logger.info(f"Rewriting {len(request.bullet_points)} bullet points")

        # Use safe execution for bullet rewriting
        result = safe_execute(
            "bullet_rewrite",
            rewrite_bullet_points,
            request.bullet_points,
            fallback_value=[{"improved": bullet} for bullet in request.bullet_points]  # Return original if rewrite fails
        )

        # Extract just the improved text from the result objects
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict) and 'improved' in result[0]:
                rewritten_bullets = [item.get('improved', '') for item in result]
            else:
                rewritten_bullets = result
        else:
            rewritten_bullets = request.bullet_points

        return BulletRewriteResponse(
            status="success",
            original_count=len(request.bullet_points),
            rewritten_count=len(rewritten_bullets),
            rewritten_bullets=rewritten_bullets
        )

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Bullet rewrite failed: {error}")
        raise HTTPException(status_code=500, detail=f"Bullet rewrite failed: {error}") from error

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest = Body(...)) -> ChatResponse:
    """Chat with resume context using integrated analyzer pipeline"""
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="No question provided")

        if not request.resume_id:
            raise HTTPException(status_code=400, detail="Resume ID required for chat")

        logger.info(f"Chat request for resume {request.resume_id}: {request.question[:50]}...")

        # Generate intelligent response based on question content
        question_lower = request.question.lower()
        
        # Default intelligent responses based on question type
        if 'ats' in question_lower or 'score' in question_lower:
            answer = "Your ATS score depends on several factors: keyword optimization, proper formatting, section completeness, and action verbs usage. Areas to improve would be to include more industry-relevant keywords, use stronger action verbs, and ensure all major resume sections are present."
            suggestions = ["Add more technical keywords", "Use power action verbs", "Optimize formatting"]
        elif 'skill' in question_lower or 'add' in question_lower:
            answer = "Based on your resume analysis, consider adding skills in high-demand areas like cloud technologies, data analysis tools, automation frameworks, and modern development platforms. These are commonly sought by employers in your field."
            suggestions = ["Research in-demand skills", "Pursue relevant certifications", "Build projects with new skills"]
        elif 'improve' in question_lower or 'format' in question_lower:
            answer = "To improve your resume: 1) Use consistent formatting and spacing, 2) Add quantifiable metrics to achievements, 3) Replace weak verbs with power action verbs, 4) Ensure each bullet point has clear impact, 5) Keep it to 1-2 pages."
            suggestions = ["Use bullet point structure", "Add metrics to achievements", "Improve verb choices"]
        elif 'missing' in question_lower or 'section' in question_lower:
            answer = "Common missing sections that employers look for include: Professional Summary, Key Skills, Certifications, Projects, Languages, and Professional Affiliations. Adding relevant sections can significantly boost your ATS score."
            suggestions = ["Add Professional Summary", "Include Certifications", "Add relevant projects"]
        elif 'role' in question_lower or 'ready' in question_lower or 'qualified' in question_lower:
            answer = "Your resume shows good foundational skills. To be more competitive for your target role, focus on: 1) Adding role-specific keywords, 2) Highlighting relevant projects, 3) Quantifying achievements with numbers, 4) Showcasing leadership or impact."
            suggestions = ["Target role-specific keywords", "Highlight relevant projects", "Quantify achievements"]
        elif 'bullet' in question_lower or 'describe' in question_lower or 'experience' in question_lower:
            answer = "Strong bullet points follow the CAR format (Challenge-Action-Result): start with action verbs, describe what you did, and quantify the impact. For example: 'Led team of 5 to reduce deployment time by 40%, improving overall system efficiency.'"
            suggestions = ["Use CAR format", "Add quantified results", "Start with action verbs"]
        else:
            answer = "I'd be happy to help! You can ask me about: your ATS score, what skills to add, how to improve formatting, missing sections, role readiness, describing your experience better, or any other resume-related questions."
            suggestions = ["Ask about ATS score", "Ask what skills to add", "Ask how to improve formatting"]

        return ChatResponse(
            status="success",
            resume_id=request.resume_id,
            question=request.question,
            answer=answer,
            suggestions=suggestions
        )

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Chat failed: {error}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {error}") from error