"""
STEP 5: STRESS TESTING
Systematic testing of pipeline with edge cases and real-world scenarios
"""

import os
import time as test_time
from typing import Dict, List, Any, Optional
from backend.services.analyzer_pipeline import CompleteResumeAnalysis


class StressTestSuite:
    """
    STEP 5: Comprehensive stress testing for the resume analyzer pipeline
    """

    def __init__(self):
        self.analyzer = CompleteResumeAnalysis()
        self.test_results = []
        self.start_time = None

    def create_test_cases(self) -> List[Dict[str, Any]]:
        """Create comprehensive test cases for different scenarios"""

        return [
            # 📄 RESUME EDGE CASES
            {
                "name": "Empty File Test",
                "category": "edge_case",
                "description": "Test with empty or minimal content",
                "data": {
                    "content": "",
                    "filename": "empty_resume.txt",
                    "expected_status": "failed",
                    "expected_errors": ["parsing", "scoring"],
                }
            },
            {
                "name": "No Skills Section",
                "category": "edge_case",
                "description": "Resume with no explicit skills section",
                "data": {
                    "content": """
                    John Doe
                    Software Engineer

                    Experience:
                    - Worked on various projects
                    - Developed applications

                    Education:
                    - Bachelor's in Computer Science
                    """,
                    "filename": "no_skills_resume.txt",
                    "expected_status": "partial",
                    "expected_ats_range": (20, 50),
                }
            },
            {
                "name": "No Experience Section",
                "category": "edge_case",
                "description": "Resume with no work experience",
                "data": {
                    "content": """
                    Jane Smith
                    Recent Graduate

                    Skills:
                    - Python, JavaScript, SQL
                    - React, Node.js, Git

                    Education:
                    - Master's in Computer Science
                    - GPA: 3.8

                    Projects:
                    - Built a web application
                    """,
                    "filename": "no_experience_resume.txt",
                    "expected_status": "partial",
                    "expected_ats_range": (40, 70),
                }
            },
            {
                "name": "Student Resume (Projects Only)",
                "category": "edge_case",
                "description": "Student resume with only projects",
                "data": {
                    "content": """
                    Alex Johnson
                    Computer Science Student

                    Projects:
                    - E-commerce website (React, Node.js)
                    - Machine learning model (Python, TensorFlow)
                    - Mobile app (React Native)

                    Skills:
                    - Python, JavaScript, SQL
                    - React, Node.js, Git, Docker

                    Education:
                    - Computer Science Major
                    - Expected graduation: 2025
                    """,
                    "filename": "student_resume.txt",
                    "expected_status": "success",
                    "expected_ats_range": (60, 85),
                }
            },
            {
                "name": "Keyword Stuffing",
                "category": "edge_case",
                "description": "Resume with excessive keyword repetition",
                "data": {
                    "content": """
                    Michael Chen
                    Python Developer

                    Skills:
                    Python, Python, Python, JavaScript, JavaScript, JavaScript,
                    React, React, React, Node.js, Node.js, Node.js,
                    SQL, SQL, SQL, Git, Git, Git, Docker, Docker, Docker,
                    AWS, AWS, AWS, Kubernetes, Kubernetes, Kubernetes

                    Experience:
                    Python developer using Python with Python frameworks.
                    JavaScript development with JavaScript and JavaScript libraries.
                    React development using React and React components.
                    """,
                    "filename": "keyword_stuffing_resume.txt",
                    "expected_status": "success",
                    "expected_ats_range": (70, 90),
                    "expected_warnings": ["keyword_stuffing"],
                }
            },
            {
                "name": "Very Long Resume",
                "category": "edge_case",
                "description": "Resume with extensive content",
                "data": {
                    "content": "\n".join([
                        "Sarah Wilson",
                        "Senior Software Engineer",
                        "",
                        "Skills:",
                        "Python, JavaScript, Java, C++, SQL, NoSQL, React, Angular, Vue.js,",
                        "Node.js, Express, Django, Flask, Spring Boot, Hibernate,",
                        "AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Git, GitHub, GitLab,",
                        "Linux, Windows, macOS, Agile, Scrum, Kanban, TDD, BDD",
                        "",
                        "Experience:"
                    ] + [f"- Position {i}: Developed applications using various technologies" for i in range(1, 21)] +
                    ["", "Education:", "- PhD in Computer Science", "- Master's in Software Engineering", "- Bachelor's in Computer Science"]),
                    "filename": "long_resume.txt",
                    "expected_status": "success",
                    "expected_ats_range": (80, 100),
                }
            },

            # 🧠 CONTENT QUALITY CASES
            {
                "name": "Strong Resume",
                "category": "quality",
                "description": "High-quality resume with all sections",
                "data": {
                    "content": """
                    David Rodriguez
                    Senior Full-Stack Developer

                    Summary:
                    Experienced developer with 8+ years in web development,
                    specializing in scalable applications and team leadership.

                    Skills:
                    - Programming: Python, JavaScript, TypeScript, Java
                    - Frameworks: React, Node.js, Django, Spring Boot
                    - Databases: PostgreSQL, MongoDB, Redis
                    - Cloud: AWS, Docker, Kubernetes
                    - Tools: Git, Jenkins, Jira

                    Experience:
                    Senior Developer at Tech Corp (2020-Present)
                    - Led team of 5 developers
                    - Built microservices architecture
                    - Improved performance by 40%

                    Full-Stack Developer at Startup Inc (2018-2020)
                    - Developed customer-facing applications
                    - Implemented CI/CD pipelines

                    Education:
                    - MS Computer Science, Stanford University
                    - BS Computer Science, UC Berkeley

                    Certifications:
                    - AWS Solutions Architect
                    - Google Cloud Professional
                    """,
                    "filename": "strong_resume.txt",
                    "expected_status": "success",
                    "expected_ats_range": (85, 100),
                    "expected_ml_range": (0.8, 1.0),
                }
            },
            {
                "name": "Weak Resume",
                "category": "quality",
                "description": "Low-quality resume with missing sections",
                "data": {
                    "content": """
                    Bob Johnson

                    I have some computer skills.
                    I can use Microsoft Word and Excel.
                    I have a high school diploma.
                    """,
                    "filename": "weak_resume.txt",
                    "expected_status": "partial",
                    "expected_ats_range": (10, 30),
                    "expected_ml_range": (0.0, 0.3),
                }
            },
            {
                "name": "Medium Resume",
                "category": "quality",
                "description": "Average resume with some sections missing",
                "data": {
                    "content": """
                    Emily Davis
                    Junior Developer

                    Skills:
                    - Python, JavaScript, HTML, CSS
                    - Git, SQL

                    Experience:
                    Intern at Local Company (6 months)
                    - Helped with basic coding tasks
                    - Learned about software development

                    Education:
                    - Bachelor's in Computer Science (In Progress)
                    """,
                    "filename": "medium_resume.txt",
                    "expected_status": "success",
                    "expected_ats_range": (45, 65),
                    "expected_ml_range": (0.3, 0.7),
                }
            },
        ]

    def create_test_file(self, test_case: Dict[str, Any]) -> str:
        """Create a temporary test file"""

        # Create temp directory if it doesn't exist
        temp_dir = "backend/temp_test_files"
        os.makedirs(temp_dir, exist_ok=True)

        file_path = os.path.join(temp_dir, test_case["data"]["filename"])

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_case["data"]["content"])

        return file_path

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single stress test case"""

        print(f"🧪 Testing: {test_case['name']}")

        # Create test file
        file_path = self.create_test_file(test_case)

        import time as time_module
        start_time = time_module.time()
        result = None
        error = None

        try:
            # Run the analysis
            result = self.analyzer.analyze_resume_complete(file_path)
            execution_time = time_module.time() - start_time

            # Validate result
            validation = self.validate_test_result(test_case, result, execution_time)

            return {
                "test_name": test_case["name"],
                "category": test_case["category"],
                "status": "SUCCESS",
                "execution_time": round(execution_time, 2),
                "result": result,
                "validation": validation,
                "error": None,
            }

        except Exception as e:
            execution_time = time_module.time() - start_time
            error = str(e)

            print(f"❌ {test_case['name']}: FAILED - {error}")

            return {
                "test_name": test_case["name"],
                "category": test_case["category"],
                "status": "FAILED",
                "execution_time": round(execution_time, 2),
                "result": result,
                "validation": None,
                "error": error,
            }

        finally:
            # Clean up test file
            if os.path.exists(file_path):
                os.remove(file_path)

    def validate_test_result(self, test_case: Dict[str, Any], result: Dict[str, Any],
                           execution_time: float) -> Dict[str, Any]:
        """Validate the test result against expectations"""

        validation = {
            "status_match": False,
            "ats_score_valid": False,
            "ml_prediction_valid": False,
            "no_crashes": True,
            "performance_ok": execution_time < 30,  # Should complete within 30 seconds
            "issues": [],
        }

        # Check status
        expected_status = test_case["data"]["expected_status"]
        actual_status = result.get("status", "unknown")

        if expected_status == "success" and actual_status in ["success", "warnings"]:
            validation["status_match"] = True
        elif expected_status == "partial" and actual_status in ["success", "warnings", "partial"]:
            validation["status_match"] = True
        elif expected_status == "failed" and actual_status == "failed":
            validation["status_match"] = True

        # Check ATS score
        if "expected_ats_range" in test_case["data"]:
            ats_score = result.get("ats_analysis", {}).get("score", 0)
            min_score, max_score = test_case["data"]["expected_ats_range"]
            if min_score <= ats_score <= max_score:
                validation["ats_score_valid"] = True
            else:
                validation["issues"].append(f"ATS score {ats_score} not in expected range [{min_score}, {max_score}]")

        # Check ML prediction
        if "expected_ml_range" in test_case["data"]:
            ml_prob = result.get("ml_prediction", {}).get("probability", 0)
            min_prob, max_prob = test_case["data"]["expected_ml_range"]
            if min_prob <= ml_prob <= max_prob:
                validation["ml_prediction_valid"] = True
            else:
                validation["issues"].append(f"ML probability {ml_prob:.2f} not in expected range [{min_prob}, {max_prob}]")

        # Check for crashes (None values in critical fields)
        critical_fields = [
            result.get("parsing"),
            result.get("ats_analysis"),
            result.get("ml_prediction"),
        ]

        if any(field is None for field in critical_fields):
            validation["no_crashes"] = False
            validation["issues"].append("Critical fields contain None values")

        return validation

    def run_pipeline_stress_test(self) -> Dict[str, Any]:
        """Run stress test with multiple rapid calls"""

        print("🔄 Running Pipeline Stress Test...")

        stress_results = []
        rapid_test_count = 10

        # Use a medium-complexity test case for stress testing
        stress_test_case = self.create_test_cases()[7]  # Medium resume

        for i in range(rapid_test_count):
            print(f"  Rapid test {i+1}/{rapid_test_count}")

            result = self.run_single_test(stress_test_case)
            stress_results.append(result)

            # Small delay to prevent overwhelming
            test_time.sleep(0.1)

        # Analyze stress test results
        success_count = sum(1 for r in stress_results if r["status"] == "SUCCESS")
        avg_time = sum(r["execution_time"] for r in stress_results) / len(stress_results)
        max_time = max(r["execution_time"] for r in stress_results)

        stress_summary = {
            "total_tests": rapid_test_count,
            "successful_tests": success_count,
            "success_rate": round(success_count / rapid_test_count * 100, 1),
            "avg_execution_time": round(avg_time, 2),
            "max_execution_time": round(max_time, 2),
            "performance_stable": max_time < avg_time * 2,  # No major performance degradation
        }

        print(f"📊 Stress Test Results:")
        print(f"  Success Rate: {stress_summary['success_rate']}%")
        print(f"  Average Time: {stress_summary['avg_execution_time']}s")
        print(f"  Max Time: {stress_summary['max_execution_time']}s")
        print(f"  Performance Stable: {'✅' if stress_summary['performance_stable'] else '❌'}")

        return stress_summary

    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete stress test suite"""

        print("🧪 STARTING COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)

        self.start_time = test_time.time()
        self.test_results = []

        # Run individual test cases
        test_cases = self.create_test_cases()

        for test_case in test_cases:
            result = self.run_single_test(test_case)
            self.test_results.append(result)

        # Run pipeline stress test
        stress_results = self.run_pipeline_stress_test()

        # Calculate overall results
        total_time = test_time.time() - self.start_time
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["status"] == "SUCCESS")
        success_rate = round(successful_tests / total_tests * 100, 1)

        # Categorize results
        category_results = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in category_results:
                category_results[cat] = []
            category_results[cat].append(result)

        category_summary = {}
        for cat, results in category_results.items():
            cat_success = sum(1 for r in results if r["status"] == "SUCCESS")
            category_summary[cat] = {
                "total": len(results),
                "successful": cat_success,
                "success_rate": round(cat_success / len(results) * 100, 1),
            }

        # Overall assessment
        if success_rate >= 90:
            overall_quality = "EXCELLENT"
        elif success_rate >= 80:
            overall_quality = "GOOD"
        elif success_rate >= 70:
            overall_quality = "FAIR"
        else:
            overall_quality = "NEEDS_IMPROVEMENT"

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "total_time": round(total_time, 2),
            "category_results": category_summary,
            "stress_test_results": stress_results,
            "overall_quality": overall_quality,
            "critical_issues": self.identify_critical_issues(),
            "recommendations": self.generate_recommendations(),
        }

        # Print final summary
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUITE RESULTS")
        print("=" * 60)
        print(f"• Total Tests: {summary['total_tests']}")
        print(f"• Success Rate: {summary['success_rate']}%")
        print(f"• Total Time: {summary['total_time']}s")
        print(f"• Overall Quality: {summary['overall_quality']}")
        print(f"• Stress Test Success: {stress_results['success_rate']}%")

        if summary["critical_issues"]:
            print(f"• Critical Issues: {len(summary['critical_issues'])}")

        return summary

    def identify_critical_issues(self) -> List[str]:
        """Identify critical issues that need immediate attention"""

        issues = []

        for result in self.test_results:
            if result["status"] == "FAILED":
                issues.append(f"Test '{result['test_name']}' failed: {result['error']}")

            if result["validation"]:
                val = result["validation"]
                if not val["no_crashes"]:
                    issues.append(f"Test '{result['test_name']}' has crashes/None values")
                if not val["performance_ok"]:
                    issues.append(f"Test '{result['test_name']}' took too long ({result['execution_time']}s)")

        return issues

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""

        recommendations = []

        # Analyze failure patterns
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failing test cases")

        # Check performance
        slow_tests = [r for r in self.test_results if r["execution_time"] > 10]
        if slow_tests:
            recommendations.append(f"Optimize performance for {len(slow_tests)} slow tests")

        # Check validation issues
        validation_issues = sum(len(r["validation"]["issues"]) for r in self.test_results
                              if r["validation"] and r["validation"]["issues"])
        if validation_issues > 0:
            recommendations.append(f"Address {validation_issues} validation issues")

        if not recommendations:
            recommendations.append("All tests passed - system is robust!")

        return recommendations


def run_stress_tests() -> Dict[str, Any]:
    """
    STEP 5 MAIN FUNCTION
    Run complete stress testing suite
    """
    print("🧪 STEP 5: STRESS TESTING INITIATED")
    print("Testing pipeline resilience with edge cases...")

    tester = StressTestSuite()
    results = tester.run_all_tests()

    return {
        "step": "stress_testing",
        "status": "completed",
        "results": results,
    }