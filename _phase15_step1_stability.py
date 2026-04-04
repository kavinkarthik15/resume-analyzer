#!/usr/bin/env python3
"""
PHASE 15 - STEP 1: Validate Feature Extraction Stability
Test that same resume produces identical features every time
"""

import json
from pathlib import Path

# Import feature extraction functions
import sys
sys.path.append('.')
from _step2_analyze_all import extract_features

def test_stability():
    """Test that feature extraction is deterministic"""
    print("PHASE 15 - STEP 1: Feature Stability Test")
    print("=" * 60)
    
    # Test with a strong resume
    test_file = Path('phase13_resumes/strong/senior_data_scientist_7years.txt')
    
    if not test_file.exists():
        print(f"Error: Test file not found: {test_file}")
        return
    
    # Read resume
    with open(test_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    # Extract features 5 times
    results = []
    print(f"\nTesting: {test_file.name}")
    print("Extracting features 5 times...\n")
    
    for i in range(5):
        features = extract_features(resume_text)
        results.append(features)
        print(f"Run {i+1}: {features}")
    
    # Check consistency
    print("\n" + "=" * 60)
    print("CONSISTENCY CHECK")
    print("=" * 60)
    
    all_identical = True
    for key in results[0].keys():
        values = [r[key] for r in results]
        is_consistent = len(set(values)) == 1
        status = "✅ CONSISTENT" if is_consistent else "❌ INCONSISTENT"
        print(f"{key:25} → {status} (values: {values})")
        if not is_consistent:
            all_identical = False
    
    print("\n" + "=" * 60)
    if all_identical:
        print("✅ RESULT: Feature extraction is deterministic and stable!")
    else:
        print("❌ RESULT: Feature extraction has inconsistencies!")
    print("=" * 60)
    
    return all_identical


if __name__ == "__main__":
    test_stability()
