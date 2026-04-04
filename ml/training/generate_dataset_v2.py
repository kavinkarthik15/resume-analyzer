"""
PHASE 14 - Generate Training Dataset with REAL Features
Creates synthetic training data using proper feature extraction
"""

import os
import random
from pathlib import Path
import re

import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = SCRIPT_DIR / "dataset.csv"


# Copy of feature extraction functions from _step2_analyze_all.py
def extract_years_experience(text):
    """Extract years of experience from dates"""
    years = re.findall(r'(20\d{2})', text)
    if len(years) >= 2:
        years = list(map(int, years))
        return max(years) - min(years)
    return 0


def count_skills(text):
    """Count technology skills"""
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
    """Extract leadership indicators"""
    leadership_words = [
        "led", "managed", "mentored", "directed", "owned", 
        "lead", "leading", "team lead", "senior",
        "principal", "architect", "head of", "director"
    ]
    text_lower = text.lower()
    return sum(1 for word in leadership_words if word in text_lower)


def achievement_score(text):
    """Count quantified achievements"""
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
    """Count projects"""
    return text.lower().count("project")


def certification_count(text):
    """Count certifications"""
    return text.lower().count("certified") + text.lower().count("certification")


def generate_synthetic_resume(quality_level):
    """Generate synthetic resume text with features matching quality level"""
    if quality_level == "strong":
        # Strong resume characteristics
        years = random.randint(6, 10)
        skills = random.randint(12, 18)
        leadership = random.randint(3, 6)
        achievements = random.randint(4, 8)
        education = random.randint(2, 3)
        projects = random.randint(1, 3)
        certs = random.randint(1, 3)
        
    elif quality_level == "average":
        # Average resume characteristics
        years = random.randint(3, 6)
        skills = random.randint(6, 10)
        leadership = random.randint(1, 2)
        achievements = random.randint(1, 3)
        education = random.randint(1, 2)
        projects = random.randint(0, 1)
        certs = random.randint(0, 1)
        
    else:  # weak
        # Weak resume characteristics
        years = random.randint(0, 2)
        skills = random.randint(2, 5)
        leadership = 0
        achievements = random.randint(0, 1)
        education = random.randint(0, 1)
        projects = 0
        certs = 0
    
    # Build synthetic resume text
    resume = f"Resume for {quality_level} candidate\n\n"
    
    # Experience section
    if years > 0:
        resume += f"EXPERIENCE\n"
        resume += f"Position at Company - {years} years\n"
        for _ in range(leadership):
            resume += f"- Led and managed team initiatives\n"
        for _ in range(achievements):
            resume += f"- Achieved {random.randint(10,50)}% improvement\n"
        resume += "\n"
    
    # Skills section
    if skills > 0:
        resume += f"SKILLS\n"
        for _ in range(skills // 3):  # Multiple skill mentions
            resume += f"- Python, Java, SQL, AWS, Docker, Kubernetes, React,\n"
        resume += "\n"
    
    # Education section
    if education > 0:
        if education == 3:
            resume += "EDUCATION\nPhD in Computer Science\nMS in Data Science\n"
        elif education == 2:
            resume += "EDUCATION\nMaster's Degree in Computer Science\n"
        else:
            resume += "EDUCATION\nBachelor's Degree\n"
        resume += "\n"
    
    # Projects section
    if projects > 0:
        for _ in range(projects):
            resume += f"PROJECT - {random.randint(2015, 2024)}\n"
            resume += "- Built scalable system\n"
        resume += "\n"
    
    # Certifications section
    if certs > 0:
        for _ in range(certs):
            resume += f"CERTIFICATIONS\n- Certified Professional\n"
        resume += "\n"
    
    return resume


# Generate training data
n_samples = 200
records = []

# Create balanced dataset
quality_distribution = [
    ("weak", 60),    # 60 weak resumes
    ("average", 70), # 70 average resumes  
    ("strong", 70)   # 70 strong resumes
]

for quality, count in quality_distribution:
    for _ in range(count):
        # Generate synthetic resume
        resume_text = generate_synthetic_resume(quality)
        
        # Extract features
        features = {
            "years_experience": extract_years_experience(resume_text),
            "skill_count": count_skills(resume_text),
            "leadership_score": leadership_score(resume_text),
            "achievement_score": achievement_score(resume_text),
            "education_score": education_score(resume_text),
            "project_count": project_count(resume_text),
            "certification_count": certification_count(resume_text),
        }
        
        # Create label: 1 for strong/average, 0 for weak
        # Or use: 0=weak, 1=average, 2=strong for multi-class
        label = 0 if quality == "weak" else 1
        
        features["shortlisted"] = label
        records.append(features)

# Create DataFrame
df = pd.DataFrame(records)

# Save to CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Generated {len(records)} training samples")
print(f"✅ Dataset saved to {OUTPUT_CSV}")
print(f"\nFeature columns: {list(df.columns)}")
print(f"\nDataset shape: {df.shape}")
print(f"Classes distribution:\n{df['shortlisted'].value_counts()}")
