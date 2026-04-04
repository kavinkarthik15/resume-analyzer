#!/usr/bin/env python3
"""
PHASE 15 - STEP 3: Feature Importance Analysis
Understand what the model relies on
"""

import joblib
import pandas as pd
from pathlib import Path

def analyze_feature_importance():
    """Analyze which features the model uses most"""
    print("PHASE 15 - STEP 3: Feature Importance Analysis")
    print("=" * 70)
    
    model_path = Path('ml/models/random_forest_model.pkl')
    dataset_path = Path('ml/training/dataset.csv')
    
    if not model_path.exists():
        print(f"Error: Model not found: {model_path}")
        return
    
    if not dataset_path.exists():
        print(f"Error: Dataset not found: {dataset_path}")
        return
    
    # Load model and dataset
    model = joblib.load(model_path)
    df = pd.read_csv(dataset_path)
    
    # Get feature names (exclude target)
    feature_names = [col for col in df.columns if col != "shortlisted"]
    feature_importances = model.feature_importances_
    
    print(f"\nModel: Random Forest with {model.n_estimators} trees")
    print(f"Features: {len(feature_names)}\n")
    
    # Sort by importance
    importance_pairs = sorted(
        zip(feature_names, feature_importances),
        key=lambda x: x[1],
        reverse=True
    )
    
    print("FEATURE IMPORTANCE RANKING:")
    print("-" * 70)
    print(f"{'Rank':<6} {'Feature':<30} {'Importance':<15} {'Percentage':<12}")
    print("-" * 70)
    
    total_importance = sum(feature_importances)
    cumulative = 0
    
    for rank, (feature, importance) in enumerate(importance_pairs, 1):
        percentage = (importance / total_importance) * 100
        cumulative += percentage
        bar_width = int(percentage / 2)
        bar = "█" * bar_width
        
        print(f"{rank:<6} {feature:<30} {importance:>7.4f} ({percentage:>5.1f}%) {bar}")
    
    # Check for fragility
    print("\n" + "=" * 70)
    print("MODEL FRAGILITY ANALYSIS:")
    print("=" * 70)
    
    top_3_importance = sum([imp for _, imp in importance_pairs[:3]])
    top_3_pct = (top_3_importance / total_importance) * 100
    
    top_1_pct = (importance_pairs[0][1] / total_importance) * 100
    
    print(f"\nTop 1 feature dominance: {top_1_pct:.1f}%")
    print(f"Top 3 features dominance: {top_3_pct:.1f}%")
    
    print("\n⚠️ FRAGILITY CHECK:")
    if top_1_pct > 70:
        print(f"  🚨 RED FLAG: Single feature dominates ({top_1_pct:.1f}%)")
        print(f"     → Model is fragile and may fail if this feature changes")
    elif top_1_pct > 50:
        print(f"  ⚠️ WARNING: One feature too important ({top_1_pct:.1f}%)")
        print(f"     → Consider collecting more diverse features")
    else:
        print(f"  ✅ HEALTHY: Features well-balanced ({top_1_pct:.1f}% max)")
    
    if top_3_pct < 70:
        print(f"  ✅ Good: Decisions use multiple signals ({top_3_pct:.1f}%)")
    else:
        print(f"  ⚠️ Top 3 features too dominant ({top_3_pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("WHAT THIS MEANS:")
    print("=" * 70)
    print("\nThe model makes decisions by weighing:")
    for rank, (feature, importance) in enumerate(importance_pairs[:5], 1):
        percentage = (importance / total_importance) * 100
        print(f"  {rank}. {feature:<30} {percentage:>5.1f}%")
    
    return importance_pairs


if __name__ == "__main__":
    analyze_feature_importance()
