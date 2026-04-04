#!/usr/bin/env python3
"""
PHASE 13.1 - STEP 4: Build Validation Table
Create comparison table between ML predictions and human verdicts
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def main():
    print("PHASE 13.1 - STEP 4: Building Validation Table")
    print("=" * 50)

    # Load analysis results and verdicts
    analysis_file = Path('phase13_analysis/all_analysis_results.json')
    verdicts_file = Path('phase13_verdicts.json')
    table_file = Path('phase13_validation_table.csv')

    analysis_data = load_json_file(analysis_file)
    verdicts_data = load_json_file(verdicts_file)

    if not analysis_data or not verdicts_data:
        print("Error: Missing analysis or verdicts data")
        return

    # Build validation table
    validation_rows = []
    category_stats = defaultdict(lambda: {'total': 0, 'matches': 0, 'ml_yes': 0, 'human_yes': 0})

    # Process each category
    categories = ['strong', 'average', 'weak']

    for category in categories:
        analysis_results = analysis_data.get(category, [])
        verdicts_results = verdicts_data.get(category, [])

        # Create lookup dict for verdicts
        verdicts_lookup = {v['file']: v for v in verdicts_results}

        print(f"\nProcessing {category} category ({len(analysis_results)} resumes)...")

        for analysis in analysis_results:
            file_name = analysis['file']
            verdict = verdicts_lookup.get(file_name)

            if not verdict:
                print(f"  Warning: No verdict found for {file_name}")
                continue

            # Convert predictions to YES/NO
            ml_prediction = analysis['prediction']
            if ml_prediction in ['strong', 'average']:
                ml_verdict = 'YES'
            else:  # weak
                ml_verdict = 'NO'

            human_verdict = verdict['verdict']

            # Check agreement
            agreement = 'YES' if ml_verdict == human_verdict else 'NO'

            # Add to table
            row = {
                'file': file_name,
                'category': category,
                'ml_prediction': ml_prediction,
                'ml_verdict': ml_verdict,
                'human_verdict': human_verdict,
                'agreement': agreement,
                'ml_confidence': round(analysis['confidence'], 3),
                'human_confidence': round(verdict['confidence'], 3),
                'human_notes': verdict['recruiter_notes']
            }
            validation_rows.append(row)

            # Update stats
            category_stats[category]['total'] += 1
            if agreement == 'YES':
                category_stats[category]['matches'] += 1
            if ml_verdict == 'YES':
                category_stats[category]['ml_yes'] += 1
            if human_verdict == 'YES':
                category_stats[category]['human_yes'] += 1

    # Write CSV table
    if validation_rows:
        fieldnames = ['file', 'category', 'ml_prediction', 'ml_verdict', 'human_verdict',
                     'agreement', 'ml_confidence', 'human_confidence', 'human_notes']

        with open(table_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(validation_rows)

        print(f"\nValidation table saved to {table_file}")

    # Print summary
    print("\nVALIDATION SUMMARY:")
    print("-" * 50)
    total_matches = 0
    total_resumes = 0

    for category, stats in category_stats.items():
        if stats['total'] > 0:
            agreement_rate = (stats['matches'] / stats['total']) * 100
            print(f"{category.capitalize()} Category:")
            print(f"  Total resumes: {stats['total']}")
            print(f"  Agreement: {stats['matches']}/{stats['total']} ({agreement_rate:.1f}%)")
            print(f"  ML predicted YES: {stats['ml_yes']}")
            print(f"  Human judged YES: {stats['human_yes']}")
            print()

            total_matches += stats['matches']
            total_resumes += stats['total']

    if total_resumes > 0:
        overall_agreement = (total_matches / total_resumes) * 100
        print(f"OVERALL AGREEMENT: {total_matches}/{total_resumes} ({overall_agreement:.1f}%)")

        if overall_agreement >= 80:
            print("✅ PASSED: Agreement ≥ 80% - System ready for production!")
        else:
            print("❌ FAILED: Agreement < 80% - Model needs retraining")

if __name__ == "__main__":
    main()