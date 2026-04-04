#!/usr/bin/env python3
"""
PHASE 15 - STEP 1 Extended: Test All Resumes for Stability
"""

import json
from pathlib import Path
from _step2_analyze_all import extract_features

def test_all_resumes_stability():
    """Test all resumes for consistency"""
    print("PHASE 15 - EXTENDED: Full System Stability Test")
    print("=" * 80)
    
    resumes_dir = Path('phase13_resumes')
    test_results = {}
    
    for category in ['strong', 'average', 'weak']:
        category_dir = resumes_dir / category
        if not category_dir.exists():
            continue
        
        test_results[category] = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print(f"\nTesting {category.upper()} resumes:")
        print("-" * 80)
        
        for resume_file in sorted(category_dir.glob('*.txt')):
            with open(resume_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract features twice
            features1 = extract_features(text)
            features2 = extract_features(text)
            
            # Check consistency
            is_consistent = features1 == features2
            
            test_results[category]['total'] += 1
            status = "✅ PASS" if is_consistent else "❌ FAIL"
            
            if is_consistent:
                test_results[category]['passed'] += 1
                print(f"  {resume_file.name:<40} {status}")
            else:
                test_results[category]['failed'] += 1
                print(f"  {resume_file.name:<40} {status}")
                test_results[category]['details'].append({
                    'file': resume_file.name,
                    'run1': features1,
                    'run2': features2
                })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    
    total_tested = 0
    total_passed = 0
    
    for category, results in test_results.items():
        total = results['total']
        passed = results['passed']
        pct = (passed / total * 100) if total > 0 else 0
        
        print(f"{category.upper():10} {passed:2}/{total:2} passed ({pct:5.1f}%)")
        
        total_tested += total
        total_passed += passed
    
    print("-" * 80)
    overall_pct = (total_passed / total_tested * 100) if total_tested > 0 else 0
    print(f"{'OVERALL':10} {total_passed:2}/{total_tested:2} passed ({overall_pct:5.1f}%)")
    
    print("\n" + "=" * 80)
    if total_passed == total_tested:
        print("✅ RESULT: All resumes are processed consistently!")
        print("✅ Feature extraction is 100% stable and deterministic.")
    else:
        print(f"❌ RESULT: {total_tested - total_passed} inconsistencies found!")
        for category, results in test_results.items():
            if results['details']:
                print(f"\n{category.upper()} failures:")
                for detail in results['details']:
                    print(f"  {detail['file']}")
    print("=" * 80)


if __name__ == "__main__":
    test_all_resumes_stability()
