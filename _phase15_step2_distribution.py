#!/usr/bin/env python3
"""
PHASE 15 - STEP 2: Feature Distribution Analysis
Check feature ranges and identify red flags
"""

import pandas as pd
from pathlib import Path

def analyze_distribution():
    """Analyze feature distribution in training dataset"""
    print("PHASE 15 - STEP 2: Feature Distribution Analysis")
    print("=" * 70)
    
    dataset_path = Path('ml/training/dataset.csv')
    
    if not dataset_path.exists():
        print(f"Error: Dataset not found: {dataset_path}")
        return
    
    # Load dataset
    df = pd.read_csv(dataset_path)
    
    print(f"\nDataset loaded: {len(df)} samples, {len(df.columns)} features\n")
    
    # Display statistics
    print("FEATURE STATISTICS:")
    print("-" * 70)
    stats = df.describe()
    print(stats)
    
    # Check for red flags
    print("\n" + "=" * 70)
    print("RED FLAG ANALYSIS:")
    print("=" * 70)
    
    expected_ranges = {
        'years_experience': (0, 15),
        'skill_count': (0, 15),
        'leadership_score': (0, 5),
        'achievement_score': (0, 5),
        'education_score': (0, 3),
        'project_count': (0, 5),
        'certification_count': (0, 5),
    }
    
    red_flags = []
    
    for feature, (min_expected, max_expected) in expected_ranges.items():
        if feature not in df.columns:
            continue
            
        col = df[feature]
        min_val = col.min()
        max_val = col.max()
        std_val = col.std()
        unique_count = col.nunique()
        
        # Check for issues
        flag = False
        reasons = []
        
        # All values same?
        if unique_count == 1:
            reasons.append("All values identical (broken feature)")
            flag = True
        
        # Outside expected range?
        if max_val > max_expected:
            reasons.append(f"Max value {max_val} exceeds expected {max_expected}")
            flag = True
        
        # Extremely high variance?
        if std_val > max_expected * 2:
            reasons.append(f"Std dev {std_val:.2f} very high (noisy)")
            flag = True
        
        status = "🚨 RED FLAG" if flag else "✅ OK"
        print(f"\n{feature}:")
        print(f"  Range: [{min_val:.2f}, {max_val:.2f}]")
        print(f"  Expected: [{min_expected}, {max_expected}]")
        print(f"  Std Dev: {std_val:.2f}")
        print(f"  Unique values: {unique_count}")
        print(f"  Status: {status}")
        
        if reasons:
            for reason in reasons:
                print(f"    → {reason}")
            red_flags.append((feature, reasons))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    
    if red_flags:
        print(f"🚨 Found {len(red_flags)} potential issues:")
        for feature, reasons in red_flags:
            print(f"  - {feature}: {', '.join(reasons)}")
    else:
        print("✅ All features within expected ranges!")
    
    # Class distribution
    print("\n" + "=" * 70)
    print("CLASS DISTRIBUTION:")
    print("=" * 70)
    print(df['shortlisted'].value_counts())
    print("\nClass balance:")
    class_pct = df['shortlisted'].value_counts(normalize=True) * 100
    for cls, pct in class_pct.items():
        print(f"  Class {cls}: {pct:.1f}%")


if __name__ == "__main__":
    analyze_distribution()
