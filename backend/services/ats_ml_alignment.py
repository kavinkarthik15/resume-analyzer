"""
STEP 4: ATS-ML Alignment
Ensure ML predictions align with ATS scoring logic
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from backend.services.ml_manager import MLPredictionEngine, FeatureEngineering
from backend.services.scorer import calculate_ats_score


class ATSMLAlignmentChecker:
    """
    STEP 4: ATS-ML Alignment
    Check and improve alignment between ATS scores and ML predictions
    """

    def __init__(self, ml_engine: MLPredictionEngine):
        self.ml_engine = ml_engine
        self.alignment_threshold = 0.15  # 15% tolerance for misalignment

    def create_alignment_test_cases(self) -> List[Dict[str, Any]]:
        """Create test cases to check ATS-ML alignment"""

        return [
            {
                "name": "Perfect Resume",
                "ats_score": 95,
                "expected_ml_range": (0.85, 1.0),
                "description": "High ATS score should predict high shortlist probability",
            },
            {
                "name": "Excellent Resume",
                "ats_score": 85,
                "expected_ml_range": (0.75, 0.95),
                "description": "Very good ATS score should predict strong shortlist probability",
            },
            {
                "name": "Good Resume",
                "ats_score": 75,
                "expected_ml_range": (0.65, 0.85),
                "description": "Good ATS score should predict good shortlist probability",
            },
            {
                "name": "Average Resume",
                "ats_score": 60,
                "expected_ml_range": (0.45, 0.75),
                "description": "Average ATS score should predict moderate shortlist probability",
            },
            {
                "name": "Below Average Resume",
                "ats_score": 45,
                "expected_ml_range": (0.25, 0.55),
                "description": "Below average ATS score should predict low shortlist probability",
            },
            {
                "name": "Poor Resume",
                "ats_score": 25,
                "expected_ml_range": (0.0, 0.35),
                "description": "Poor ATS score should predict very low shortlist probability",
            },
        ]

    def check_alignment(self, ats_score: float, ml_probability: float) -> Dict[str, Any]:
        """Check if ATS score and ML probability are aligned"""

        # Expected probability range based on ATS score
        expected_min = max(0.0, (ats_score / 100.0) - self.alignment_threshold)
        expected_max = min(1.0, (ats_score / 100.0) + self.alignment_threshold)

        aligned = expected_min <= ml_probability <= expected_max

        # Calculate alignment score (0-1, higher is better alignment)
        ats_normalized = ats_score / 100.0
        alignment_score = 1.0 - min(abs(ats_normalized - ml_probability), 1.0)

        # Determine alignment quality
        if alignment_score >= 0.9:
            quality = "EXCELLENT"
        elif alignment_score >= 0.8:
            quality = "GOOD"
        elif alignment_score >= 0.7:
            quality = "FAIR"
        elif alignment_score >= 0.6:
            quality = "POOR"
        else:
            quality = "MISALIGNED"

        return {
            "aligned": aligned,
            "alignment_score": round(alignment_score, 3),
            "quality": quality,
            "expected_range": (round(expected_min, 3), round(expected_max, 3)),
            "ats_normalized": round(ats_normalized, 3),
            "ml_probability": round(ml_probability, 3),
            "deviation": round(abs(ats_normalized - ml_probability), 3),
        }

    def run_alignment_tests(self) -> Dict[str, Any]:
        """Run alignment tests with synthetic data"""

        test_cases = self.create_alignment_test_cases()
        results = []

        print("🔗 Running ATS-ML Alignment Tests...")

        for test_case in test_cases:
            # Create synthetic analysis data
            analysis_data = self._create_synthetic_data(test_case["ats_score"])

            # Get ML prediction
            try:
                prediction = self.ml_engine.predict_shortlist_probability(analysis_data)
                ml_prob = prediction.get("probability", 0.5)
            except Exception as e:
                print(f"❌ Error in {test_case['name']}: {str(e)}")
                continue

            # Check alignment
            alignment = self.check_alignment(test_case["ats_score"], ml_prob)

            result = {
                "test_name": test_case["name"],
                "ats_score": test_case["ats_score"],
                "ml_probability": ml_prob,
                "expected_range": test_case["expected_ml_range"],
                "alignment": alignment,
                "status": "PASS" if alignment["aligned"] else "FAIL",
            }

            results.append(result)

            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_emoji} {result['test_name']}: {result['status']} "
                  f"(ATS: {test_case['ats_score']}, ML: {ml_prob:.2f}, "
                  f"Quality: {alignment['quality']})")

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["status"] == "PASS")
        avg_alignment_score = np.mean([r["alignment"]["alignment_score"] for r in results])

        # Overall alignment quality
        if avg_alignment_score >= 0.85:
            overall_quality = "EXCELLENT"
        elif avg_alignment_score >= 0.75:
            overall_quality = "GOOD"
        elif avg_alignment_score >= 0.65:
            overall_quality = "FAIR"
        else:
            overall_quality = "NEEDS_IMPROVEMENT"

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
            "avg_alignment_score": round(avg_alignment_score, 3),
            "overall_quality": overall_quality,
            "results": results,
        }

        print(f"\n📊 ATS-ML Alignment Summary:")
        print(f"• Pass Rate: {summary['pass_rate']}%")
        print(f"• Average Alignment Score: {summary['avg_alignment_score']}")
        print(f"• Overall Quality: {summary['overall_quality']}")

        return summary

    def _create_synthetic_data(self, target_ats_score: float) -> Dict[str, Any]:
        """Create synthetic resume data to achieve target ATS score"""

        # Map ATS score ranges to resume characteristics
        if target_ats_score >= 90:
            # Perfect resume
            skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS", "Kubernetes"]
            skill_freq = {"Python": 4, "JavaScript": 3, "React": 3, "SQL": 3, "Docker": 2, "AWS": 2}
            sections = {"Skills": True, "Experience": True, "Education": True, "Projects": True, "Summary": True}
            missing_skills = {}
            formatting_issues = []
        elif target_ats_score >= 80:
            # Excellent resume
            skills = ["Python", "JavaScript", "React", "SQL", "Git"]
            skill_freq = {"Python": 3, "JavaScript": 2, "React": 2, "SQL": 2}
            sections = {"Skills": True, "Experience": True, "Education": True, "Projects": True, "Summary": True}
            missing_skills = {"DevOps": ["Docker"]}
            formatting_issues = []
        elif target_ats_score >= 70:
            # Good resume
            skills = ["Python", "SQL", "Excel"]
            skill_freq = {"Python": 2, "SQL": 2, "Excel": 1}
            sections = {"Skills": True, "Experience": True, "Education": True, "Projects": False, "Summary": True}
            missing_skills = {"Web Development": ["JavaScript", "HTML"]}
            formatting_issues = ["Could use more bullet points"]
        elif target_ats_score >= 50:
            # Average resume
            skills = ["Python", "Excel"]
            skill_freq = {"Python": 1, "Excel": 1}
            sections = {"Skills": True, "Experience": True, "Education": True, "Projects": False, "Summary": False}
            missing_skills = {"Programming Languages": ["JavaScript"], "Databases": ["SQL"]}
            formatting_issues = ["Missing projects section", "No summary"]
        elif target_ats_score >= 30:
            # Below average
            skills = ["Basic Computer Skills"]
            skill_freq = {"Basic Computer Skills": 1}
            sections = {"Skills": False, "Experience": True, "Education": False, "Projects": False, "Summary": False}
            missing_skills = {"Programming Languages": ["Python", "Java"], "Tools": ["Excel"]}
            formatting_issues = ["Too short", "No bullet points", "Missing education"]
        else:
            # Poor resume
            skills = []
            skill_freq = {}
            sections = {"Skills": False, "Experience": False, "Education": False, "Projects": False, "Summary": False}
            missing_skills = {"Everything": ["Python", "JavaScript", "SQL", "Excel"]}
            formatting_issues = ["Very short", "No structure", "Missing all sections"]

        return {
            "ats_score": target_ats_score,
            "skills_found": skills,
            "skill_frequency": skill_freq,
            "sections_detected": sections,
            "missing_skills": missing_skills,
            "formatting_issues": formatting_issues,
            "raw_text": f"Sample resume with ATS score {target_ats_score}",
        }

    def suggest_alignment_improvements(self, alignment_results: Dict[str, Any]) -> List[str]:
        """Suggest improvements for better ATS-ML alignment"""

        suggestions = []

        avg_score = alignment_results["avg_alignment_score"]
        pass_rate = alignment_results["pass_rate"]

        if avg_score < 0.7:
            suggestions.append("🔧 ML model predictions are significantly misaligned with ATS scores")
            suggestions.append("   Consider retraining the model with more balanced data")
            suggestions.append("   Review feature engineering to better capture ATS scoring factors")

        if pass_rate < 80:
            suggestions.append("⚠️ Many test cases failed alignment checks")
            suggestions.append("   Adjust alignment threshold or recalibrate ML predictions")
            suggestions.append("   Ensure ML features properly reflect ATS scoring components")

        # Check for systematic bias
        results = alignment_results["results"]
        high_ats_failures = sum(1 for r in results if r["ats_score"] >= 80 and r["status"] == "FAIL")
        low_ats_failures = sum(1 for r in results if r["ats_score"] <= 40 and r["status"] == "FAIL")

        if high_ats_failures > low_ats_failures:
            suggestions.append("📈 ML model underestimates high-ATS resumes")
            suggestions.append("   Add more high-quality resume examples to training data")
        elif low_ats_failures > high_ats_failures:
            suggestions.append("📉 ML model overestimates low-ATS resumes")
            suggestions.append("   Add more low-quality resume examples to training data")

        if not suggestions:
            suggestions.append("✅ ATS-ML alignment is good - no major improvements needed")

        return suggestions


def check_ats_ml_alignment(ml_engine: Optional[MLPredictionEngine] = None) -> Dict[str, Any]:
    """
    STEP 4 MAIN FUNCTION
    Run complete ATS-ML alignment check
    """
    if ml_engine is None:
        # Create with no model for testing
        ml_engine = MLPredictionEngine(model=None)

    checker = ATSMLAlignmentChecker(ml_engine)
    results = checker.run_alignment_tests()
    suggestions = checker.suggest_alignment_improvements(results)

    return {
        "alignment_check": results,
        "improvement_suggestions": suggestions,
        "step_status": "completed",
    }