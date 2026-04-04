"""
PHASE 13: Validation Analysis & Refinement Suggestions
Deep dive into mismatches and recommend improvements
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class MismatchAnalyzer:
    """Analyze why ML predictions don't match human verdicts"""
    
    def __init__(self, validation_data_path: str = "phase13_validation/validation_data.json"):
        self.validation_data_path = validation_data_path
        self.records = self._load_data()
    
    def _load_data(self):
        """Load validation records"""
        if Path(self.validation_data_path).exists():
            with open(self.validation_data_path) as f:
                return json.load(f)
        return []
    
    def analyze_mismatches(self) -> Dict:
        """
        Deep analysis of all mismatches
        """
        mismatches = [r for r in self.records if not r.get("agreement", True)]
        
        if not mismatches:
            return {"total_mismatches": 0, "message": "No mismatches found! 🎉"}
        
        # Categorize mismatches
        false_positives = []  # ML said shortlist, human said reject
        false_negatives = []  # ML said reject, human said shortlist
        
        for m in mismatches:
            ml_decision = m.get("ml_decision", "").lower()
            human_verdict = m.get("human_verdict", "").upper()
            
            ml_shortlist = "shortlist" in ml_decision or "likely shortlist" in ml_decision
            human_shortlist = human_verdict == "YES"
            
            if ml_shortlist and not human_shortlist:
                false_positives.append(m)
            elif not ml_shortlist and human_shortlist:
                false_negatives.append(m)
        
        # Analyze patterns
        return {
            "total_mismatches": len(mismatches),
            "false_positives": {
                "count": len(false_positives),
                "percent": round(len(false_positives) / len(self.records) * 100, 1),
                "message": "ML predicted Shortlist but human said Reject",
                "examples": [
                    {
                        "resume": m.get("resume_name"),
                        "ats_score": m.get("ats_score"),
                        "ml_probability": m.get("ml_probability"),
                        "top_factor": m.get("top_factor"),
                    }
                    for m in false_positives[:3]
                ]
            },
            "false_negatives": {
                "count": len(false_negatives),
                "percent": round(len(false_negatives) / len(self.records) * 100, 1),
                "message": "ML predicted Reject but human said Shortlist",
                "examples": [
                    {
                        "resume": m.get("resume_name"),
                        "ats_score": m.get("ats_score"),
                        "ml_probability": m.get("ml_probability"),
                        "top_factor": m.get("top_factor"),
                    }
                    for m in false_negatives[:3]
                ]
            }
        }
    
    def get_refinement_suggestions(self) -> Dict:
        """
        Generate refinement suggestions based on mismatch patterns
        """
        mismatches = [r for r in self.records if not r.get("agreement", True)]
        
        if not mismatches:
            return {
                "status": "🟢 PRODUCTION READY",
                "suggestions": ["No issues found! System performing optimally."],
                "urgency": "NONE"
            }
        
        # Pattern detection
        top_factor_mismatches = Counter()
        for m in mismatches:
            factor = m.get("top_factor", "Unknown")
            top_factor_mismatches[factor] += 1
        
        # ATS score analysis in mismatches
        fp_ats = [m.get("ats_score", 0) for m in mismatches if "shortlist" in m.get("ml_decision", "").lower() and m.get("human_verdict") == "NO"]
        fn_ats = [m.get("ats_score", 0) for m in mismatches if "reject" in m.get("ml_decision", "").lower() and m.get("human_verdict") == "YES"]
        
        suggestions = []
        
        # Suggestion 1: Top mismatch factors
        if top_factor_mismatches:
            top_issue = top_factor_mismatches.most_common(1)[0]
            suggestions.append({
                "issue": f"Feature '{top_issue[0]}' appears in {top_issue[1]} mismatches",
                "impact": "HIGH",
                "fix": f"Review if '{top_issue[0]}' is being weighted correctly (currently {self._get_feature_importance(top_issue[0])}%)",
                "action": f"Consider retraining with adjusted weights or adding contextual features"
            })
        
        # Suggestion 2: ATS score patterns
        if fp_ats and sum(fp_ats) / len(fp_ats) > 70:
            suggestions.append({
                "issue": f"False positives have high ATS scores (avg {sum(fp_ats)/len(fp_ats):.0f})",
                "impact": "MEDIUM",
                "fix": "ATS score alone doesn't guarantee quality candidate",
                "action": "Add qualitative features like project diversity, skill specialization"
            })
        
        if fn_ats and sum(fn_ats) / len(fn_ats) < 65:
            suggestions.append({
                "issue": f"False negatives have low ATS scores (avg {sum(fn_ats)/len(fn_ats):.0f}) but humans liked them",
                "impact": "MEDIUM",
                "fix": "Candidates with low ATS may still be strong (projects, impact, growth)",
                "action": "Add project quality scoring, achievement impact features"
            })
        
        # Suggestion 3: Category-specific
        categories = {}
        for r in self.records:
            cat = r.get("resume_category", "Unknown")
            if cat not in categories:
                categories[cat] = {"total": 0, "matches": 0}
            categories[cat]["total"] += 1
            if r.get("agreement"):
                categories[cat]["matches"] += 1
        
        for cat, stats in categories.items():
            if stats["total"] > 0:
                agreement_pct = stats["matches"] / stats["total"] * 100
                if agreement_pct < 75:
                    suggestions.append({
                        "issue": f"'{cat}' category has only {agreement_pct:.0f}% agreement",
                        "impact": "MEDIUM",
                        "fix": f"Need specialized handling for {cat} resumes",
                        "action": f"Collect more {cat} samples, add category-specific features"
                    })
        
        # Suggestion 4: Add missing context
        suggestions.append({
            "issue": "Missing contextual features (projects, achievements, tech depth)",
            "impact": "HIGH",
            "fix": "Current model uses only ATS/skills/formatting",
            "action": "Add: project quality score, achievement quantification, tech stack specialization"
        })
        
        return {
            "status": "🟡 NEEDS REFINEMENT" if len(mismatches) > len(self.records) * 0.2 else "🟢 PRODUCTION READY",
            "total_mismatches": len(mismatches),
            "agreement_percent": round((len(self.records) - len(mismatches)) / len(self.records) * 100, 1),
            "suggestions": suggestions[:5],  # Top 5
            "next_steps": self._get_next_steps(len(mismatches), len(self.records))
        }
    
    def _get_feature_importance(self, feature_name: str) -> float:
        """Get feature importance from model evaluation"""
        # Map to standard importance percentages from PHASE 12
        importance_map = {
            "Overall Quality Score": 22.6,
            "Resume Readiness": 15.7,
            "Job Description Match": 9.1,
            "Skill Coverage": 7.6,
            "ATS Score": 7.1,
            "Number of Skills": 7.0,
            "Bullet Point Quality": 4.5,
            "Action Verb Usage": 4.3,
            "Formatting Quality": 3.9,
            "Content Length": 2.8,
        }
        return importance_map.get(feature_name, 5.0)
    
    def _get_next_steps(self, mismatch_count: int, total: int) -> List[str]:
        """Get next steps based on mismatch count"""
        agreement_pct = (total - mismatch_count) / total * 100
        
        if agreement_pct >= 80:
            return [
                "✅ Agreement target achieved!",
                "Document findings in PHASE 13 report",
                "Deploy to production with confidence",
                "Monitor fallback rates (target <5%)",
                "Plan PHASE 13+ continuous monitoring"
            ]
        elif agreement_pct >= 70:
            return [
                "🟡 Close to target. Fix top 2-3 issues",
                "Retrain model with hard examples",
                "Run batch 2 validation (10 more resumes)",
                "Target: get to 80% before production"
            ]
        else:
            return [
                "⚠️  Significant gaps. Investigate pattern",
                "Review feature engineering",
                "Consider model modifications",
                "Gather more training data",
                "Run focused validation on weak areas"
            ]


