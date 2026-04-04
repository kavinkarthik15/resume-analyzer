"""
PHASE 12: ML Model Evaluation & Metrics
Comprehensive evaluation of model performance on test data
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.model_selection import train_test_split

import joblib

SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_PATH = SCRIPT_DIR / "dataset.csv"
MODEL_PATH = SCRIPT_DIR.parent / "models" / "random_forest_model.pkl"
OUTPUT_PATH = SCRIPT_DIR / "evaluation_results.json"

def evaluate_model():
    """Evaluate model performance on test set"""
    
    print("=" * 60)
    print("PHASE 12: ML MODEL EVALUATION")
    print("=" * 60)
    
    # Load dataset
    print(f"\n📂 Loading dataset from {DATASET_PATH}")
    data = pd.read_csv(DATASET_PATH)
    
    feature_columns = [col for col in data.columns if col != "shortlisted"]
    X = data[feature_columns]
    y = data["shortlisted"]
    
    # Train-test split (same as training)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Load model
    print(f"🤖 Loading model from {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    print("\n📊 CALCULATING METRICS...")
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"✅ Accuracy:  {accuracy * 100:.2f}%")
    print(f"✅ Precision: {precision * 100:.2f}%")
    print(f"✅ Recall:    {recall * 100:.2f}%")
    print(f"✅ F1 Score:  {f1 * 100:.2f}%")
    print(f"✅ ROC AUC:   {roc_auc * 100:.2f}%")
    
    # Confusion Matrix
    print("\n🎯 CONFUSION MATRIX")
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print(f"   Predicted")
    print(f"   0      1")
    print(f"A 0  {tn:3d}  {fp:3d}")
    print(f"c 1  {fn:3d}  {tp:3d}")
    print(f"t")
    print(f"u")
    print(f"a")
    print(f"l")
    
    print("\n🎲 MISCLASSIFICATION ANALYSIS")
    print(f"True Negatives (TN):  {tn} - Correctly identified non-shortlist")
    print(f"False Positives (FP): {fp} - Falsely marked shortlist")
    print(f"False Negatives (FN): {fn} - Missed shortlist candidates")
    print(f"True Positives (TP):  {tp} - Correctly identified shortlist")
    
    # Classification report
    print("\n📈 DETAILED CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred, target_names=["Not Shortlisted", "Shortlisted"]))
    
    # Feature importance
    print("\n⭐ FEATURE IMPORTANCE (Top 10)")
    importances = model.feature_importances_
    feature_importance_dict = dict(zip(feature_columns, importances))
    sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    for i, (feature, importance) in enumerate(sorted_features[:10], 1):
        print(f"{i:2d}. {feature:35s} {importance:6.4f} {'█' * int(importance * 100)}")
    
    # Save evaluation results
    evaluation_results = {
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
        },
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "feature_importance": {
            name: float(imp) for name, imp in sorted_features
        },
        "model_quality_assessment": assess_model_quality(accuracy, precision, recall, f1),
        "test_set_size": int(len(X_test)),
        "training_set_size": int(len(X_train)),
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"\n✅ Evaluation results saved to: {OUTPUT_PATH}")
    
    return evaluation_results

def assess_model_quality(accuracy, precision, recall, f1):
    """Assess overall model quality based on metrics"""
    score = (accuracy + precision + recall + f1) / 4
    
    if score >= 0.85:
        rating = "EXCELLENT"
        recommendation = "Ready for production with confidence"
    elif score >= 0.75:
        rating = "GOOD"
        recommendation = "Suitable with monitoring"
    elif score >= 0.65:
        rating = "FAIR"
        recommendation = "Needs more training data or feature engineering"
    else:
        rating = "POOR"
        recommendation = "Requires significant improvements"
    
    return {
        "average_score": float(score),
        "rating": rating,
        "recommendation": recommendation
    }

if __name__ == "__main__":
    results = evaluate_model()
