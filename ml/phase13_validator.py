"""
PHASE 13: Resume Validation Collector
Efficiently collect ML predictions + human verdicts for testing
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationRecord:
    """Single validation result for a resume"""
    resume_id: str
    resume_name: str
    
    # Automated metrics
    ats_score: float
    ml_decision: str
    ml_probability: float
    ml_confidence: str
    top_factor: str  # Most important factor
    top_factor_importance: float
    
    # Human verdict
    human_verdict: str  # "YES" or "NO"
    human_reviewer: str  # Name of recruiter/reviewer
    
    # Comparison
    agreement: bool  # True if ML and human match
    prediction_time_ms: float
    
    # Notes
    mismatch_reason: str = ""  # If agreement=False, why they differ
    resume_category: str = ""  # "Strong" / "Average" / "Weak"
    notes: str = ""
    
    # Metadata
    validation_date: str = ""
    

class ValidationCollector:
    """PHASE 13: Collect and track validation data"""
    
    def __init__(self, output_dir: str = "phase13_validation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.records: List[ValidationRecord] = []
        self.csv_path = self.output_dir / "validation_results.csv"
        self.json_path = self.output_dir / "validation_data.json"
        self.metrics_path = self.output_dir / "validation_metrics.json"
        
        # Load existing records if they exist
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing validation records"""
        if self.csv_path.exists():
            import pandas as pd
            df = pd.read_csv(self.csv_path)
            # Convert back to records (simplified)
            print(f"📂 Loaded {len(df)} existing validation records")
    
    def add_record(self, record: ValidationRecord) -> None:
        """Add a validation record"""
        record.validation_date = datetime.now().isoformat()
        self.records.append(record)
        print(f"✅ Added: {record.resume_name} (Match: {'✅' if record.agreement else '❌'})")
    
    def collect_from_resume(
        self,
        resume_path: str,
        ml_result: Dict,
        human_verdict: str,
        reviewer_name: str,
        resume_category: str = "Unknown"
    ) -> ValidationRecord:
        """
        Create validation record from resume analysis
        
        Args:
            resume_path: Path to resume file
            ml_result: Output from analyzer.analyze_resume_complete()
            human_verdict: "YES" or "NO" (would you shortlist?)
            reviewer_name: Name of person giving verdict
            resume_category: "Strong" / "Average" / "Weak"
        """
        ml_pred = ml_result.get("ml_prediction", {})
        
        # Extract top factor
        top_factors = ml_pred.get("top_factors", [])
        top_factor = top_factors[0]["factor"] if top_factors else "Unknown"
        top_importance = top_factors[0]["importance"] if top_factors else 0
        
        # Determine agreement
        ml_decision = ml_pred.get("decision", "Unknown")
        ml_shortlist = "shortlist" in ml_decision.lower()
        human_shortlist = human_verdict.upper() == "YES"
        agreement = ml_shortlist == human_shortlist
        
        record = ValidationRecord(
            resume_id=Path(resume_path).stem,
            resume_name=Path(resume_path).name,
            
            ats_score=ml_result.get("ats_analysis", {}).get("score", 0),
            ml_decision=ml_decision,
            ml_probability=ml_pred.get("probability", 0),
            ml_confidence=ml_pred.get("confidence", "Unknown"),
            top_factor=top_factor,
            top_factor_importance=top_importance,
            
            human_verdict=human_verdict.upper(),
            human_reviewer=reviewer_name,
            
            agreement=agreement,
            prediction_time_ms=ml_pred.get("prediction_duration_ms", 0),
            
            resume_category=resume_category,
        )
        
        self.add_record(record)
        return record
    
    def save_results(self) -> Dict[str, str]:
        """Save all collected data to CSV and JSON"""
        if not self.records:
            print("⚠️  No validation records to save")
            return {}
        
        # Save as CSV
        csv_data = [asdict(r) for r in self.records]
        import pandas as pd
        df = pd.DataFrame(csv_data)
        df.to_csv(self.csv_path, index=False)
        print(f"💾 Saved {len(self.records)} records to {self.csv_path}")
        
        # Save as JSON
        with open(self.json_path, 'w') as f:
            json.dump([asdict(r) for r in self.records], f, indent=2)
        print(f"💾 Saved to {self.json_path}")
        
        # Calculate and save metrics
        metrics = self.calculate_metrics()
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"📊 Saved metrics to {self.metrics_path}")
        
        return {
            "csv": str(self.csv_path),
            "json": str(self.json_path),
            "metrics": str(self.metrics_path),
        }
    
    def calculate_metrics(self) -> Dict:
        """Calculate validation metrics"""
        if not self.records:
            return {"total": 0}
        
        total = len(self.records)
        matches = sum(1 for r in self.records if r.agreement)
        
        # By category
        strong = [r for r in self.records if r.resume_category == "Strong"]
        average = [r for r in self.records if r.resume_category == "Average"]
        weak = [r for r in self.records if r.resume_category == "Weak"]
        
        strong_agreement = sum(1 for r in strong if r.agreement) / len(strong) * 100 if strong else 0
        avg_agreement = sum(1 for r in average if r.agreement) / len(average) * 100 if average else 0
        weak_agreement = sum(1 for r in weak if r.agreement) / len(weak) * 100 if weak else 0
        
        # Top mismatches
        mismatches = [r for r in self.records if not r.agreement]
        false_positives = [r for r in mismatches if r.ml_decision.lower().find("shortlist") >= 0]
        false_negatives = [r for r in mismatches if r.ml_decision.lower().find("reject") >= 0]
        
        return {
            "total_validations": total,
            "agreements": matches,
            "mismatches": len(mismatches),
            "overall_agreement_percent": round(matches / total * 100, 1),
            "by_category": {
                "Strong": {
                    "total": len(strong),
                    "agreement_percent": round(strong_agreement, 1)
                },
                "Average": {
                    "total": len(average),
                    "agreement_percent": round(avg_agreement, 1)
                },
                "Weak": {
                    "total": len(weak),
                    "agreement_percent": round(weak_agreement, 1)
                }
            },
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "status": "READY_FOR_PRODUCTION" if matches / total >= 0.80 else "NEEDS_REFINEMENT",
        }


