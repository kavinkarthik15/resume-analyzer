"""
Integrated Resume Analysis Pipeline
Combines all phases 6-11 for complete analysis
"""

import time
from typing import Optional, Dict, Any

from .parser import parse_resume, validate_parsed_resume, ResumeParsedData
from .scorer import calculate_ats_score, get_ats_improvement_tips, ATSScoreBreakdown
from .chat_assistant import chat_assistant
from .progress_tracker import ProgressTracker
from .database import db
from .ml_manager import MLPredictionEngine, FeatureEngineering
from .ml_validation import MLValidator
from .ats_ml_alignment import ATSMLAlignmentChecker
from ..models.ml_model import ml_model as default_ml_model
from ..utils.logger import logger, safe_execute, SafeOperation, create_safe_response


class CompleteResumeAnalysis:
    """
    INTEGRATED PHASE 6-11 PIPELINE
    Complete resume analysis with all features
    """
    
    def __init__(self, ml_model=None):
        if ml_model is None:
            ml_model = default_ml_model
        self.ml_engine = MLPredictionEngine(model=ml_model)
        self.progress_tracker = ProgressTracker()
        self.db = db
    
    def analyze_resume_complete(self, file_path: str, jd_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete resume analysis pipeline
        
        Steps:
        1. Parse resume (Phase 6)
        2. Calculate ATS score (Phase 7)
        3. Prepare for chat (Phase 8)
        4. Track progress (Phase 9)
        5. Store in database (Phase 10)
        6. ML prediction (Phase 11)
        
        Args:
            file_path: Path to resume file
            jd_text: Optional job description for comparison
            
        Returns:
            Comprehensive analysis result
        """
        start_time = time.time()
        logger.info(f"Starting complete resume analysis for: {file_path}")

        try:
            # PHASE 6: Parse Resume
            with SafeOperation("resume_parsing"):
                parsed = safe_execute(
                    "resume_parsing",
                    parse_resume,
                    file_path,
                    fallback_value=ResumeParsedData()
                )
                validation = safe_execute(
                    "resume_validation",
                    validate_parsed_resume,
                    parsed,
                    fallback_value={"valid": False, "issues": ["Parsing failed"]}
                )

            # PHASE 7: Calculate ATS Score
            with SafeOperation("ats_scoring"):
                ats_breakdown = safe_execute(
                    "ats_scoring",
                    calculate_ats_score,
                    parsed.raw_text,
                    parsed.skills,
                    parsed.skill_frequency,
                    parsed.sections_detected,
                    fallback_value=ATSScoreBreakdown()
                )

            # Build analysis data
            analysis_data = {
                "parsed": parsed.to_dict(),
                "validation": validation,
                "ats_score": ats_breakdown.total_score,
                "breakdown": ats_breakdown.to_dict()["breakdown"],
                "missing_skills": ats_breakdown.missing_skills,
                "missing_sections": ats_breakdown.missing_sections,
                "formatting_issues": ats_breakdown.formatting_issues,
                "skills_found": parsed.skills,
                "skill_categories": parsed.skill_categories,
                "sections_detected": parsed.sections_detected,
                "raw_text": parsed.raw_text,
            }

            # PHASE 8: Prepare chat context (ready for questions)
            chat_context = {
                "ats_score": ats_breakdown.total_score,
                "breakdown": ats_breakdown.to_dict()["breakdown"],
                "skills_found": parsed.skills,
                "skill_categories": parsed.skill_categories,
                "missing_skills": ats_breakdown.missing_skills,
                "formatting_issues": ats_breakdown.formatting_issues,
                "raw_text": parsed.raw_text,
            }

            # PHASE 9: Record in progress tracker
            with SafeOperation("progress_tracking"):
                safe_execute(
                    "progress_update",
                    self.progress_tracker.record_analysis,
                    ats_breakdown.total_score, parsed.skills
                )

            # PHASE 10: Save to database
            with SafeOperation("database_storage"):
                resume_id = safe_execute(
                    "resume_save",
                    self.db.save_resume,
                    file_path.split("\\")[-1],
                    parsed.raw_text,
                    parsed.to_dict(),
                    file_path,
                    fallback_value=None
                )

                analysis_id = safe_execute(
                    "analysis_save",
                    self.db.save_analysis,
                    resume_id, analysis_data,
                    fallback_value=None
                ) if resume_id else None

            # PHASE 11: ML Prediction
            with SafeOperation("ml_prediction"):
                ml_prediction = safe_execute(
                    "ml_prediction",
                    self.ml_engine.predict_shortlist_probability,
                    analysis_data,
                    fallback_value={
                        "probability": ats_breakdown.total_score / 100.0,
                        "decision": "Unable to predict",
                        "error": "ML prediction failed",
                        "fallback": True
                    }
                )

            # STEP 3: ML Validation (Sanity Checks)
            with SafeOperation("ml_validation"):
                ml_validator = MLValidator(self.ml_engine)
                validation_result = safe_execute(
                    "ml_validation",
                    ml_validator.debug_feature_inputs,
                    analysis_data,
                    fallback_value={}
                )

            # STEP 4: ATS-ML Alignment Check
            with SafeOperation("ats_ml_alignment"):
                alignment_checker = ATSMLAlignmentChecker(self.ml_engine)
                ats_score = ats_breakdown.total_score
                ml_probability = ml_prediction.get("probability", 0.5)
                alignment_result = safe_execute(
                    "alignment_check",
                    alignment_checker.check_alignment,
                    ats_score, ml_probability,
                    fallback_value={"aligned": False, "quality": "UNKNOWN"}
                )

            # Compile complete result
            complete_result = {
                "status": "success" if validation["valid"] else "warnings",
                "resume_id": resume_id,
                "analysis_id": analysis_id,

                # Phase 6 Results
                "parsing": {
                    "skills": parsed.skills,
                    "skill_categories": parsed.skill_categories,
                    "experience": parsed.experience,
                    "education": parsed.education,
                    "projects": parsed.projects,
                    "sections_detected": parsed.sections_detected,
                    "validation": validation,
                },

                # Phase 7 Results
                "ats_analysis": {
                    "score": ats_breakdown.total_score,
                    "breakdown": ats_breakdown.to_dict()["breakdown"],
                    "missing_skills": ats_breakdown.missing_skills[:5],
                    "improvement_tips": safe_execute(
                        "improvement_tips",
                        get_ats_improvement_tips,
                        ats_breakdown,
                        fallback_value=[]
                    ),
                },

                # Phase 8 Results
                "chat_ready": True,
                "chat_context_summary": f"Resume with {len(parsed.skills)} skills and ATS score {ats_breakdown.total_score}/100",

                # Phase 9 Results
                "progress": safe_execute(
                    "progress_retrieval",
                    self.progress_tracker.get_improvement_metrics,
                    fallback_value={}
                ),

                # Phase 11 Results
                "ml_prediction": ml_prediction,

                # Step 3 Results
                "ml_validation": {
                    "feature_analysis": validation_result.get("features", {}),
                    "prediction_debug": validation_result.get("prediction", {}),
                    "validation_status": "completed",
                },

                # Step 4 Results
                "ats_ml_alignment": {
                    "alignment_check": alignment_result,
                    "ats_score": ats_score,
                    "ml_probability": ml_probability,
                    "alignment_status": "completed",
                },

                # PHASE D: Intelligent Summary
                # Temporarily disabled due to circular reference issue
                "intelligent_summary": {
                    "summary": "Analysis completed successfully",
                    "quality_assessment": "UNKNOWN",
                    "priority_actions": [],
                    "ats_score": ats_breakdown.total_score,
                    "ml_probability": ml_prediction.get("probability", 0),
                },
            }

            duration = time.time() - start_time
            logger.info(f"Complete resume analysis finished in {duration:.2f}s - Status: {complete_result['status']}")

            return complete_result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Pipeline failed after {duration:.2f}s: {str(e)}")

            # Return safe fallback response
            return create_safe_response(
                status="failed",
                message="Resume analysis failed",
                error=str(e),
                data={
                    "file_path": file_path,
                    "duration": round(duration, 2),
                }
            )
    
    def chat_with_context(self, question: str, resume_id: int) -> Dict[str, Any]:
        """
        Chat about resume with context
        
        Phase 8 integration with database context
        """
        # Get analysis from database
        resume = db.get_resume(resume_id)
        if not resume:
            return {
                "error": "Resume not found",
                "status": "failed"
            }
        
        # Get latest analysis
        history = db.get_resume_history(resume_id, limit=1)
        if not history:
            return {
                "error": "No analysis found for this resume",
                "status": "failed"
            }
        
        latest_analysis = history[0]
        
        # Prepare context
        context = {
            "ats_score": latest_analysis.get("ats_score"),
            "breakdown": latest_analysis.get("breakdown"),
            "skills_found": latest_analysis.get("skills", []),
            "missing_skills": latest_analysis.get("missing_skills"),
            "formatting_issues": latest_analysis.get("formatting_issues"),
        }
        
        # Get chat response (Phase 8)
        response = chat_assistant(question, context)
        
        return {
            "status": "success",
            "question": question,
            "response": response.to_dict() if hasattr(response, 'to_dict') else response,
        }
    
    def generate_intelligent_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PHASE D-16: Generate intelligent summary with feature importance insights
        
        PHASE 11: Basic summary generation
        PHASE 14: Include top contributing factors
        PHASE 15: Track model version in summary
        PHASE 16: Include validation status and confidence thresholds
        """
        ats_score = analysis_data.get("ats_analysis", {}).get("score", 0)
        ml_prediction = analysis_data.get("ml_prediction", {})
        skills = analysis_data.get("parsing", {}).get("skills", [])
        skill_categories = analysis_data.get("parsing", {}).get("skill_categories", {})
        
        # Determine quality assessment
        probability = ml_prediction.get("probability", 0)
        ats_score_norm = ats_score / 100.0

        if ats_score >= 80 and probability >= 0.75:
            summary = "✅ Strong resume with excellent ATS compatibility and shortlisting potential."
            quality = "STRONG"
        elif ats_score >= 70 or probability >= 0.65:
            summary = "⚡ Good foundation with room for targeted improvements to increase competitiveness."
            quality = "GOOD"
        else:
            summary = "📚 Resume needs stronger alignment, clearer achievements, and better formatting to attract recruiters."
            quality = "NEEDS_IMPROVEMENT"

        # Generate priority actions
        priority_actions = []

        if ats_score < 70:
            priority_actions.append("Optimize keywords and skills section for better ATS scoring")
        if len(skills) < 8:
            priority_actions.append("Add more technical skills relevant to your target roles")
        if probability < 0.6:
            priority_actions.append("Focus on quantifiable achievements and metrics")
        if len(skill_categories) < 3:
            priority_actions.append("Diversify skill categories (technical, soft skills, tools)")

        # Add role-specific suggestions
        if "python" in [s.lower() for s in skills]:
            priority_actions.append("Highlight Python projects and frameworks used")
        if "javascript" in [s.lower() for s in skills]:
            priority_actions.append("Add React/Vue/Angular experience if applicable")

        why_score = ml_prediction.get("why_score", ml_prediction.get("reasoning", []))
        fix_priorities = ml_prediction.get("fix_priorities", priority_actions)
        
        # PHASE 14: Include top contributing factors
        top_factors = ml_prediction.get("top_factors", [])
        
        # PHASE 16: Determine if human validation is recommended (low confidence)
        confidence_level = ml_prediction.get("confidence", "Medium")
        needs_validation = probability < 0.65 or ats_score < 50
        
        # PHASE 15: Track model version
        model_version = ml_prediction.get("validation_round", "PHASE_12_EVALUATED")

        return {
            "summary": summary,
            "quality_assessment": quality,
            "priority_actions": fix_priorities[:5],  # Limit to top 5
            "why_this_score": why_score[:4] if why_score else [],
            "what_to_fix_first": fix_priorities[:4] if fix_priorities else [],
            "confidence_level": confidence_level,
            "top_factors": top_factors,  # PHASE 14: Feature importance
            "needs_human_review": needs_validation,  # PHASE 16: Validation flag
            "model_version": model_version,  # PHASE 15: Version tracking
            "ats_score": ats_score,
            "ml_probability": round(probability, 2),
            "total_skills": len(skills),
        }
        """
        Get progress report for resume
        
        Phase 9 integration with database
        """
        stats = db.get_user_statistics(resume_id)
        progress = db.get_progress(resume_id)
        
        return {
            "status": "success",
            "statistics": stats,
            "latest_progress": progress,
            "metrics": self.progress_tracker.get_improvement_metrics(),
        }