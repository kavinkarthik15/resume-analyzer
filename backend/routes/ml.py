from fastapi import APIRouter, HTTPException

from ..services.analyzer_pipeline import CompleteResumeAnalysis
from ..models.api_models import MLPredictionRequest, MLPredictionResponse
from ..utils.logger import logger, safe_execute

router = APIRouter()

# Initialize analyzer pipeline
analyzer = CompleteResumeAnalysis()

@router.post("/predict", response_model=MLPredictionResponse)
async def predict_shortlist(request: MLPredictionRequest) -> MLPredictionResponse:
    """Predict shortlist probability for a resume using ML model"""
    try:
        logger.info(f"ML prediction request for resume {request.resume_id}")

        # Get analysis data for the resume (placeholder - would need database integration)
        # For now, we'll create a mock analysis result
        mock_analysis_data = {
            "skill_count": 15,
            "matched_role_skills": 8,
            "ats_score": 85.0,
            "jd_similarity": 0.7,
            "experience_years": 5.0,
            "action_verbs": 12,
            "achievements": 8,
            "pages": 2,
            "section_score": 0.9
        }

        # Use analyzer pipeline's ML engine for prediction
        prediction_result = safe_execute(
            "ml_prediction",
            analyzer.ml_engine.predict_shortlist_probability,
            mock_analysis_data,
            fallback_value={
                "probability": 0.5,
                "decision": "Unable to predict",
                "confidence": "Low",
                "reasoning": ["Prediction service temporarily unavailable"]
            }
        )

        return MLPredictionResponse(
            status="success",
            resume_id=request.resume_id,
            probability=prediction_result.get("probability", 0.5),
            decision=prediction_result.get("decision", "Unable to predict"),
            confidence=prediction_result.get("confidence"),
            reasoning=prediction_result.get("reasoning", [])
        )

    except Exception as error:
        logger.error(f"ML prediction failed: {error}")
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {error}") from error