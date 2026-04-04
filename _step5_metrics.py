#!/usr/bin/env python3
"""
PHASE 13.1 - STEP 5: Calculate Final Metrics
Generate comprehensive validation metrics and production readiness assessment
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_csv_file(file_path):
    """Load CSV file safely"""
    try:
        import csv
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def calculate_metrics(validation_data):
    """Calculate comprehensive validation metrics"""
    metrics = {
        'total_resumes': len(validation_data),
        'overall_agreement': 0,
        'category_breakdown': {},
        'ml_accuracy_by_category': {},
        'human_reliability': {},
        'error_analysis': {},
        'production_readiness': {}
    }

    # Calculate overall agreement
    agreements = sum(1 for row in validation_data if row['agreement'] == 'YES')
    metrics['overall_agreement'] = agreements / metrics['total_resumes']

    # Category breakdown
    categories = {}
    for row in validation_data:
        cat = row['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'agreements': 0, 'ml_yes': 0, 'human_yes': 0}

        categories[cat]['total'] += 1
        if row['agreement'] == 'YES':
            categories[cat]['agreements'] += 1
        if row['ml_verdict'] == 'YES':
            categories[cat]['ml_yes'] += 1
        if row['human_verdict'] == 'YES':
            categories[cat]['human_yes'] += 1

    # Calculate category metrics
    for cat, data in categories.items():
        agreement_rate = data['agreements'] / data['total']
        metrics['category_breakdown'][cat] = {
            'agreement_rate': agreement_rate,
            'agreements': data['agreements'],
            'ml_positive_rate': data['ml_yes'] / data['total'],
            'human_positive_rate': data['human_yes'] / data['total'],
            'total_resumes': data['total']
        }

    # Error analysis
    false_positives = sum(1 for row in validation_data
                         if row['ml_verdict'] == 'YES' and row['human_verdict'] == 'NO')
    false_negatives = sum(1 for row in validation_data
                         if row['ml_verdict'] == 'NO' and row['human_verdict'] == 'YES')

    metrics['error_analysis'] = {
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'false_positive_rate': false_positives / metrics['total_resumes'],
        'false_negative_rate': false_negatives / metrics['total_resumes']
    }

    # Production readiness assessment
    agreement_threshold = 0.80  # 80%
    min_category_agreement = 0.70  # 70% per category

    overall_pass = metrics['overall_agreement'] >= agreement_threshold
    category_pass = all(cat_data['agreement_rate'] >= min_category_agreement
                       for cat_data in metrics['category_breakdown'].values())

    metrics['production_readiness'] = {
        'overall_agreement_threshold': agreement_threshold,
        'category_agreement_threshold': min_category_agreement,
        'overall_pass': overall_pass,
        'category_pass': category_pass,
        'ready_for_production': overall_pass and category_pass,
        'recommendations': []
    }

    # Generate recommendations
    if not overall_pass:
        metrics['production_readiness']['recommendations'].append(
            f"Overall agreement ({metrics['overall_agreement']:.1%}) below threshold ({agreement_threshold:.1%})"
        )

    for cat, cat_data in metrics['category_breakdown'].items():
        if cat_data['agreement_rate'] < min_category_agreement:
            metrics['production_readiness']['recommendations'].append(
                f"{cat.capitalize()} category agreement ({cat_data['agreement_rate']:.1%}) below threshold ({min_category_agreement:.1%})"
            )

    if false_positives > false_negatives:
        metrics['production_readiness']['recommendations'].append(
            "Model has high false positive rate - too many weak resumes classified as strong"
        )
    elif false_negatives > false_positives:
        metrics['production_readiness']['recommendations'].append(
            "Model has high false negative rate - too many strong resumes classified as weak"
        )

    return metrics

def main():
    print("PHASE 13.1 - STEP 5: Calculating Final Metrics")
    print("=" * 50)

    # Load validation table
    table_file = Path('phase13_validation_table.csv')
    validation_data = load_csv_file(table_file)

    if not validation_data:
        print("Error: Could not load validation table")
        return

    # Calculate metrics
    metrics = calculate_metrics(validation_data)

    # Save metrics
    metrics_file = Path('phase13_metrics.json')
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # Generate report
    report_file = Path('phase13_final_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("PHASE 13.1 - REAL-WORLD VALIDATION FINAL REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total resumes analyzed: {metrics['total_resumes']}\n")
        f.write(f"Overall agreement: {metrics['overall_agreement']:.1%}\n")
        f.write(f"Production ready: {'YES' if metrics['production_readiness']['ready_for_production'] else 'NO'}\n\n")

        f.write("CATEGORY BREAKDOWN\n")
        f.write("-" * 20 + "\n")
        for cat, data in metrics['category_breakdown'].items():
            f.write(f"{cat.capitalize()} Category:\n")
            f.write(f"  Agreement: {data['agreement_rate']:.1%} ({data['agreements']}/{data['total_resumes']})\n")
            f.write(f"  ML positive rate: {data['ml_positive_rate']:.1%}\n")
            f.write(f"  Human positive rate: {data['human_positive_rate']:.1%}\n\n")

        f.write("ERROR ANALYSIS\n")
        f.write("-" * 15 + "\n")
        f.write(f"False positives: {metrics['error_analysis']['false_positives']} ({metrics['error_analysis']['false_positive_rate']:.1%})\n")
        f.write(f"False negatives: {metrics['error_analysis']['false_negatives']} ({metrics['error_analysis']['false_negative_rate']:.1%})\n\n")

        f.write("PRODUCTION READINESS ASSESSMENT\n")
        f.write("-" * 35 + "\n")
        f.write(f"Overall threshold: {metrics['production_readiness']['overall_agreement_threshold']:.1%}\n")
        f.write(f"Category threshold: {metrics['production_readiness']['category_agreement_threshold']:.1%}\n")
        f.write(f"Overall pass: {'YES' if metrics['production_readiness']['overall_pass'] else 'NO'}\n")
        f.write(f"Category pass: {'YES' if metrics['production_readiness']['category_pass'] else 'NO'}\n")
        f.write(f"READY FOR PRODUCTION: {'YES' if metrics['production_readiness']['ready_for_production'] else 'NO'}\n\n")

        if metrics['production_readiness']['recommendations']:
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 15 + "\n")
            for rec in metrics['production_readiness']['recommendations']:
                f.write(f"• {rec}\n")
        else:
            f.write("✅ No major issues identified\n")

    print(f"\nMetrics saved to {metrics_file}")
    print(f"Report saved to {report_file}")

    # Print summary to console
    print("\n" + "=" * 60)
    print("FINAL VALIDATION RESULTS")
    print("=" * 60)
    print(f"Overall Agreement: {metrics['overall_agreement']:.1%}")
    print(f"Production Ready: {'YES' if metrics['production_readiness']['ready_for_production'] else 'NO'}")

    if not metrics['production_readiness']['ready_for_production']:
        print("\nNext Steps:")
        print("1. Retrain ML model with better features")
        print("2. Improve feature engineering")
        print("3. Collect more diverse training data")
        print("4. Re-run validation after improvements")

if __name__ == "__main__":
    main()