"""
PHASE 10: Database Integration
SQLite persistence layer
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


DATABASE_PATH = Path(__file__).parent.parent.parent / "resume_analyzer.db"


class Database:
    """SQLite Database manager for Resume Analyzer"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.initialize()
    
    def initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_text TEXT,
                parsed_data JSON,
                UNIQUE(filename, upload_date)
            )
        """)
        
        # Analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ats_score INTEGER,
                breakdown JSON,
                skills JSON,
                sections_detected JSON,
                missing_skills JSON,
                formatting_issues JSON,
                suggestions JSON,
                jd_comparison JSON,
                ml_prediction JSON,
                FOREIGN KEY(resume_id) REFERENCES resumes(id)
            )
        """)
        
        # Progress tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                analysis_id INTEGER NOT NULL,
                previous_score INTEGER,
                current_score INTEGER,
                improvement INTEGER,
                new_skills JSON,
                tracked_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(resume_id) REFERENCES resumes(id),
                FOREIGN KEY(analysis_id) REFERENCES analysis(id)
            )
        """)
        
        # JD comparison history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jd_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                jd_text TEXT,
                match_score INTEGER,
                matched_skills JSON,
                missing_skills JSON,
                comparison_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(resume_id) REFERENCES resumes(id)
            )
        """)
        
        self.conn.commit()
    
    def save_resume(self, filename: str, raw_text: str, parsed_data: dict,
                   file_path: Optional[str] = None) -> int:
        """
        Save or update resume to database
        
        Returns:
            resume_id
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO resumes (filename, file_path, raw_text, parsed_data, upload_date)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, file_path, raw_text, json.dumps(parsed_data), datetime.now()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_resume(self, resume_id: int) -> Optional[dict]:
        """Get resume by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def save_analysis(self, resume_id: int, analysis_data: dict) -> int:
        """
        Save analysis to database
        
        Returns:
            analysis_id
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis (
                resume_id, ats_score, breakdown, skills, sections_detected,
                missing_skills, formatting_issues, suggestions, jd_comparison, ml_prediction
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get("ats_score"),
            json.dumps(analysis_data.get("breakdown", {})),
            json.dumps(analysis_data.get("skills", [])),
            json.dumps(analysis_data.get("sections_detected", {})),
            json.dumps(analysis_data.get("missing_skills", {})),
            json.dumps(analysis_data.get("formatting_issues", [])),
            json.dumps(analysis_data.get("suggestions", [])),
            json.dumps(analysis_data.get("jd_comparison", {})) if analysis_data.get("jd_comparison") else None,
            json.dumps(analysis_data.get("ml_prediction", {})) if analysis_data.get("ml_prediction") else None,
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_analysis(self, analysis_id: int) -> Optional[dict]:
        """Get analysis by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM analysis WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            # Parse JSON fields
            for json_field in ["breakdown", "skills", "sections_detected", "missing_skills", 
                             "formatting_issues", "suggestions", "jd_comparison", "ml_prediction"]:
                if result.get(json_field):
                    try:
                        result[json_field] = json.loads(result[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            return result
        return None
    
    def get_resume_history(self, resume_id: int, limit: int = 10) -> List[dict]:
        """Get analysis history for a resume"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis WHERE resume_id = ?
            ORDER BY analysis_date DESC LIMIT ?
        """, (resume_id, limit))
        
        results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            # Parse JSON fields
            for json_field in ["breakdown", "skills", "sections_detected", "missing_skills"]:
                if analysis.get(json_field):
                    try:
                        analysis[json_field] = json.loads(analysis[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            results.append(analysis)
        
        return results
    
    def save_progress(self, resume_id: int, analysis_id: int, previous_score: int,
                     current_score: int, new_skills: List[str]) -> int:
        """Save progress tracking data"""
        cursor = self.conn.cursor()
        
        improvement = current_score - previous_score if previous_score >= 0 else None
        
        cursor.execute("""
            INSERT INTO progress_tracking (resume_id, analysis_id, previous_score, current_score, improvement, new_skills)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (resume_id, analysis_id, previous_score, current_score, improvement, json.dumps(new_skills)))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_progress(self, resume_id: int) -> Optional[dict]:
        """Get latest progress for resume"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM progress_tracking WHERE resume_id = ?
            ORDER BY tracked_date DESC LIMIT 1
        """, (resume_id,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get("new_skills"):
                try:
                    result["new_skills"] = json.loads(result["new_skills"])
                except (json.JSONDecodeError, TypeError):
                    pass
            return result
        return None
    
    def save_jd_comparison(self, resume_id: int, jd_text: str,
                          comparison_data: dict) -> int:
        """Save JD comparison results"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO jd_comparisons (resume_id, jd_text, match_score, matched_skills, missing_skills)
            VALUES (?, ?, ?, ?, ?)
        """, (
            resume_id,
            jd_text,
            comparison_data.get("jd_match_score"),
            json.dumps(comparison_data.get("matched_skills", [])),
            json.dumps(comparison_data.get("missing_skills", [])),
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_statistics(self, resume_id: int) -> dict:
        """Get statistics for a resume"""
        cursor = self.conn.cursor()
        
        # Total analyses
        cursor.execute("SELECT COUNT(*) as count FROM analysis WHERE resume_id = ?", (resume_id,))
        analysis_count = cursor.fetchone()["count"]
        
        # Scores
        cursor.execute("""
            SELECT AVG(ats_score) as avg_score, MAX(ats_score) as max_score, MIN(ats_score) as min_score
            FROM analysis WHERE resume_id = ?
        """, (resume_id,))
        scores = cursor.fetchone()
        
        return {
            "total_analyses": analysis_count,
            "average_score": round(scores["avg_score"]) if scores["avg_score"] else 0,
            "highest_score": scores["max_score"] or 0,
            "lowest_score": scores["min_score"] or 0,
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global database instance
db = Database()