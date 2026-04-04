"""
STEP 1: End-to-End Testing Framework
Test with different resume types and validate system behavior
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any

from backend.services.parser import parse_resume, validate_parsed_resume
from backend.services.scorer import calculate_ats_score
from backend.services.ml_manager import MLPredictionEngine, FeatureEngineering


class ResumeTestCase:
    """Test case for resume analysis"""

    def __init__(self, name: str, content: str, expected_features: Dict[str, Any]):
        self.name = name
        self.content = content
        self.expected_features = expected_features


class EndToEndTester:
    """
    STEP 1: End-to-End Testing Framework
    Test system with various resume types
    """

    def __init__(self, ml_model=None):
        self.ml_engine = MLPredictionEngine(model=ml_model)
        self.test_results = []

    def create_test_resumes(self) -> List[ResumeTestCase]:
        """Create various test resume types"""

        # Test Case 1: Clean ATS Resume
        clean_resume = """
        JOHN DOE
        Software Engineer

        SKILLS
        Python, JavaScript, React, Node.js, SQL, Git, Docker, AWS

        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020-Present
        • Developed scalable web applications using Python and React
        • Improved system performance by 40% through optimization
        • Led team of 5 developers on microservices architecture

        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology | 2016-2020
        GPA: 3.8/4.0

        PROJECTS
        E-commerce Platform
        • Built full-stack application with 10,000+ users
        • Implemented payment processing and inventory management
        """

        # Test Case 2: Fancy Design Resume (Poor Formatting)
        fancy_resume = """
        ════════════════════════════════════════════════════════════════
        📧 john.doe@email.com                    📱 (555) 123-4567
        ════════════════════════════════════════════════════════════════

        🎯 PROFESSIONAL SUMMARY
        Innovative software engineer with 5+ years experience building
        scalable solutions. Passionate about clean code and user experience.

        💼 WORK EXPERIENCE
        Senior Developer @ StartupXYZ (2021-Present)
        - Built mobile apps with React Native
        - Increased user engagement by 25%
        - Collaborated with cross-functional teams

        🎓 EDUCATION
        Computer Science Degree
        State University (2017-2021)

        🛠️ TECHNICAL SKILLS
        • Programming: Python, Java
        • Frameworks: Django, Spring
        • Tools: Git, Jenkins, Kubernetes
        """

        # Test Case 3: Minimal Resume (No Skills Section)
        minimal_resume = """
        Jane Smith
        Junior Developer

        WORK EXPERIENCE
        Intern | Local Company | Summer 2023
        Helped with basic coding tasks
        Learned about software development

        EDUCATION
        Associate Degree in Information Technology
        Community College | 2021-2023
        """

        # Test Case 4: Technical Resume (Heavy Skills)
        technical_resume = """
        DR. ALICE JOHNSON
        Machine Learning Engineer

        TECHNICAL SKILLS
        Python, R, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy,
        SQL, MongoDB, Docker, Kubernetes, AWS, GCP, Azure,
        Apache Spark, Hadoop, Kafka, Jenkins, Git, Linux

        EXPERIENCE
        ML Engineer | AI Company | 2019-Present
        • Developed deep learning models achieving 95% accuracy
        • Processed 1TB+ datasets using distributed computing
        • Published 3 papers in top-tier ML conferences
        • Led team of 8 data scientists and engineers

        EDUCATION
        PhD in Computer Science (Machine Learning)
        MIT | 2015-2019
        Thesis: "Advanced Neural Network Architectures"

        PUBLICATIONS
        • "Novel Transformer Architecture" - NeurIPS 2022
        • "Efficient Training Methods" - ICML 2021
        """

        return [
            ResumeTestCase("Clean ATS Resume", clean_resume, {
                "expected_skills": 8,
                "expected_sections": ["Skills", "Experience", "Education", "Projects"],
                "expected_ats_score": (70, 100),
                "expected_ml_probability": (0.6, 1.0),
            }),
            ResumeTestCase("Fancy Design Resume", fancy_resume, {
                "expected_skills": 6,
                "expected_sections": ["Summary", "Experience", "Education", "Skills"],
                "expected_ats_score": (50, 85),
                "expected_ml_probability": (0.4, 0.8),
            }),
            ResumeTestCase("Minimal Resume", minimal_resume, {
                "expected_skills": 0,
                "expected_sections": ["Experience", "Education"],
                "expected_ats_score": (20, 50),
                "expected_ml_probability": (0.1, 0.4),
            }),
            ResumeTestCase("Technical Resume", technical_resume, {
                "expected_skills": 15,
                "expected_sections": ["Skills", "Experience", "Education", "Publications"],
                "expected_ats_score": (85, 100),
                "expected_ml_probability": (0.8, 1.0),
            }),
        ]

    def run_test(self, test_case: ResumeTestCase) -> Dict[str, Any]:
        """Run single test case"""

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_case.content)
            temp_path = f.name

        try:
            # Step 1: Parse Resume
            parsed = parse_resume(temp_path)
            validation = validate_parsed_resume(parsed)

            # Step 2: Calculate ATS Score
            ats_breakdown = calculate_ats_score(
                parsed.raw_text,
                parsed.skills,
                parsed.skill_frequency,
                parsed.sections_detected
            )

            # Step 3: ML Prediction
            analysis_data = {
                "ats_score": ats_breakdown.total_score,
                "skills_found": parsed.skills,
                "skill_frequency": parsed.skill_frequency,
                "sections_detected": parsed.sections_detected,
                "missing_skills": ats_breakdown.missing_skills,
                "formatting_issues": ats_breakdown.formatting_issues,
                "raw_text": parsed.raw_text,
            }

            try:
                ml_prediction = self.ml_engine.predict_shortlist_probability(analysis_data)
            except Exception as e:
                ml_prediction = {"error": str(e), "probability": 0.5}

            # Step 4: Validate Results
            validation_results = self.validate_results(
                test_case, parsed, ats_breakdown, ml_prediction
            )

            return {
                "test_name": test_case.name,
                "passed": validation_results["overall_pass"],
                "parsing": {
                    "skills_found": len(parsed.skills),
                    "sections_detected": sum(parsed.sections_detected.values()),
                    "validation": validation,
                },
                "ats_score": ats_breakdown.total_score,
                "ml_probability": ml_prediction.get("probability", 0),
                "validation": validation_results,
                "details": {
                    "parsed": parsed.to_dict(),
                    "ats_breakdown": ats_breakdown.to_dict(),
                    "ml_prediction": ml_prediction,
                }
            }

        finally:
            # Clean up
            os.unlink(temp_path)

    def validate_results(self, test_case: ResumeTestCase, parsed, ats_breakdown, ml_prediction) -> Dict[str, Any]:
        """Validate test results against expectations"""

        issues = []
        warnings = []

        # Check skills
        expected_skills = test_case.expected_features["expected_skills"]
        actual_skills = len(parsed.skills)

        if abs(actual_skills - expected_skills) > 2:
            issues.append(f"Skills count mismatch: expected ~{expected_skills}, got {actual_skills}")
        elif abs(actual_skills - expected_skills) > 0:
            warnings.append(f"Skills count slight mismatch: expected ~{expected_skills}, got {actual_skills}")

        # Check sections
        expected_sections = test_case.expected_features["expected_sections"]
        detected_sections = [k for k, v in parsed.sections_detected.items() if v]

        missing_sections = set(expected_sections) - set(detected_sections)
        if missing_sections:
            issues.append(f"Missing expected sections: {missing_sections}")

        # Check ATS score range
        expected_ats_range = test_case.expected_features["expected_ats_score"]
        actual_ats = ats_breakdown.total_score

        if not (expected_ats_range[0] <= actual_ats <= expected_ats_range[1]):
            warnings.append(f"ATS score {actual_ats} outside expected range {expected_ats_range}")

        # Check ML probability range
        expected_ml_range = test_case.expected_features["expected_ml_probability"]
        actual_ml = ml_prediction.get("probability", 0)

        if not (expected_ml_range[0] <= actual_ml <= expected_ml_range[1]):
            warnings.append(f"ML probability {actual_ml} outside expected range {expected_ml_range}")

        # Check ATS-ML alignment
        ats_category = "high" if actual_ats >= 70 else "medium" if actual_ats >= 50 else "low"
        ml_category = "high" if actual_ml >= 0.7 else "medium" if actual_ml >= 0.5 else "low"

        if ats_category != ml_category:
            warnings.append(f"ATS-ML misalignment: ATS={ats_category} ({actual_ats}), ML={ml_category} ({actual_ml})")

        return {
            "overall_pass": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "skills_accuracy": abs(actual_skills - expected_skills) <= 2,
            "sections_accuracy": len(missing_sections) == 0,
            "ats_in_range": expected_ats_range[0] <= actual_ats <= expected_ats_range[1],
            "ml_in_range": expected_ml_range[0] <= actual_ml <= expected_ml_range[1],
            "ats_ml_aligned": ats_category == ml_category,
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases"""

        test_cases = self.create_test_resumes()
        results = []

        for test_case in test_cases:
            result = self.run_test(test_case)
            results.append(result)
            print(f"✅ {test_case.name}: {'PASS' if result['passed'] else 'ISSUES'}")

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["passed"])
        issues_found = sum(len(r["validation"]["issues"]) for r in results)
        warnings_found = sum(len(r["validation"]["warnings"]) for r in results)

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": round(passed_tests / total_tests * 100, 1),
            "total_issues": issues_found,
            "total_warnings": warnings_found,
            "system_reliability": "HIGH" if issues_found == 0 else "MEDIUM" if issues_found <= 2 else "LOW",
            "results": results,
        }

        print(f"\n📊 Test Summary:")
        print(f"• Pass Rate: {summary['pass_rate']}%")
        print(f"• Issues Found: {issues_found}")
        print(f"• Warnings: {warnings_found}")
        print(f"• System Reliability: {summary['system_reliability']}")

        return summary


def run_end_to_end_tests(ml_model=None) -> Dict[str, Any]:
    """
    STEP 1 MAIN FUNCTION
    Run complete end-to-end testing suite
    """
    tester = EndToEndTester(ml_model=ml_model)
    return tester.run_all_tests()