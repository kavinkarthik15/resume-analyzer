"""
STEP 8: REAL-WORLD BENCHMARKING
Benchmark the system with real resume data and industry standards
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .analyzer_pipeline import CompleteResumeAnalysis
from .stress_testing import StressTestSuite
from ..utils.logger import logger, safe_execute


class BenchmarkEngine:
    """
    STEP 8: Real-world benchmarking engine
    Tests system performance with actual resume data
    """

    def __init__(self):
        self.analyzer = CompleteResumeAnalysis()
        self.stress_tester = StressTestSuite()
        self.benchmark_results = []

    def load_benchmark_dataset(self) -> List[Dict[str, Any]]:
        """
        Load benchmark dataset with real resumes and expected results
        """
        # For now, create synthetic benchmark data
        # In production, this would load from a curated dataset
        return [
            {
                "resume_id": "bench_001",
                "resume_type": "software_engineer",
                "content": """
                John Smith
                Senior Software Engineer

                Skills: Python, JavaScript, React, Node.js, SQL, AWS
                Experience: 5+ years developing web applications
                Education: BS Computer Science

                Projects:
                - Built e-commerce platform serving 10k+ users
                - Developed REST APIs with 99.9% uptime
                """,
                "expected_ats_score": 85,
                "expected_skills_found": 6,
                "target_role": "Software Engineer"
            },
            {
                "resume_id": "bench_002",
                "resume_type": "data_scientist",
                "content": """
                Sarah Johnson
                Data Scientist

                Skills: Python, R, Machine Learning, SQL, Tableau
                Experience: 3 years in data analysis and modeling
                Education: MS Data Science

                Key Achievements:
                - Improved model accuracy by 25%
                - Analyzed datasets with 1M+ records
                """,
                "expected_ats_score": 78,
                "expected_skills_found": 5,
                "target_role": "Data Scientist"
            },
            {
                "resume_id": "bench_003",
                "resume_type": "product_manager",
                "content": """
                Michael Chen
                Product Manager

                Experience: Led cross-functional teams of 15+ members
                Skills: Product Strategy, Agile, Analytics, SQL
                Education: MBA

                Achievements:
                - Launched product increasing revenue by 40%
                - Managed roadmap for 5+ products
                """,
                "expected_ats_score": 82,
                "expected_skills_found": 4,
                "target_role": "Product Manager"
            }
        ]

    def run_single_benchmark(self, benchmark_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run benchmark test for a single resume
        """
        resume_id = benchmark_case["resume_id"]
        logger.info(f"Running benchmark for {resume_id}")

        try:
            # Create temporary file for testing
            temp_file = f"/tmp/{resume_id}.txt"
            with open(temp_file, 'w') as f:
                f.write(benchmark_case["content"])

            # Run complete analysis
            start_time = time.time()
            analysis_result = safe_execute(
                f"benchmark_analysis_{resume_id}",
                self.analyzer.analyze_resume_complete,
                temp_file,
                fallback_value={"status": "failed", "error": "Analysis failed"}
            )
            analysis_time = time.time() - start_time

            # Extract key metrics
            ats_score = analysis_result.get("ats_analysis", {}).get("total_score", 0)
            skills_found = len(analysis_result.get("parsing", {}).get("skills", []))
            ml_probability = analysis_result.get("ml_prediction", {}).get("probability", 0.0)

            # Calculate accuracy metrics
            expected_ats = benchmark_case["expected_ats_score"]
            expected_skills = benchmark_case["expected_skills_found"]

            ats_accuracy = 1.0 - abs(ats_score - expected_ats) / 100.0
            skills_accuracy = min(skills_found / expected_skills, 1.0) if expected_skills > 0 else 0.0

            # Determine pass/fail
            ats_pass = abs(ats_score - expected_ats) <= 10  # Within 10 points
            skills_pass = skills_found >= expected_skills * 0.8  # At least 80% of expected skills
            overall_pass = ats_pass and skills_pass

            result = {
                "test_name": resume_id,
                "resume_type": benchmark_case["resume_type"],
                "ats_score": ats_score,
                "expected_ats_score": expected_ats,
                "ats_accuracy": round(ats_accuracy, 2),
                "skills_found": skills_found,
                "expected_skills": expected_skills,
                "skills_accuracy": round(skills_accuracy, 2),
                "ml_probability": ml_probability,
                "analysis_time": round(analysis_time, 2),
                "ats_pass": ats_pass,
                "skills_pass": skills_pass,
                "overall_pass": overall_pass,
                "verdict": "PASS" if overall_pass else "FAIL",
                "notes": f"ATS: {'✓' if ats_pass else '✗'} ({ats_score}/{expected_ats}), Skills: {'✓' if skills_pass else '✗'} ({skills_found}/{expected_skills})"
            }

            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return result

        except Exception as e:
            logger.error(f"Benchmark failed for {resume_id}: {e}")
            return {
                "test_name": resume_id,
                "resume_type": benchmark_case["resume_type"],
                "ats_score": 0,
                "expected_ats_score": benchmark_case["expected_ats_score"],
                "ats_accuracy": 0.0,
                "skills_found": 0,
                "expected_skills": benchmark_case["expected_skills_found"],
                "skills_accuracy": 0.0,
                "ml_probability": 0.0,
                "analysis_time": 0.0,
                "ats_pass": False,
                "skills_pass": False,
                "overall_pass": False,
                "verdict": "ERROR",
                "notes": f"Test failed: {str(e)}"
            }

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run comprehensive benchmark suite
        """
        logger.info("Starting comprehensive benchmark suite")

        benchmark_cases = self.load_benchmark_dataset()
        results = []

        for case in benchmark_cases:
            result = self.run_single_benchmark(case)
            results.append(result)
            self.benchmark_results.append(result)

        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["overall_pass"])
        failed_tests = total_tests - passed_tests

        avg_ats_score = sum(r["ats_score"] for r in results) / total_tests
        avg_ats_accuracy = sum(r["ats_accuracy"] for r in results) / total_tests
        avg_skills_accuracy = sum(r["skills_accuracy"] for r in results) / total_tests
        avg_ml_probability = sum(r["ml_probability"] for r in results) / total_tests
        avg_analysis_time = sum(r["analysis_time"] for r in results) / total_tests

        # Determine overall quality assessment
        overall_accuracy = (avg_ats_accuracy + avg_skills_accuracy) / 2

        if overall_accuracy >= 0.9:
            quality = "EXCELLENT - Production Ready"
        elif overall_accuracy >= 0.8:
            quality = "GOOD - Minor Improvements Needed"
        elif overall_accuracy >= 0.7:
            quality = "FAIR - Significant Improvements Needed"
        else:
            quality = "POOR - Major Overhaul Required"

        # Generate recommendations
        recommendations = []

        if avg_ats_accuracy < 0.8:
            recommendations.append("Improve ATS scoring algorithm accuracy")
        if avg_skills_accuracy < 0.8:
            recommendations.append("Enhance skill extraction and detection")
        if avg_analysis_time > 5.0:
            recommendations.append("Optimize analysis pipeline performance")
        if failed_tests > 0:
            recommendations.append(f"Fix issues in {failed_tests} failing test cases")

        if not recommendations:
            recommendations.append("System performing well - continue monitoring")

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "average_ats_score": round(avg_ats_score, 1),
            "average_ats_accuracy": round(avg_ats_accuracy, 2),
            "average_skills_accuracy": round(avg_skills_accuracy, 2),
            "average_ml_probability": round(avg_ml_probability, 2),
            "average_analysis_time": round(avg_analysis_time, 2),
            "overall_quality": quality,
            "results": results,
            "recommendations": recommendations,
            "benchmark_timestamp": time.time()
        }

        logger.info(f"Benchmark completed: {passed_tests}/{total_tests} tests passed")
        return summary

    def run_industry_comparison(self) -> Dict[str, Any]:
        """
        Compare system performance against industry benchmarks
        """
        logger.info("Running industry comparison benchmarks")

        # Industry standards (approximate)
        industry_standards = {
            "ats_accuracy_target": 0.85,  # 85% accuracy
            "skills_detection_target": 0.90,  # 90% detection rate
            "processing_time_target": 3.0,  # 3 seconds max
            "ml_prediction_confidence": 0.75  # 75% confidence threshold
        }

        benchmark_results = self.run_comprehensive_benchmark()

        comparison = {
            "ats_accuracy_vs_target": benchmark_results["average_ats_accuracy"] - industry_standards["ats_accuracy_target"],
            "skills_accuracy_vs_target": benchmark_results["average_skills_accuracy"] - industry_standards["skills_detection_target"],
            "processing_time_vs_target": industry_standards["processing_time_target"] - benchmark_results["average_analysis_time"],
            "ml_confidence_vs_target": benchmark_results["average_ml_probability"] - industry_standards["ml_prediction_confidence"],
            "industry_standards": industry_standards,
            "meets_ats_target": benchmark_results["average_ats_accuracy"] >= industry_standards["ats_accuracy_target"],
            "meets_skills_target": benchmark_results["average_skills_accuracy"] >= industry_standards["skills_detection_target"],
            "meets_performance_target": benchmark_results["average_analysis_time"] <= industry_standards["processing_time_target"],
            "meets_ml_target": benchmark_results["average_ml_probability"] >= industry_standards["ml_prediction_confidence"]
        }

        return {
            "benchmark_results": benchmark_results,
            "industry_comparison": comparison,
            "overall_industry_readiness": all([
                comparison["meets_ats_target"],
                comparison["meets_skills_target"],
                comparison["meets_performance_target"],
                comparison["meets_ml_target"]
            ])
        }


def run_real_world_benchmarks() -> Dict[str, Any]:
    """
    STEP 8: Run real-world benchmarking
    Main entry point for benchmarking
    """
    benchmark_engine = BenchmarkEngine()
    return benchmark_engine.run_industry_comparison()