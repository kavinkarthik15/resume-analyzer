"""
PHASE 9: Progress Tracking System
Show user improvement over time
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class AnalysisSnapshot:
    """Single point in time analysis"""
    
    def __init__(self, ats_score: int, skills: List[str], timestamp: Optional[datetime] = None):
        self.timestamp = timestamp or datetime.now()
        self.ats_score = ats_score
        self.skills = skills
        self.skill_count = len(skills)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "ats_score": self.ats_score,
            "skill_count": self.skill_count,
            "skills": self.skills,
        }


class ProgressReport:
    """Comparison between two snapshots"""
    
    def __init__(self, previous: Optional[AnalysisSnapshot] = None,
                 current: AnalysisSnapshot = None):
        self.previous = previous
        self.current = current
        self.score_improvement = 0
        self.new_skills = []
        self.improved_sections = []
        
        if previous and current:
            self._calculate_improvement()
    
    def _calculate_improvement(self):
        """Calculate improvement metrics"""
        # ATS score improvement
        self.score_improvement = self.current.ats_score - self.previous.ats_score
        
        # New skills added
        previous_skills_set = set(self.previous.skills)
        current_skills_set = set(self.current.skills)
        self.new_skills = list(current_skills_set - previous_skills_set)
    
    def to_dict(self) -> dict:
        return {
            "previous_score": self.previous.ats_score if self.previous else None,
            "current_score": self.current.ats_score if self.current else 0,
            "improvement": self.score_improvement,
            "improvement_percentage": round((self.score_improvement / max(self.previous.ats_score, 1)) * 100, 1) if self.previous else 0,
            "new_skills": self.new_skills,
            "new_skills_count": len(self.new_skills),
            "total_skills_now": self.current.skill_count if self.current else 0,
        }
    
    def get_insights(self) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        if not self.previous:
            insights.append(f"📊 First analysis: ATS score {self.current.ats_score}/100")
            insights.append(f"🎯 Starting with {self.current.skill_count} identified skills")
            return insights
        
        # Score improvement
        if self.score_improvement > 0:
            insights.append(f"✅ ATS Score improved by +{self.score_improvement} points ({round((self.score_improvement/self.previous.ats_score)*100, 1)}%)")
        elif self.score_improvement < 0:
            insights.append(f"⚠️ ATS Score decreased by {self.score_improvement} points")
        else:
            insights.append(f"→ ATS Score unchanged at {self.current.ats_score}/100")
        
        # Skills
        if self.new_skills:
            insights.append(f"🆕 Added {len(self.new_skills)} new skills: {', '.join(self.new_skills[:3])}")
        
        if self.current.skill_count > self.previous.skill_count:
            added = self.current.skill_count - self.previous.skill_count
            insights.append(f"📈 Total skills increased from {self.previous.skill_count} to {self.current.skill_count}")
        
        # Overall sentiment
        if self.score_improvement >= 10:
            insights.append("🚀 Great progress! Keep working on the remaining sections.")
        elif self.score_improvement > 0:
            insights.append("👍 Solid improvement. Continue refining your resume.")
        elif self.score_improvement == 0 and self.new_skills:
            insights.append("📝 Added new skills while maintaining baseline quality.")
        
        return insights


class ProgressTracker:
    """
    PHASE 9 MAIN CLASS
    Track resume analysis improvements over time
    """
    
    def __init__(self):
        self.snapshots: List[AnalysisSnapshot] = []
        self.analysis_count = 0
    
    def record_analysis(self, ats_score: int, skills: List[str]) -> str:
        """
        Record a new analysis snapshot
        
        Args:
            ats_score: ATS score from analysis
            skills: List of detected skills
            
        Returns:
            snapshot_id (timestamp string)
        """
        snapshot = AnalysisSnapshot(ats_score, skills)
        self.snapshots.append(snapshot)
        self.analysis_count += 1
        
        return snapshot.timestamp.isoformat()
    
    def get_latest_analysis(self) -> Optional[AnalysisSnapshot]:
        """Get most recent analysis"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_previous_analysis(self) -> Optional[AnalysisSnapshot]:
        """Get second most recent analysis"""
        return self.snapshots[-2] if len(self.snapshots) >= 2 else None
    
    def get_progress_report(self) -> ProgressReport:
        """
        MAIN PROGRESS TRACKING FUNCTION
        Generate progress report comparing previous and current analysis
        """
        current = self.get_latest_analysis()
        previous = self.get_previous_analysis()
        
        if not current:
            raise ValueError("No analysis data available")
        
        report = ProgressReport(previous, current)
        return report
    
    def get_timeline(self, limit: int = 10) -> List[dict]:
        """Get analysis timeline (last N analyses)"""
        recent = self.snapshots[-limit:]
        return [s.to_dict() for s in recent]
    
    def get_statistics(self) -> dict:
        """Get overall statistics across all analyses"""
        if not self.snapshots:
            return {
                "total_analyses": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "total_unique_skills": 0,
            }
        
        scores = [s.ats_score for s in self.snapshots]
        all_skills = set()
        for s in self.snapshots:
            all_skills.update(s.skills)
        
        return {
            "total_analyses": len(self.snapshots),
            "average_score": round(sum(scores) / len(scores), 1),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "score_trend": "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable",
            "total_unique_skills": len(all_skills),
            "first_analysis": self.snapshots[0].timestamp.isoformat(),
            "last_analysis": self.snapshots[-1].timestamp.isoformat(),
        }
    
    def get_improvement_metrics(self) -> dict:
        """Get detailed improvement metrics"""
        if len(self.snapshots) < 2:
            return {
                "analyses_count": self.analysis_count,
                "status": "insufficient_data",
                "message": "Need at least 2 analyses for comparison",
            }
        
        report = self.get_progress_report()
        
        return {
            "analyses_count": self.analysis_count,
            "status": "calculated",
            "metrics": report.to_dict(),
            "insights": report.get_insights(),
            "recommendations": self._get_recommendations(report),
        }
    
    def _get_recommendations(self, report: ProgressReport) -> List[str]:
        """Generate recommendations based on progress"""
        recommendations = []
        
        if report.score_improvement < 5 and report.current.ats_score < 75:
            recommendations.append("⚡ Focus on adding more relevant keywords to boost ATS score")
        
        if not report.new_skills:
            recommendations.append("📚 Work on learning and documenting new skills")
        
        if report.current.skill_count < 8:
            recommendations.append("🎯 Aim for at least 8-10 technical skills")
        
        if report.current.ats_score >= 75:
            recommendations.append("✨ Excellent! Prepare for interviews and start applying")
        
        if report.score_improvement > 0 and report.score_improvement < 5:
            recommendations.append("🚀 You're on the right track! Keep iterating and improving")
        
        return recommendations


# In-memory storage for demo purposes
# In production, this would use a database
progress_trackers: Dict[str, ProgressTracker] = {}