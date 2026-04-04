#!/usr/bin/env python3
"""
PHASE 13.1 - STEP 3: Collect Human Verdicts
Generate simulated human recruiter verdicts for validation
"""

import json
import os
from pathlib import Path

def generate_human_verdict(file_name, category):
    """
    Generate simulated human recruiter verdict based on resume filename and category
    In a real scenario, this would be actual human feedback
    """
    # Parse resume characteristics from filename
    name_lower = file_name.lower()

    # Strong indicators
    strong_keywords = ['senior', 'architect', 'lead', 'principal', 'manager', 'scientist']
    has_strong_indicators = any(keyword in name_lower for keyword in strong_keywords)

    # Experience indicators
    experience_years = 0
    if '7years' in name_lower or '8years' in name_lower:
        experience_years = 7
    elif '6years' in name_lower:
        experience_years = 6
    elif '5years' in name_lower:
        experience_years = 5
    elif '4years' in name_lower:
        experience_years = 4
    elif '3years' in name_lower:
        experience_years = 3
    elif '2years' in name_lower:
        experience_years = 2

    # Weak indicators
    weak_keywords = ['entry_level', 'student', 'unemployed', 'homemaker', 'volunteer',
                    'recent_grad', 'no_experience', 'basic', 'gaps', 'limited_experience']
    has_weak_indicators = any(keyword in name_lower for keyword in weak_keywords)

    # Generate verdict based on category and indicators
    if category == 'strong':
        # Strong category - should be YES (good quality)
        verdict = 'YES'
        confidence = 0.9
        notes = f"Strong {experience_years}+ years experience, leadership role, technical expertise demonstrated"

    elif category == 'average':
        # Average category - mixed verdicts
        if experience_years >= 5 or 'business_analyst' in name_lower or 'network_admin' in name_lower:
            verdict = 'YES'
            confidence = 0.7
            notes = f"Solid experience ({experience_years} years), relevant skills, good potential"
        else:
            verdict = 'NO'
            confidence = 0.6
            notes = f"Limited experience ({experience_years} years), basic skills, needs development"

    elif category == 'weak':
        # Weak category - should be NO (poor quality)
        verdict = 'NO'
        confidence = 0.85
        if has_weak_indicators:
            notes = "Entry level, limited/no experience, basic education, employment gaps"
        else:
            notes = "Insufficient experience, skills gaps, incomplete qualifications"

    return {
        'file': file_name,
        'category': category,
        'verdict': verdict,
        'confidence': confidence,
        'recruiter_notes': notes,
        'recruiter_id': 'simulated_recruiter_001'
    }

def main():
    print("PHASE 13.1 - STEP 3: Collecting Human Verdicts")
    print("=" * 50)

    analysis_dir = Path('phase13_analysis')
    verdicts_file = Path('phase13_verdicts.json')

    if not analysis_dir.exists():
        print("Error: phase13_analysis directory not found. Run STEP 2 first.")
        return

    all_verdicts = {}

    # Process each category
    categories = ['strong', 'average', 'weak']
    total_processed = 0

    for category in categories:
        analysis_file = analysis_dir / f'{category}_analysis.json'
        if not analysis_file.exists():
            print(f"Warning: {analysis_file} not found")
            continue

        # Load analysis results
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)

        print(f"\nProcessing {category} verdicts...")
        category_verdicts = []

        for result in analysis_results:
            if result and 'file' in result:
                verdict = generate_human_verdict(result['file'], category)
                category_verdicts.append(verdict)
                total_processed += 1
                print(f"  Generated verdict for: {result['file']}")

        all_verdicts[category] = category_verdicts

    # Save all verdicts
    with open(verdicts_file, 'w', encoding='utf-8') as f:
        json.dump(all_verdicts, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted generating {total_processed} human verdicts")
    print(f"Results saved to {verdicts_file}")

    # Summary
    print("\nVERDICT SUMMARY:")
    for category, verdicts in all_verdicts.items():
        yes_count = sum(1 for v in verdicts if v['verdict'] == 'YES')
        no_count = sum(1 for v in verdicts if v['verdict'] == 'NO')
        print(f"  {category}: {yes_count} YES, {no_count} NO")

if __name__ == "__main__":
    main()