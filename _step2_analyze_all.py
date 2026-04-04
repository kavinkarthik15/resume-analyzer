#!/usr/bin/env python3
"""
PHASE 14 - Analyze All Resumes with REAL Feature Extraction
Fixed version with proper feature engineering
"""

import os
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append('backend')
sys.path.append('backend/models')


def load_ml_model():
    """Load the ML model directly"""
    try:
        import joblib
        model_path = 'ml/models/random_forest_model.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print("ML model loaded successfully from pickle file")
            return model
        else:
            print(f"Model file not found at {model_path}")
            return None
    except Exception as e:
        print(f"Error loading ML model: {e}")
        return None


def extract_years_experience(text):
    """Extract years of experience from dates in resume"""
    years = re.findall(r'(20\d{2})', text)
    
    if len(years) >= 2:
        years = list(map(int, years))
        return max(years) - min(years)
    
    return 0


def count_skills(text):
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


def leadership_score(text):
    """Extract leadership indicators from resume"""
    leadership_words = [
        "led", "managed", "mentored", "directed", "owned", 
        "lead", "leading", "leading team", "team lead", "senior",
        "principal", "architect", "head of", "director"
    ]
    
    text_lower = text.lower()
    return sum(1 for word in leadership_words if word in text_lower)


def achievement_score(text):
    """Count quantified achievements (%, $, numbers with impact)"""
    # Look for percentages, dollar amounts, and numbers followed by x
    return len(re.findall(r'(\d+%|\$\d+k?|\d+x|\d+\s*(million|billion|thousand|k))', text, re.IGNORECASE))


def education_score(text):
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


def project_count(text):
    """Count projects mentioned in resume"""
    return text.lower().count("project")


def certification_count(text):
    """Count certifications mentioned in resume"""
    return text.lower().count("certified") + text.lower().count("certification")


def extract_features(text):
    """REAL Feature extraction - PHASE 14 FIX"""
    return {
        "years_experience": extract_years_experience(text),
        "skill_count": count_skills(text),
        "leadership_score": leadership_score(text),
        "achievement_score": achievement_score(text),
        "education_score": education_score(text),
        "project_count": project_count(text),
        "certification_count": certification_count(text),
    }




def analyze_resume_simple(file_path, category, ml_model):
    """Analyze a single resume using direct ML model with REAL features"""
    
    # STEP 6: Handle Edge Cases
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        # Edge case: Resume too short
        if len(resume_text.strip()) < 50:
            return {
                'file': os.path.basename(file_path),
                'category': category,
                'prediction': 'ERROR',
                'confidence': 0.0,
                'error': 'Resume too short (< 50 characters)',
                'success': False
            }
        
        # Extract REAL features (PHASE 14 FIX)
        features = extract_features(resume_text)
        
        # Edge case: No content detected
        total_features = sum(features.values())
        if total_features == 0:
            return {
                'file': os.path.basename(file_path),
                'category': category,
                'prediction': 'ERROR',
                'confidence': 0.0,
                'error': 'No identifiable resume content',
                'success': False
            }

        # Convert to proper format for ML model
        import pandas as pd
        feature_df = pd.DataFrame([features])

        # Make prediction
        prediction_proba = ml_model.predict_proba(feature_df)[0]
        prediction = ml_model.predict(feature_df)[0]

        # STEP 5: Add Confidence Thresholds
        # Determine confidence threshold based on probabilities
        max_prob = max(prediction_proba)
        
        # Map prediction to quality category
        n_classes = len(prediction_proba)
        if n_classes == 2:
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
        else:
            # Multi-class classification
            quality_map = {0: 'weak', 1: 'average', 2: 'strong'}
            predicted_quality = quality_map.get(prediction, 'unknown')
            probabilities = {
                'weak': float(prediction_proba[0]),
                'average': float(prediction_proba[1]),
                'strong': float(prediction_proba[2])
            }
            decision = predicted_quality
            confidence_level = 'high' if max_prob > 0.7 else 'low'

        # STEP 4: Add Explainability Output
        feature_names = list(features.keys())
        feature_importances = ml_model.feature_importances_
        
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
            'file': os.path.basename(file_path),
            'category': category,
            'prediction': predicted_quality,
            'confidence': float(max_prob),
            'confidence_level': confidence_level,  # NEW: high/low indicator
            'decision': decision,  # NEW: With threshold applied
            'raw_prediction': int(prediction),
            'probabilities': probabilities,
            'features': features,
            'top_factors': top_factors,  # NEW: Explainability
            'success': True
        }

    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return {
            'file': os.path.basename(file_path),
            'category': category,
            'prediction': 'ERROR',
            'confidence': 0.0,
            'error': str(e),
            'success': False
        }

def main():
    print("PHASE 14 - Analyzing All Resumes with REAL Features")
    print("=" * 55)

    # Load ML model
    print("Loading ML model...")
    ml_model = load_ml_model()
    if ml_model is None:
        print("Failed to load ML model. Exiting.")
        return

    resumes_dir = Path('phase13_resumes')
    analysis_dir = Path('phase13_analysis')
    analysis_dir.mkdir(exist_ok=True)

    all_results = {}

    # Process each category
    categories = ['strong', 'average', 'weak']
    total_processed = 0

    for category in categories:
        category_dir = resumes_dir / category
        if not category_dir.exists():
            print(f"Warning: {category_dir} does not exist")
            continue

        print(f"\nProcessing {category} resumes...")
        category_results = []

        # Process all txt files in category
        for resume_file in category_dir.glob('*.txt'):
            print(f"  Analyzing: {resume_file.name}")
            result = analyze_resume_simple(resume_file, category, ml_model)
            category_results.append(result)
            total_processed += 1

        all_results[category] = category_results

        # Save category results
        output_file = analysis_dir / f'{category}_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_results, f, indent=2, ensure_ascii=False)

    # Save all results
    output_file = analysis_dir / 'all_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted analysis of {total_processed} resumes")
    print(f"Results saved to {analysis_dir}/")

    # Summary
    print("\nSUMMARY:")
    for category, results in all_results.items():
        successful = sum(1 for r in results if r['success'])
        print(f"  {category}: {successful}/{len(results)} successful")

if __name__ == "__main__":
    main()