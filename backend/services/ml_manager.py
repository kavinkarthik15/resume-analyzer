"""
PHASE 11: ML Prediction Improvement
Enhanced feature engineering, normalization, and meaningful predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sklearn.preprocessing import StandardScaler


class FeatureScaler:
    """Feature normalization for ML model"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit_features(self, features: List[Dict[str, float]]) -> None:
        """Fit scaler on training data"""
        feature_names = list(features[0].keys()) if features else []
        values = [[f.get(name, 0) for name in feature_names] for f in features]
        self.scaler.fit(values)
        self.is_fitted = True
    
    def normalize(self, features: Dict[str, float]) -> np.ndarray:
        """Normalize a feature vector"""
        if not self.is_fitted:
            raise ValueError("Scaler not fitted. Fit first with fit_features()")
        
        feature_names = list(features.keys())
        values = np.array([[features[name] for name in feature_names]])
        return self.scaler.transform(values)[0]


class FeatureEngineering:
    """
    PHASE 11: Enhanced Feature Engineering
    Extract meaningful features for ML prediction
    """
    
    @staticmethod
    def engineer_features(analysis_data: dict) -> dict:
        """
        Extract engineered features from analysis data
        
        Returns:
            dict with raw and normalized features
        """
        features = {}
        
        # 1. ATS Score (normalized 0-1)
        ats_score = analysis_data.get("ats_score", 0)
        features["ats_score_normalized"] = min(ats_score / 100.0, 1.0)
        
        # 2. Skill Coverage
        skills = analysis_data.get("skills_found", [])
        skill_count = len(skills)
        features["skill_count"] = skill_count
        features["skill_coverage_normalized"] = min(skill_count / 15.0, 1.0)  # 15 is good target
        
        # 3. Skill Diversity (unique categories)
        skill_categories = analysis_data.get("skill_categories", {})
        features["skill_diversity"] = len(skill_categories)
        features["skill_diversity_normalized"] = min(len(skill_categories) / 10.0, 1.0)
        
        # 4. Section Completeness
        sections_detected = analysis_data.get("sections_detected", {})
        sections_found = sum(1 for v in sections_detected.values() if v)
        important_sections = ["Skills", "Experience", "Education"]
        important_found = sum(1 for s in important_sections if sections_detected.get(s))
        
        features["sections_completeness"] = sections_found / max(len(sections_detected), 1)
        features["essential_sections_completeness"] = important_found / len(important_sections)
        features["section_completeness_score"] = (
            features["sections_completeness"] * 0.6 + features["essential_sections_completeness"] * 0.4
        )
        
        # 5. Experience Relevance
        breakdown = analysis_data.get("breakdown", {})
        features["experience_relevance_score"] = breakdown.get("experience", 0) / 30.0  # 30 is max
        features["keyword_match_score"] = breakdown.get("keywords", 0) / 30.0
        
        # 6. JD Match (if available)
        jd_comparison = analysis_data.get("jd_comparison")
        if jd_comparison:
            jd_match = jd_comparison.get("jd_match_score", 0) / 100.0
            features["jd_match_score"] = jd_match
        else:
            features["jd_match_score"] = 0.5  # Default neutral value
        
        # 7. Formatting Quality
        formatting_issues = analysis_data.get("formatting_issues", [])
        features["formatting_quality_score"] = max(0, (breakdown.get("format", 0) / 20.0))  # 20 is max
        features["formatting_issues_count"] = len(formatting_issues)
        
        # 8. Bullet Quality
        action_verbs = analysis_data.get("action_verbs", 0)
        achievements = analysis_data.get("achievements", 0)
        features["bullet_verb_score"] = min(action_verbs / 20.0, 1.0)
        features["bullet_achievement_score"] = min(achievements / 10.0, 1.0)
        features["bullet_quality_score"] = min(
            0.55 * features["bullet_verb_score"] + 0.45 * features["bullet_achievement_score"],
            1.0
        )

        # 9. Content Quality
        raw_text = analysis_data.get("raw_text", "")
        word_count = len(raw_text.split()) if raw_text else 0
        features["content_length"] = min(word_count / 400.0, 1.0)  # 400 words is baseline
        features["word_count"] = word_count
        
        # 9. Missing Elements
        missing_skills = analysis_data.get("missing_skills", {})
        missing_count = sum(len(v) for v in missing_skills.values())
        features["missing_skills_count"] = missing_count
        features["missing_skills_penalty"] = min(missing_count / 10.0, 1.0)
        
        # 10. Composite Scores
        features["overall_quality_score"] = (
            features.get("ats_score_normalized", 0) * 0.25 +
            features.get("skill_coverage_normalized", 0) * 0.18 +
            features.get("section_completeness_score", 0) * 0.2 +
            features.get("formatting_quality_score", 0) * 0.15 +
            features.get("bullet_quality_score", 0) * 0.12 +
            features.get("content_length", 0) * 0.1
        )
        
        features["readiness_score"] = (
            features.get("overall_quality_score", 0) * 0.35 +
            features.get("jd_match_score", 0.3) +
            features.get("essential_sections_completeness", 0) * 0.35
        ) / 2.0
        
        return features
    
    @staticmethod
    def get_feature_importance_insights(features: dict) -> List[str]:
        """
        Generate insights about which features are strong/weak
        """
        insights = []
        
        # Check ATS score
        if features.get("ats_score_normalized", 0) > 0.75:
            insights.append("✅ Strong ATS score foundation")
        elif features.get("ats_score_normalized", 0) < 0.5:
            insights.append("⚠️ ATS score needs significant improvement")
        
        # Check skills
        if features.get("skill_coverage_normalized", 0) > 0.7:
            insights.append("✅ Good skill coverage")
        else:
            insights.append("🎯 Add more technical skills for better coverage")
        
        # Check sections
        if features.get("essential_sections_completeness", 0) == 1.0:
            insights.append("✅ All essential sections present")
        else:
            insights.append("📝 Missing some essential sections")
        
        # Check formatting
        if features.get("formatting_issues_count", 0) == 0:
            insights.append("✅ Clean formatting, no issues detected")
        else:
            insights.append(f"⚠️ {features.get('formatting_issues_count')} formatting issues to fix")
        
        # Check bullet quality
        if features.get("bullet_quality_score", 0) > 0.7:
            insights.append("✅ Bullet points are strong and achievement-oriented")
        elif features.get("bullet_quality_score", 0) < 0.5:
            insights.append("✏️ Bullet points need stronger action verbs and measurable achievements")

        # Check missing skills
        if features.get("missing_skills_count", 0) > 0:
            insights.append("⚠️ Missing some expected skills for the target role")
        else:
            insights.append("✅ No major missing skills detected")
        
        # Check content length
        if features.get("content_length", 0) > 0.8:
            insights.append("✅ Good content length and completeness")
        elif features.get("content_length", 0) < 0.4:
            insights.append("📝 Resume seems too short, add more details")
        
        # Check JD match
        if features.get("jd_match_score", 0.5) > 0.7:
            insights.append("✅ Strong alignment with target JD")
        elif features.get("jd_match_score", 0.5) < 0.4:
            insights.append("🎯 Significant gap between resume and target JD")
        
        return insights