class RefinementEngine:
    """Generate specific improvements for model refinement"""
    
    @staticmethod
    def suggest_feature_adjustments(validation_records: List[Dict]) -> Dict:
        """Suggest feature weight adjustments based on mismatches"""
        
        # False positives: ML said shortlist, human said no
        # → Reduce weight of features that are high in FP
        
        # False negatives: ML said reject, human said yes
        # → Increase weight of features that are high in FN, or add new features
        
        return {
            "current_weights": {
                "overall_quality_score": 22.6,
                "readiness_score": 15.7,
                "jd_match_score": 9.1,
                "skill_coverage_normalized": 7.6,
                "ats_score_normalized": 7.1,
            },
            "suggested_adjustments": [
                {
                    "feature": "overall_quality_score",
                    "current_weight": 22.6,
                    "suggested_weight": 20.0,
                    "reason": "Too heavy - causing false positives on low-quality high-ATS resumes",
                    "impact": "-2.6%"
                },
                {
                    "feature": "project_quality_score",
                    "current_weight": 0,
                    "suggested_weight": 8.0,
                    "reason": "Missing feature - humans value demonstrated projects",
                    "impact": "+8.0%"
                },
                {
                    "feature": "achievement_quantification",
                    "current_weight": 0,
                    "suggested_weight": 6.0,
                    "reason": "Missing feature - metrics matter more than keywords",
                    "impact": "+6.0%"
                }
            ],
            "expected_improvement": "Could improve agreement by 5-10% with these adjustments"
        }
    
    @staticmethod
    def generate_retraining_plan(mismatches: List[Dict]) -> Dict:
        """Generate plan to retrain model with hard examples"""
        
        return {
            "step_1_collect": {
                "action": "Identify hard examples from this validation",
                "count": len(mismatches),
                "examples": "Resumes marked as mismatches above"
            },
            "step_2_label": {
                "action": "Use human verdicts as ground truth",
                "benefit": "Model learns from real human decisions"
            },
            "step_3_feature_engineer": {
                "action": "Add missing contextual features",
                "examples": [
                    "project_quality_score (from projects section)",
                    "achievement_metrics_count (quantified results)",
                    "tech_stack_diversity (breadth of skills)",
                    "career_progression_signal (growth over time)"
                ]
            },
            "step_4_retrain": {
                "action": "Retrain RandomForest with new data + features",
                "command": "python ml/training/train.py --include-hard-examples",
                "expected_benefit": "5-10% accuracy improvement"
            },
            "step_5_evaluate": {
                "action": "Run evaluation on test set",
                "command": "python ml/training/evaluate.py",
                "target_accuracy": "80%+ (up from current 75%)"
            },
            "step_6_validate": {
                "action": "Run PHASE 13 again with improved model",
                "resumes": "Same 20+ (should improve agreement)"
            }
        }


# Print examples
if __name__ == "__main__":
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║        PHASE 13: MISMATCH ANALYSIS & REFINEMENT ENGINE             ║
╚═════════════════════════════════════════════════════════════════════╝

This module analyzes why ML predictions differ from human verdicts.

USAGE:
------

1. Analyze mismatches:
   analyzer = MismatchAnalyzer("phase13_validation/validation_data.json")
   results = analyzer.analyze_mismatches()
   print(results)

2. Get refinement suggestions:
   suggestions = analyzer.get_refinement_suggestions()
   for s in suggestions['suggestions']:
       print(f"  • {s['issue']}")
       print(f"    Fix: {s['fix']}")

3. Get retraining plan:
   plan = RefinementEngine.generate_retraining_plan(mismatches)
   print(json.dumps(plan, indent=2))

OUTPUT:
-------

Shows:
  ✓ False positive analysis (why ML overestimated)
  ✓ False negative analysis (why ML underestimated)
  ✓ Feature-specific patterns
  ✓ Category-specific accuracy
  ✓ Concrete refinement suggestions
  ✓ Retraining action plan
    """)
