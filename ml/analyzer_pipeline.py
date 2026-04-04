import os
import re
import pandas as pd
import joblib
from typing import Dict, Any


class CompleteResumeAnalysis:
    """Complete resume analysis pipeline with ML model"""

    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        """Load the ML model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'random_forest_model.pkl')
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            raise Exception(f"Error loading ML model: {e}")

    def extract_years_experience(self, text: str) -> int:
        """Extract years of experience from dates in resume"""
        years = re.findall(r'(20\d{2})', text)

        if len(years) >= 2:
            years = list(map(int, years))
            return max(years) - min(years)

        return 0

    def count_skills(self, text: str) -> int:
        """Count technology skills mentioned in resume"""
        common_skills = [
            "python", "java", "sql", "aws", "docker", "kubernetes",
            "react", "node", "node.js", "tensorflow", "pytorch",
            "excel", "javascript", "typescript", "c++", "c#",
            "php", "ruby", "go", "rust", "scala",
            "spark", "hadoop", "hive", "postgres", "mongodb",
            "redis", "cassandra", "elasticsearch", "tableau",
            "git", "jenkins", "gitlab", "github", "bitbucket",
            "linux", "windows", "unix", "gcp", "azure",
            "angular", "vue", "svelte", "express", "django",
            "flask", "spring", "scala", "kotlin", "swift"
        ]

        text_lower = text.lower()
        return sum(1 for skill in common_skills if skill in text_lower)

    def leadership_score(self, text: str) -> int:
        """Extract leadership indicators from resume"""
        leadership_words = [
            "led", "managed", "mentored", "directed", "owned",
            "lead", "leading", "leading team", "team lead", "senior",
            "principal", "architect", "head of", "director"
        ]

        text_lower = text.lower()
        return sum(1 for word in leadership_words if word in text_lower)

    def achievement_score(self, text: str) -> int:
        """Count quantified achievements (%, $, numbers with impact)"""
        # Look for percentages, dollar amounts, and numbers followed by x
        return len(re.findall(r'(\d+%|\$\d+k?|\d+x|\d+\s*(million|billion|thousand|k))', text, re.IGNORECASE))

    def education_score(self, text: str) -> int:
        """Evaluate education level"""
        text_lower = text.lower()

        if "phd" in text_lower or "doctorate" in text_lower:
            return 3
        elif "master" in text_lower or "ms" in text_lower or "m.s" in text_lower or "m.tech" in text_lower:
            return 2
        elif "bachelor" in text_lower or "b.s" in text_lower or "bs" in text_lower or "b.tech" in text_lower:
            return 1
        else:
            return 0

    def project_count(self, text: str) -> int:
        """Count projects mentioned in resume"""
        return text.lower().count("project")

    def certification_count(self, text: str) -> int:
        """Count certifications mentioned in resume"""
        return text.lower().count("certified") + text.lower().count("certification")

    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract all features from resume text"""
        return {
            "years_experience": self.extract_years_experience(text),
            "skill_count": self.count_skills(text),
            "leadership_score": self.leadership_score(text),
            "achievement_score": self.achievement_score(text),
            "education_score": self.education_score(text),
            "project_count": self.project_count(text),
            "certification_count": self.certification_count(text),
        }

    def analyze_resume_text(self, text: str) -> Dict[str, Any]:
        """Analyze resume text and return complete analysis"""

        # Handle edge cases
        if len(text.strip()) < 50:
            return {
                'prediction': 'ERROR',
                'confidence': 0.0,
                'error': 'Resume too short (< 50 characters)',
                'success': False
            }

        # Extract features
        features = self.extract_features(text)

        # Check for no content
        total_features = sum(features.values())
        if total_features == 0:
            return {
                'prediction': 'ERROR',
                'confidence': 0.0,
                'error': 'No identifiable resume content',
                'success': False
            }

        # Convert to DataFrame for ML model
        feature_df = pd.DataFrame([features])

        # Make prediction
        prediction_proba = self.model.predict_proba(feature_df)[0]
        prediction = self.model.predict(feature_df)[0]

        # Determine confidence and decision
        max_prob = max(prediction_proba)

        # Binary classification: weak vs strong
        quality_map = {0: 'weak', 1: 'strong'}
        predicted_quality = quality_map.get(prediction, 'unknown')
        probabilities = {
            'weak': float(prediction_proba[0]),
            'strong': float(prediction_proba[1]),
            'average': 0.0  # Not predicted by binary model
        }

        # Confidence-based decision
        if prediction_proba[1] > 0.7:
            decision = 'strong'
            confidence_level = 'high'
        elif prediction_proba[1] < 0.3:
            decision = 'weak'
            confidence_level = 'high'
        else:
            decision = 'borderline'
            confidence_level = 'low'

        # Add explainability
        feature_names = list(features.keys())
        feature_importances = self.model.feature_importances_

        # Rank features by importance
        feature_importance_pairs = sorted(
            zip(feature_names, feature_importances),
            key=lambda x: x[1],
            reverse=True
        )

        # Get top 3 factors
        top_factors = [
            {
                'feature': name,
                'importance': float(importance),
                'value': int(features[name]) if isinstance(features[name], int) else features[name]
            }
            for name, importance in feature_importance_pairs[:3]
        ]

        return {
            'prediction': predicted_quality,
            'confidence': float(max_prob),
            'confidence_level': confidence_level,
            'decision': decision,
            'raw_prediction': int(prediction),
            'probabilities': probabilities,
            'features': features,
            'top_factors': top_factors,
            'success': True
        }