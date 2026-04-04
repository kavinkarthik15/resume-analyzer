"""
ML Manager for Resume Analyzer
Provides centralized access to ML models and analysis
"""

from .analyzer_pipeline import CompleteResumeAnalysis


class MLManager:
    """Manager for ML operations"""

    def __init__(self):
        self.analyzer = CompleteResumeAnalysis()

    def analyze_resume(self, text: str):
        """Analyze resume text"""
        return self.analyzer.analyze_resume_text(text)


# Global instance
ml_manager = MLManager()