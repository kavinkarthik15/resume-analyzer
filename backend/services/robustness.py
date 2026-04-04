"""
PHASE 16: Robustness & Error Handling
Input validation, graceful fallback, timeout protection, and enhanced logging
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
import time


class InputValidator:
    """PHASE 16: Comprehensive input validation for resume analysis"""
    
    # Validation rules
    MINIMUM_TEXT_LENGTH = 50  # characters
    MAXIMUM_TEXT_LENGTH = 50000  # characters
    MINIMUM_SKILL_COUNT = 1
    MAXIMUM_SKILL_COUNT = 200
    EXPECTED_FEATURE_COUNT = 22
    
    @staticmethod
    def validate_resume_text(raw_text: str) -> Tuple[bool, Optional[str]]:
        """Validate resume text input"""
        if not isinstance(raw_text, str):
            return False, "Resume must be text input"
        
        if len(raw_text.strip()) < InputValidator.MINIMUM_TEXT_LENGTH:
            return False, f"Resume too short (minimum {InputValidator.MINIMUM_TEXT_LENGTH} characters)"
        
        if len(raw_text) > InputValidator.MAXIMUM_TEXT_LENGTH:
            return False, f"Resume too long (maximum {InputValidator.MAXIMUM_TEXT_LENGTH} characters)"
        
        # Check for presence of meaningful content (not just numbers/symbols)
        words = raw_text.split()
        if len(words) < 10:
            return False, "Resume must contain at least 10 words"
        
        return True, None
    
    @staticmethod
    def validate_skills_list(skills: list) -> Tuple[bool, Optional[str]]:
        """Validate skills input"""
        if not isinstance(skills, list):
            return False, "Skills must be a list"
        
        if len(skills) < InputValidator.MINIMUM_SKILL_COUNT:
            return False, f"At least {InputValidator.MINIMUM_SKILL_COUNT} skill required"
        
        if len(skills) > InputValidator.MAXIMUM_SKILL_COUNT:
            return False, f"Maximum {InputValidator.MAXIMUM_SKILL_COUNT} skills allowed"
        
        # Validate each skill is string
        for skill in skills:
            if not isinstance(skill, str) or len(skill.strip()) == 0:
                return False, "All skills must be non-empty strings"
        
        return True, None
    
    @staticmethod
    def validate_analysis_data(analysis_data: dict) -> Tuple[bool, Optional[str]]:
        """Comprehensive validation of analysis data"""
        if not isinstance(analysis_data, dict):
            return False, "Analysis data must be a dictionary"
        
        required_fields = ["raw_text", "ats_score", "breakdown"]
        for field in required_fields:
            if field not in analysis_data:
                return False, f"Missing required field: {field}"
        
        # Validate raw text
        is_valid, error = InputValidator.validate_resume_text(analysis_data.get("raw_text", ""))
        if not is_valid:
            return False, f"Invalid resume text: {error}"
        
        # Validate ATS score
        ats_score = analysis_data.get("ats_score")
        if not isinstance(ats_score, (int, float)) or not (0 <= ats_score <= 100):
            return False, "ATS score must be between 0 and 100"
        
        return True, None


class FallbackPrediction:
    """PHASE 16: Fallback prediction logic when ML fails"""
    
    @staticmethod
    def get_heuristic_decision(analysis_data: dict) -> Dict[str, Any]:
        """
        Generate prediction using heuristic rules when ML is unavailable
        
        Rules:
        - ATS score > 75 AND skills > 8 → Shortlist
        - ATS score < 50 OR skills < 3 → Reject
        - Otherwise → Uncertain
        """
        ats_score = analysis_data.get("ats_score", 0)
        skills = analysis_data.get("skills_found", [])
        
        if ats_score > 75 and len(skills) > 8:
            probability = 0.78
            decision = "Shortlisted"
            confidence = "High"
        elif ats_score < 50 or len(skills) < 3:
            probability = 0.25
            decision = "Likely Rejected"
            confidence = "High"
        else:
            probability = 0.5
            decision = "Uncertain"
            confidence = "Low"
        
        return {
            "probability": probability,
            "decision": decision,
            "confidence": confidence,
            "reasoning": ["Using heuristic fallback (ML unavailable)"],
            "why_score": ["Fallback: Based on ATS score and skill count"],
            "fix_priorities": ["Unable to generate specific recommendations without ML"],
            "fallback_used": True,
            "fallback_reason": "ML prediction unavailable",
        }


class RobustPredictionEngine:
    """PHASE 16: Wrapper around ML prediction with comprehensive error handling"""
    
    def __init__(self, ml_engine, timeout_seconds=10):
        self.ml_engine = ml_engine
        self.timeout_seconds = timeout_seconds
        self.logger = logging.getLogger(__name__)
        self.prediction_log = []
    
    def predict_with_robustness(self, analysis_data: dict) -> Dict[str, Any]:
        """
        Predict with validation, fallback, and timeout protection
        
        Process:
        1. Validate input
        2. Attempt ML prediction (with timeout)
        3. Fallback to heuristic if ML fails
        4. Log all decisions for debugging
        5. Return result with metadata
        """
        prediction_start = time.time()
        
        # PHASE 16: Input validation
        is_valid, validation_error = InputValidator.validate_analysis_data(analysis_data)
        if not is_valid:
            self.logger.warning(f"Input validation failed: {validation_error}")
            return {
                "error": validation_error,
                "probability": 0.5,
                "decision": "Unable to Assess",
                "confidence": "Very Low",
                "validation_failed": True,
            }
        
        # PHASE 16: Attempt ML prediction with timeout
        try:
            self.logger.info(f"Starting prediction for resume ({len(analysis_data.get('raw_text', ''))} chars)")
            
            # Set timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Prediction exceeded {self.timeout_seconds}s timeout")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout_seconds)
            
            try:
                result = self.ml_engine.predict_shortlist_probability(analysis_data)
                signal.alarm(0)  # Cancel timeout
            except TimeoutError:
                signal.alarm(0)  # Cancel timeout
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
            
            prediction_duration = time.time() - prediction_start
            result["prediction_duration_ms"] = round(prediction_duration * 1000, 2)
            result["validation_status"] = "PHASE_12_VALIDATED"
            
            self.logger.info(f"Prediction succeeded in {result['prediction_duration_ms']}ms: {result.get('decision')}")
            self._log_prediction(analysis_data, result, "SUCCESS")
            
            return result
        
        except TimeoutError as e:
            # PHASE 16: Timeout protection - use fallback
            self.logger.error(f"Prediction timeout: {str(e)}")
            result = FallbackPrediction.get_heuristic_decision(analysis_data)
            result["timeout_error"] = True
            result["error"] = str(e)
            
            prediction_duration = time.time() - prediction_start
            result["prediction_duration_ms"] = round(prediction_duration * 1000, 2)
            
            self._log_prediction(analysis_data, result, "TIMEOUT_FALLBACK")
            return result
        
        except Exception as e:
            # PHASE 16: Generic error handling - use fallback
            self.logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            result = FallbackPrediction.get_heuristic_decision(analysis_data)
            result["ml_error"] = True
            result["error"] = str(e)
            
            prediction_duration = time.time() - prediction_start
            result["prediction_duration_ms"] = round(prediction_duration * 1000, 2)
            
            self._log_prediction(analysis_data, result, "ERROR_FALLBACK")
            return result
    
    def _log_prediction(self, analysis_data: dict, result: dict, status: str) -> None:
        """PHASE 16: Enhanced logging for debugging and monitoring"""
        log_entry = {
            "timestamp": time.time(),
            "status": status,
            "input_size": len(analysis_data.get("raw_text", "")),
            "ats_score": analysis_data.get("ats_score"),
            "skill_count": len(analysis_data.get("skills_found", [])),
            "prediction": result.get("decision"),
            "probability": result.get("probability"),
            "confidence": result.get("confidence"),
            "duration_ms": result.get("prediction_duration_ms"),
            "fallback_used": result.get("fallback_used", False),
            "error": result.get("error"),
        }
        
        self.prediction_log.append(log_entry)
        
        # Log as JSON for parsing
        json_log = json.dumps(log_entry)
        self.logger.info(f"PREDICTION_LOG: {json_log}")
    
    def get_prediction_metrics(self) -> Dict[str, Any]:
        """Get aggregated prediction metrics for monitoring"""
        if not self.prediction_log:
            return {"total_predictions": 0}
        
        total = len(self.prediction_log)
        successful = sum(1 for p in self.prediction_log if p["status"] == "SUCCESS")
        fallbacks = sum(1 for p in self.prediction_log if "FALLBACK" in p["status"])
        errors = sum(1 for p in self.prediction_log if "ERROR" in p["status"])
        
        avg_duration = sum(p.get("duration_ms", 0) for p in self.prediction_log) / max(total, 1)
        
        return {
            "total_predictions": total,
            "successful": successful,
            "success_rate_percent": round((successful / max(total, 1)) * 100, 2),
            "fallbacks_triggered": fallbacks,
            "errors": errors,
            "average_duration_ms": round(avg_duration, 2),
            "last_prediction": self.prediction_log[-1] if self.prediction_log else None,
        }


class EnhancedLogger:
    """PHASE 16: Enhanced logging for debugging and monitoring"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup console and file handlers"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_prediction_start(self, file_name: str, resume_size: int):
        """Log prediction start"""
        self.logger.info(f"📋 Starting analysis: {file_name} ({resume_size} chars)")
    
    def log_prediction_complete(self, decision: str, probability: float, duration: float):
        """Log prediction completion"""
        self.logger.info(f"✅ Prediction complete: {decision} (prob={probability:.2f}, {duration:.2f}ms)")
    
    def log_error(self, phase: str, error: str):
        """Log phase-specific error"""
        self.logger.error(f"❌ {phase} failed: {error}")
    
    def log_validation(self, field: str, valid: bool, detail: str):
        """Log validation result"""
        status = "✅" if valid else "⚠️"
        self.logger.info(f"{status} {field}: {detail}")
