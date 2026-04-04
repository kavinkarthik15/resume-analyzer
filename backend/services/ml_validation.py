"""
STEP 3: ML Prediction Validation
Sanity checks and debugging for ML predictions
"""

import numpy as np
from typing import Dict, List, Any, Optional
from backend.services.ml_manager import MLPredictionEngine, FeatureEngineering


class MLValidator:
    """
    STEP 3: ML Prediction Validation
    Validate predictions with sanity checks and debugging
    """

    def __init__(self, ml_engine: MLPredictionEngine):
        self.ml_engine = ml_engine
        self.validation_results = []

    def create_sanity_test_cases(self) -> List[Dict[str, Any]]:
        """Create test cases for ML prediction validation"""

        return [
            {
                "name": "Strong Resume",
                "description": "High ATS score, many skills, complete sections",
                "data": {
                    "ats_score": 85,
                    "skills_found": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS"],
                    "skill_frequency": {"Python": 3, "JavaScript": 2, "React": 2, "SQL": 2},
                    "sections_detected": {
                        "Skills": True, "Experience": True, "Education": True,
                        "Projects": True, "Summary": True
                    },
                    "missing_skills": {},
                    "formatting_issues": [],
                    "raw_text": "Senior developer with extensive experience...",
                },
                "expected_probability_range": (0.7, 1.0),
                "expected_decision": "Shortlisted",
            },
            {
                "name": "Weak Resume",
                "description": "Low ATS score, few skills, missing sections",
                "data": {
                    "ats_score": 35,
                    "skills_found": ["Basic Computer Skills"],
                    "skill_frequency": {"Basic Computer Skills": 1},
                    "sections_detected": {
                        "Skills": False, "Experience": True, "Education": False,
                        "Projects": False, "Summary": False
                    },
                    "missing_skills": {"Programming Languages": ["Python", "Java"]},
                    "formatting_issues": ["Too short", "No bullet points"],
                    "raw_text": "Entry level position...",
                },
                "expected_probability_range": (0.0, 0.3),
                "expected_decision": "Rejected",
            },
            {
                "name": "Medium Resume",
                "description": "Moderate ATS score, some skills, partial sections",
                "data": {
                    "ats_score": 55,
                    "skills_found": ["Python", "SQL", "Excel"],
                    "skill_frequency": {"Python": 1, "SQL": 1, "Excel": 1},
                    "sections_detected": {
                        "Skills": True, "Experience": True, "Education": True,
                        "Projects": False, "Summary": False
                    },
                    "missing_skills": {"Web Development": ["JavaScript", "HTML"]},
                    "formatting_issues": ["Could use more bullet points"],
                    "raw_text": "Developer with some experience...",
                },
                "expected_probability_range": (0.3, 0.7),
                "expected_decision": "Uncertain",
            },
        ]

    def validate_prediction(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single prediction"""

        # Get prediction
        try:
            prediction = self.ml_engine.predict_shortlist_probability(test_case["data"])
        except Exception as e:
            return {
                "test_name": test_case["name"],
                "status": "ERROR",
                "error": str(e),
                "expected_range": test_case["expected_probability_range"],
            }

        probability = prediction.get("probability", 0)
        decision = prediction.get("decision", "Unknown")
        expected_range = test_case["expected_probability_range"]
        expected_decision = test_case["expected_decision"]

        # Check if probability is in expected range
        in_range = expected_range[0] <= probability <= expected_range[1]

        # Check if decision matches expectation
        decision_match = self._decision_matches_expectation(decision, expected_decision)

        # Feature debugging
        features = FeatureEngineering.engineer_features(test_case["data"])
        feature_debug = self._analyze_feature_contributions(features, probability)

        return {
            "test_name": test_case["name"],
            "status": "PASS" if in_range and decision_match else "FAIL",
            "probability": probability,
            "decision": decision,
            "expected_range": expected_range,
            "expected_decision": expected_decision,
            "in_expected_range": in_range,
            "decision_matches": decision_match,
            "feature_analysis": feature_debug,
            "prediction_details": prediction,
        }

    def _decision_matches_expectation(self, actual_decision: str, expected_decision: str) -> bool:
        """Check if decision matches expected category"""

        # Map decisions to categories
        decision_categories = {
            "Shortlisted": ["Shortlisted", "Likely Shortlisted"],
            "Rejected": ["Rejected", "Likely Rejected"],
            "Uncertain": ["Uncertain"],
        }

        actual_category = None
        expected_category = None

        for category, decisions in decision_categories.items():
            if actual_decision in decisions:
                actual_category = category
            if expected_decision in decisions:
                expected_category = category

        return actual_category == expected_category

    def _analyze_feature_contributions(self, features: Dict[str, float],
                                     probability: float) -> Dict[str, Any]:
        """Analyze which features contribute most to prediction"""

        # Sort features by value (higher = more positive contribution)
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)

        # Identify key positive and negative factors
        positive_factors = []
        negative_factors = []

        for feature_name, value in sorted_features[:5]:  # Top 5
            if value >= 0.7:
                positive_factors.append(f"{feature_name}: {value:.2f}")
            elif value <= 0.3:
                negative_factors.append(f"{feature_name}: {value:.2f}")

        return {
            "top_positive_features": positive_factors,
            "top_negative_features": negative_factors,
            "probability_correlation": self._calculate_probability_correlation(features, probability),
            "feature_summary": f"Probability {probability:.2f} driven by {len(positive_factors)} strong factors",
        }

    def _calculate_probability_correlation(self, features: Dict[str, float],
                                         probability: float) -> str:
        """Calculate correlation between features and probability"""

        # Simple correlation analysis
        high_prob_features = sum(1 for v in features.values() if v >= 0.7)
        low_prob_features = sum(1 for v in features.values() if v <= 0.3)

        if probability >= 0.7 and high_prob_features >= 3:
            return "Strong positive correlation - features support high probability"
        elif probability <= 0.3 and low_prob_features >= 2:
            return "Strong negative correlation - features support low probability"
        elif 0.4 <= probability <= 0.6:
            return "Moderate correlation - features align with uncertain prediction"
        else:
            return "Weak correlation - prediction may not align with features"

    def run_sanity_checks(self) -> Dict[str, Any]:
        """Run all sanity checks"""

        test_cases = self.create_sanity_test_cases()
        results = []

        print("🔍 Running ML Prediction Sanity Checks...")

        for test_case in test_cases:
            result = self.validate_prediction(test_case)
            results.append(result)

            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "ERROR" else "⚠️"
            print(f"{status_emoji} {result['test_name']}: {result['status']}")

            if result["status"] == "FAIL":
                print(f"   Expected: {result['expected_range']}, Got: {result['probability']:.2f}")
                print(f"   Decision: Expected ~{result['expected_decision']}, Got: {result['decision']}")

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["status"] == "PASS")
        error_tests = sum(1 for r in results if r["status"] == "ERROR")

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "error_tests": error_tests,
            "pass_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
            "ml_reliability": "HIGH" if passed_tests == total_tests else "MEDIUM" if passed_tests >= total_tests * 0.7 else "LOW",
            "results": results,
        }

        print(f"\n📊 ML Validation Summary:")
        print(f"• Pass Rate: {summary['pass_rate']}%")
        print(f"• Errors: {error_tests}")
        print(f"• ML Reliability: {summary['ml_reliability']}")

        return summary

    def debug_feature_inputs(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Debug feature inputs for a specific analysis"""

        print("🔧 ML Feature Debug Information:")
        print("=" * 50)

        # Engineer features
        features = FeatureEngineering.engineer_features(analysis_data)

        print("📊 Engineered Features:")
        for feature_name, value in sorted(features.items(), key=lambda x: x[1], reverse=True):
            print(f"  {feature_name}: {value:.3f}")

        print("\n🎯 Key Resume Metrics:")
        print(f"  ATS Score: {analysis_data.get('ats_score', 0)}")
        print(f"  Skills Count: {len(analysis_data.get('skills_found', []))}")
        print(f"  Sections Found: {sum(analysis_data.get('sections_detected', {}).values())}")

        # Get prediction
        try:
            prediction = self.ml_engine.predict_shortlist_probability(analysis_data)
            print("\n🤖 ML Prediction:")
            print(f"  Probability: {prediction.get('probability', 0):.3f}")
            print(f"  Decision: {prediction.get('decision', 'Unknown')}")
            print(f"  Confidence: {prediction.get('confidence', 'Unknown')}")

            if prediction.get('reasoning'):
                print("\n💡 Reasoning:")
                for reason in prediction['reasoning'][:3]:
                    print(f"  • {reason}")

        except Exception as e:
            print(f"❌ Prediction Error: {str(e)}")

        return {
            "features": features,
            "prediction": prediction if 'prediction' in locals() else None,
            "analysis_data": analysis_data,
        }


def validate_ml_predictions(ml_engine: Optional[MLPredictionEngine] = None) -> Dict[str, Any]:
    """
    STEP 3 MAIN FUNCTION
    Run complete ML prediction validation
    """
    if ml_engine is None:
        # Create with no model for testing
        ml_engine = MLPredictionEngine(model=None)

    validator = MLValidator(ml_engine)
    return validator.run_sanity_checks()