class ValidationWorkflow:
    """PHASE 13: Step-by-step validation workflow"""
    
    @staticmethod
    def print_steps():
        """Print enrollment workflow"""
        workflow = """
╔═════════════════════════════════════════════════════════════════════╗
║           PHASE 13: VALIDATION WORKFLOW (20+ Resumes)              ║
╚═════════════════════════════════════════════════════════════════════╝

STEP 1️⃣  COLLECT RESUMES (Minimum 20)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mix:
  • Strong resumes (80+ ATS, likely shortlist)
  • Average resumes (60-80 ATS, borderline)
  • Weak resumes (<60 ATS, clear reject)

Sources:
  • Friends / classmates
  • LinkedIn (convert to PDF/TXT)
  • Resume databases online

Place in: ./phase13_resumes/


STEP 2️⃣  RUN AUTOMATED ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each resume:

  python phase13_validator.py \\
    --resume path/to/resume.pdf \\
    --reviewer "Your Name" \\
    --category "Strong|Average|Weak"

Gets:
  ✓ ATS Score
  ✓ ML Decision (Shortlist/Reject/Uncertain)
  ✓ Confidence level
  ✓ Top 5 factors


STEP 3️⃣  GATHER HUMAN VERDICTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each resume, ask recruiting expert:

  "Would you shortlist this candidate?"
  
Answer: YES / NO

(Script will prompt for verdict after showing ML result)


STEP 4️⃣  BUILD VALIDATION TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CSV automatically created:

Resume | ATS | ML Decision | ML Prob | Human | Match
─────────────────────────────────────────────────────
R1     | 78  | Shortlist   | 0.81    | YES   | ✅
R2     | 65  | Uncertain   | 0.58    | NO    | ✅
R3     | 52  | Reject      | 0.35    | NO    | ✅
R4     | 72  | Shortlist   | 0.72    | NO    | ❌ (FP)


STEP 5️⃣  CALCULATE AGREEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Results auto-generated:

  Total Validations: 20
  Agreements: 18/20 = 🎯 90%
  
  By Category:
    Strong (5): 5/5 = 100% ✅
    Average (8): 6/8 = 75% ⚠️
    Weak (7): 7/7 = 100% ✅


STEP 6️⃣  ANALYZE FAILURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each mismatch:

  python phase13_analyzer.py analyze-mismatches

Shows:

  False Positive (ML said YES, human said NO):
    • Missing context in JD match
    • Over-reliance on ATS score
    
  False Negative (ML said NO, human said YES):
    • Missing project quality signal
    • Weak skill matching


STEP 7️⃣  GET REFINEMENT SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Auto-generated improvement list:

  python phase13_analyzer.py refinements

Output:

  Top Issues Found:
    1. Missing project context (affects 2 mismatches)
    2. Course/certification quality blind spot
    3. Over-weight JD match penalty
  
  Suggestions:
    → Add project quality feature
    → Add certifications feature
    → Reduce jd_match_score weight from 9.1% to 6%


STEP 8️⃣  DECLARE PRODUCTION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When:
  ✅ Agreement ≥ 80%
  ✅ No category < 70% (except maybe 1)
  ✅ Mismatches understood & documented

Result: 🟢 PRODUCTION READY


═══════════════════════════════════════════════════════════════════════
        """
        print(workflow)


if __name__ == "__main__":
    ValidationWorkflow.print_steps()