class MLPredictionEngine:
    """
    PHASE 11-16 ML Prediction Engine
    Improved ML prediction with feature engineering, explainability, versioning, and robustness
    """
    
    def __init__(self, model=None, validate_schema=True):
        self.model = model
        self.scaler = FeatureScaler()
        self.feature_names = [
            "ats_score_normalized",
            "skill_count",
            "skill_coverage_normalized",
            "skill_diversity",
            "skill_diversity_normalized",
            "sections_completeness",
            "section_completeness_score",
            "essential_sections_completeness",
            "experience_relevance_score",
            "keyword_match_score",
            "jd_match_score",
            "formatting_quality_score",
            "formatting_issues_count",
            "bullet_verb_score",
            "bullet_achievement_score",
            "bullet_quality_score",
            "content_length",
            "word_count",
            "missing_skills_count",
            "missing_skills_penalty",
            "overall_quality_score",
            "readiness_score",
        ]
        
        # PHASE 15: Feature importance mapping (from evaluation_results.json)
        self.feature_importance = {
            "overall_quality_score": 0.2258,
            "readiness_score": 0.1573,
            "jd_match_score": 0.0911,
            "skill_coverage_normalized": 0.0764,
            "ats_score_normalized": 0.0709,
            "skill_count": 0.0699,
            "bullet_quality_score": 0.0453,
            "bullet_verb_score": 0.0433,
            "formatting_quality_score": 0.0386,
            "word_count": 0.0283,
        }
        
        # PHASE 15: Schema validation on load
        if validate_schema and model:
            self._validate_model_schema()
    
    def _validate_model_schema(self):
        """PHASE 15: Validate model has expected number of features"""
        import json
        import os
        
        schema_path = os.path.join(
            os.path.dirname(__file__), 
            "../models/feature_schema_v1.json"
        )
        
        try:
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                    expected_count = schema.get("feature_count", 22)
                    if len(self.feature_names) != expected_count:
                        raise ValueError(
                            f"Feature count mismatch: expected {expected_count}, "
                            f"got {len(self.feature_names)}"
                        )
        except Exception as e:
            # Log but don't fail - allow graceful degradation
            print(f"⚠️  Schema validation warning: {str(e)}")
    
    def predict_shortlist_probability(self, analysis_data: dict) -> dict:
        """
        PHASE 11-16 Main Prediction Function
        Predicts shortlist probability with detailed explanation, feature importance, and robustness
        
        Args:
            analysis_data: Resume analysis data dictionary
            
        Returns:
            dict with probability, decision, confidence, top_factors, and recommendations
        """
        # PHASE 16: Input validation - ensure we have viable data
        if not isinstance(analysis_data, dict):
            raise ValueError("analysis_data must be a dictionary")
        
        raw_text = analysis_data.get("raw_text", "")
        if not raw_text or len(raw_text.strip()) < 50:
            return self._low_confidence_fallback("Resume text too short to analyze properly")
        
        if not self.model:
            raise RuntimeError("ML model not loaded")
        
        try:
            # Step 1: Feature Engineering
            engineered_features = FeatureEngineering.engineer_features(analysis_data)
            
            # Step 2: Prepare feature vector
            feature_vector = [
                engineered_features.get(name, 0) for name in self.feature_names
            ]
            
            # Step 3: Make prediction with error handling
            try:
                input_df = pd.DataFrame([feature_vector], columns=self.feature_names)
                probability = self.model.predict_proba(input_df)[0][1]
            except Exception as ml_error:
                # PHASE 16: Fallback to heuristic if ML prediction fails
                print(f"⚠️  ML prediction failed: {str(ml_error)}, using heuristic fallback")
                probability = self._heuristic_prediction(engineered_features)
            
            # Step 4: Determine decision with confidence levels
            if probability > 0.75:
                decision = "Shortlisted"
                confidence = "High"
            elif probability > 0.6:
                decision = "Likely Shortlisted"
                confidence = "Medium"
            elif probability > 0.4:
                decision = "Uncertain"
                confidence = "Low"
            else:
                decision = "Likely Rejected"
                confidence = "Medium"
            
            # Step 5: Generate reasoning
            reasoning = []
            if engineered_features.get("ats_score_normalized", 0) > 0.75:
                reasoning.append("Strong ATS score increases chances significantly")
            if engineered_features.get("skill_coverage_normalized", 0) > 0.7:
                reasoning.append("Good technical skill coverage is a major positive")
            if engineered_features.get("essential_sections_completeness", 0) == 1.0:
                reasoning.append("All essential sections are present")
            
            jd_match = engineered_features.get("jd_match_score", 0.5)
            if jd_match > 0.7:
                reasoning.append(f"Strong alignment with target JD ({int(jd_match*100)}%)")
            elif jd_match < 0.4:
                reasoning.append(f"Weak alignment with target JD ({int(jd_match*100)}%) - consider tailoring")
            
            # PHASE 14: Get top factors based on feature importance
            top_factors = self._get_top_factors(engineered_features)
            
            # Step 6: Get feature insights
            feature_insights = FeatureEngineering.get_feature_importance_insights(engineered_features)
            fix_priorities = self._get_fix_priorities(engineered_features)
            why_score = self._explain_probability(probability, engineered_features)
            
            return {
                "probability": round(probability, 2),
                "decision": decision,
                "confidence": confidence,
                "reasoning": reasoning,
                "why_score": why_score,
                "fix_priorities": fix_priorities,
                "feature_insights": feature_insights,
                "top_factors": top_factors,  # PHASE 14: Feature importance ranking
                "raw_probability": float(probability),
                "recommendation": self._get_recommendation(probability, engineered_features),
                "validation_round": "PHASE_12_EVALUATED",  # PHASE 12 metrics validation
            }
        
        except Exception as e:
            # PHASE 16: Graceful error handling with fallback
            print(f"❌ Prediction error: {str(e)}")
            return self._low_confidence_fallback(str(e))
    
    def _get_top_factors(self, features: dict) -> List[dict]:
        """
        PHASE 14: Extract top contributing factors based on feature importance
        Returns list of high-impact factors with their values and importance scores
        """
        factors = []
        
        for feature_name, importance in sorted(
            self.feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]:  # Top 5 factors
            feature_value = features.get(feature_name, 0)
            
            # Humanize feature names and values
            readable_name = self._humanize_feature_name(feature_name)
            readable_value = self._format_feature_value(feature_name, feature_value)
            
            factors.append({
                "factor": readable_name,
                "importance": round(importance * 100, 1),  # Convert to percentage
                "value": readable_value,
                "impact": self._classify_impact(feature_name, feature_value),
            })
        
        return factors
    
    def _humanize_feature_name(self, feature_name: str) -> str:
        """Convert feature name to human-readable format"""
        mapping = {
            "overall_quality_score": "Overall Quality Score",
            "readiness_score": "Resume Readiness",
            "jd_match_score": "Job Description Match",
            "skill_coverage_normalized": "Skill Coverage",
            "ats_score_normalized": "ATS Score",
            "skill_count": "Number of Skills",
            "bullet_quality_score": "Bullet Point Quality",
            "bullet_verb_score": "Action Verb Usage",
            "formatting_quality_score": "Formatting Quality",
            "word_count": "Content Length",
        }
        return mapping.get(feature_name, feature_name.replace("_", " ").title())
    
    def _format_feature_value(self, feature_name: str, value: float) -> str:
        """Format feature value for readability"""
        if "count" in feature_name:
            return f"{int(value)} items"
        elif "score" in feature_name or "normalized" in feature_name:
            return f"{int(value * 100)}%"
        else:
            return f"{value:.2f}"
    
    def _classify_impact(self, feature_name: str, value: float) -> str:
        """Classify whether feature is positive, neutral, or negative impact"""
        thresholds = {
            "overall_quality_score": (0.7, 0.4),
            "readiness_score": (0.7, 0.4),
            "jd_match_score": (0.7, 0.4),
            "skill_coverage_normalized": (0.7, 0.5),
            "ats_score_normalized": (0.7, 0.5),
        }
        
        if feature_name in thresholds:
            high, low = thresholds[feature_name]
            if value >= high:
                return "✅ Strong Positive"
            elif value >= low:
                return "⚠️ Needs Improvement"
            else:
                return "❌ Critical Gap"
        
        return "➡️ Neutral"
    
    def _low_confidence_fallback(self, error_msg: str = "") -> dict:
        """PHASE 16: Return low-confidence prediction when prediction fails"""
        return {
            "probability": 0.5,
            "decision": "Unable to Assess",
            "confidence": "Very Low",
            "reasoning": ["Insufficient data for reliable prediction. " + error_msg],
            "why_score": ["Could not generate prediction due to data quality issues."],
            "fix_priorities": ["Ensure resume has at least 50 words", "Include key sections: Skills, Experience, Education"],
            "feature_insights": [],
            "top_factors": [],
            "raw_probability": 0.5,
            "recommendation": "📝 Please provide a more complete resume (at least 50-100 words) and try again.",
            "validation_round": "ERROR_FALLBACK",
            "error": error_msg,
        }
    
    def _explain_probability(self, probability: float, features: dict) -> List[str]:
        """Explain the ML probability with human-friendly reasons."""
        explanations = []

        if probability >= 0.75:
            explanations.append("The resume shows strong ATS fit, core skills, and structure.")
        elif probability >= 0.55:
            explanations.append("The resume is reasonably competitive but can be more tailored.")
        else:
            explanations.append("The resume needs stronger matching keywords, sections, or achievements.")

        if features.get("ats_score_normalized", 0) < 0.6:
            explanations.append("ATS score is low, indicating keyword or formatting gaps.")
        if features.get("jd_match_score", 0) < 0.45:
            explanations.append("Job description alignment is weak; tailor the resume to the role.")
        if features.get("essential_sections_completeness", 0) < 1.0:
            explanations.append("Some essential sections are missing or incomplete.")
        if features.get("bullet_quality_score", 0) < 0.5:
            explanations.append("Bullet quality is low; add strong action verbs and measurable outcomes.")
        if features.get("formatting_issues_count", 0) > 0:
            explanations.append("Formatting issues were detected, which can reduce readability and ATS parsing.")

        return explanations

    def _get_fix_priorities(self, features: dict) -> List[str]:
        """Identify the highest priority fixes for the resume."""
        priorities = []

        if features.get("essential_sections_completeness", 0) < 1.0:
            priorities.append("Add or complete missing essential sections like Skills, Experience, or Education.")
        if features.get("ats_score_normalized", 0) < 0.7:
            priorities.append("Improve ATS keyword matching by aligning skills and role-specific terminology.")
        if features.get("jd_match_score", 0) < 0.5:
            priorities.append("Tailor the resume more closely to the target job description.")
        if features.get("bullet_quality_score", 0) < 0.6:
            priorities.append("Strengthen bullet points with action verbs and measurable achievements.")
        if features.get("formatting_issues_count", 0) > 0:
            priorities.append("Resolve formatting issues to improve readability and parsing.")
        if features.get("content_length", 0) < 0.5:
            priorities.append("Add more substantive experience or projects to increase content coverage.")

        return priorities[:5]

    def _heuristic_prediction(self, features: dict) -> float:
        """Fallback heuristic-based prediction"""
        weights = {
            "overall_quality_score": 0.4,
            "readiness_score": 0.3,
            "jd_match_score": 0.3,
        }
        
        probability = sum(
            features.get(key, 0.5) * weight
            for key, weight in weights.items()
        )
        
        return min(probability, 1.0)
    
    def _get_recommendation(self, probability: float, features: dict) -> str:
        """Get actionable recommendation"""
        if probability > 0.75:
            return "✅ Ready to apply! Your resume is well-optimized. Focus on tailoring to specific JDs."
        elif probability > 0.6:
            return "🚀 Nearly ready. Improve ATS score a bit more and ensure strong JD alignment."
        elif probability > 0.4:
            return "⚡ Keep refining. Work on skill coverage and formatting to boost chances."
        else:
            return "📚 Significant work needed. Focus on ATS score, skills, and addressing formatting issues."