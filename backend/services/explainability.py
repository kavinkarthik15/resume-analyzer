"""
STEP 2: Explainability Layer
Add detailed explanations for scores and predictions
"""

from typing import Dict, List, Any, Tuple


class ScoreExplanation:
    """Detailed explanation of a score component"""

    def __init__(self, component: str, score: int, max_score: int, reason: str, impact: str):
        self.component = component
        self.score = score
        self.max_score = max_score
        self.reason = reason
        self.impact = impact
        self.suggestions = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round(self.score / self.max_score * 100, 1) if self.max_score > 0 else 0,
            "reason": self.reason,
            "impact": self.impact,
            "suggestions": self.suggestions,
        }


class ExplainableATSScore:
    """ATS Score with detailed explanations"""

    def __init__(self):
        self.total_score = 0
        self.explanations: List[ScoreExplanation] = []
        self.overall_feedback = ""
        self.priority_improvements: List[str] = []

    def add_explanation(self, explanation: ScoreExplanation):
        """Add a component explanation"""
        self.explanations.append(explanation)

    def calculate_total(self):
        """Calculate total score from explanations"""
        self.total_score = sum(exp.score for exp in self.explanations)

        # Generate overall feedback
        self._generate_overall_feedback()

        # Generate priority improvements
        self._generate_priority_improvements()

    def _generate_overall_feedback(self):
        """Generate overall feedback based on scores"""
        low_components = [exp for exp in self.explanations if exp.score < exp.max_score * 0.6]

        if self.total_score >= 80:
            self.overall_feedback = "Excellent resume! Your ATS score indicates strong optimization for applicant tracking systems."
        elif self.total_score >= 60:
            self.overall_feedback = "Good foundation. Your resume passes most ATS filters but has room for improvement."
        elif self.total_score >= 40:
            self.overall_feedback = "Moderate performance. Significant improvements needed to reliably pass ATS screening."
        else:
            self.overall_feedback = "Low ATS compatibility. Major revisions required to improve system compatibility."

        if low_components:
            self.overall_feedback += f" Focus on improving: {', '.join([c.component for c in low_components])}."

    def _generate_priority_improvements(self):
        """Generate priority improvement suggestions"""
        improvements = []

        for exp in self.explanations:
            if exp.score < exp.max_score * 0.7:  # Below 70%
                improvements.extend(exp.suggestions)

        # Sort by impact (simple heuristic: more missing points = higher priority)
        self.priority_improvements = improvements[:5]  # Top 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "overall_feedback": self.overall_feedback,
            "priority_improvements": self.priority_improvements,
            "component_explanations": [exp.to_dict() for exp in self.explanations],
        }


def explain_keyword_match(skills_found: List[str], skill_frequency: Dict[str, int],
                         resume_text: str) -> ScoreExplanation:
    """Explain keyword match component"""

    total_skills = len(skills_found)
    total_occurrences = sum(skill_frequency.values())

    # Calculate score (30 points max)
    skill_score = min(total_skills * 2, 20)  # 20 points for skills
    frequency_score = min(total_occurrences, 10)  # 10 points for frequency
    score = skill_score + frequency_score

    # Generate reason
    if total_skills == 0:
        reason = "No technical skills detected in resume"
        impact = "Critical - ATS systems prioritize resumes with relevant skills"
        suggestions = [
            "Add a dedicated Skills section with technical competencies",
            "Include 8-12 relevant skills for your target role",
            "Use exact skill names as they appear in job descriptions"
        ]
    elif total_skills < 5:
        reason = f"Only {total_skills} skills found - below typical requirement"
        impact = f"Lost {20 - skill_score} points due to insufficient skills"
        suggestions = [
            "Add more technical skills relevant to your target role",
            "Include both hard skills (Python, SQL) and soft skills (Leadership, Communication)",
            "Review job descriptions to identify missing key skills"
        ]
    elif total_occurrences < 5:
        reason = f"Skills present but infrequently mentioned ({total_occurrences} total occurrences)"
        impact = f"Lost {10 - frequency_score} points due to low keyword frequency"
        suggestions = [
            "Repeat key skills naturally throughout resume sections",
            "Use skills in context (e.g., 'Developed Python applications')",
            "Include skills in Summary, Experience, and Projects sections"
        ]
    else:
        reason = f"Good skill coverage with {total_skills} skills and {total_occurrences} keyword occurrences"
        impact = "Strong foundation for ATS keyword matching"
        suggestions = [
            "Continue emphasizing most relevant skills for target roles",
            "Consider adding emerging technologies in your field"
        ]

    explanation = ScoreExplanation(
        component="Keyword Match",
        score=score,
        max_score=30,
        reason=reason,
        impact=impact
    )
    explanation.suggestions = suggestions

    return explanation


def explain_section_completeness(sections_detected: Dict[str, bool]) -> ScoreExplanation:
    """Explain section completeness component"""

    important_sections = ["Skills", "Experience", "Education"]
    essential_found = sum(1 for s in important_sections if sections_detected.get(s, False))
    total_sections = len(sections_detected)
    found_sections = sum(sections_detected.values())

    # Calculate score (20 points max)
    essential_score = essential_found * 6  # 18 points max for essentials
    other_score = min((found_sections - essential_found) * 1, 2)  # 2 points for others
    score = essential_score + other_score

    # Generate reason
    missing_essential = [s for s in important_sections if not sections_detected.get(s, False)]
    missing_other = [s for s, found in sections_detected.items() if not found and s not in important_sections]

    if missing_essential:
        reason = f"Missing essential sections: {', '.join(missing_essential)}"
        impact = f"Critical gaps - lost {18 - essential_score} points for missing core sections"
        suggestions = [
            f"Add {missing_essential[0]} section with relevant details",
            "Include all three essential sections: Skills, Experience, Education",
            "Use clear section headers that ATS can recognize"
        ]
    elif found_sections < 5:
        reason = f"Limited section coverage ({found_sections}/{total_sections} sections found)"
        impact = f"Lost {20 - score} points due to incomplete resume structure"
        suggestions = [
            "Add more sections like Projects, Certifications, or Awards",
            "Ensure comprehensive coverage of your professional background",
            "Use standard section names that ATS systems expect"
        ]
    else:
        reason = f"Comprehensive section coverage ({found_sections} sections detected)"
        impact = "Strong structural foundation for ATS parsing"
        suggestions = [
            "Maintain clear section organization",
            "Consider adding relevant optional sections if space allows"
        ]

    explanation = ScoreExplanation(
        component="Section Completeness",
        score=score,
        max_score=20,
        reason=reason,
        impact=impact
    )
    explanation.suggestions = suggestions

    return explanation


def explain_formatting_quality(resume_text: str, formatting_issues: List[str]) -> ScoreExplanation:
    """Explain formatting quality component"""

    # Analyze formatting issues
    word_count = len(resume_text.split())
    has_bullets = '•' in resume_text or '-' in resume_text
    clean_formatting = not any(char in resume_text for char in ['█', '▓', '░', '▌'])

    # Calculate score (20 points max)
    score = 20

    if not has_bullets:
        score -= 5

    if word_count < 200:
        score -= 5
    elif word_count > 1000:
        score -= 3

    if formatting_issues:
        score -= min(len(formatting_issues) * 2, 7)  # Up to 7 points for issues

    score = max(score, 0)

    # Generate reason
    issues_desc = []
    if not has_bullets:
        issues_desc.append("no bullet points")
    if word_count < 200:
        issues_desc.append("too short")
    elif word_count > 1000:
        issues_desc.append("too long")
    if formatting_issues:
        issues_desc.extend(formatting_issues[:2])

    if issues_desc:
        reason = f"Formatting issues detected: {', '.join(issues_desc)}"
        impact = f"Lost {20 - score} points affecting ATS readability"
        suggestions = [
            "Use standard bullet points (• or -) for lists",
            "Keep resume length between 250-750 words",
            "Avoid complex formatting, tables, or graphics",
            "Use simple fonts and clear section headers"
        ]
    else:
        reason = "Clean, ATS-friendly formatting with appropriate length and structure"
        impact = "Optimal formatting for ATS parsing and readability"
        suggestions = [
            "Maintain consistent formatting throughout",
            "Regularly test resume with different ATS systems"
        ]

    explanation = ScoreExplanation(
        component="Formatting Quality",
        score=score,
        max_score=20,
        reason=reason,
        impact=impact
    )
    explanation.suggestions = suggestions

    return explanation


def explain_experience_relevance(resume_text: str, breakdown: Dict[str, int]) -> ScoreExplanation:
    """Explain experience relevance component"""

    experience_score = breakdown.get("experience", 0)

    # Analyze content for action verbs and metrics
    action_verbs = ["achieved", "built", "created", "developed", "directed",
                   "implemented", "improved", "increased", "led", "managed"]
    verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())

    # Look for quantifiable results
    has_metrics = bool(re.search(r'\d+%|\$[\d,]+|\d+x|increased.*by|reduced.*by', resume_text))

    # Calculate score (30 points max)
    verb_score = min(verb_count * 1.5, 15)
    metric_score = 10 if has_metrics else 5
    score = verb_score + metric_score

    # Generate reason
    if verb_count < 3:
        reason = f"Low action verb usage ({verb_count} detected) - resume reads passively"
        impact = f"Lost {15 - verb_score} points for weak action language"
        suggestions = [
            "Replace passive phrases with strong action verbs",
            "Start each bullet with verbs like 'Achieved', 'Built', 'Created'",
            "Use dynamic language that shows initiative and results"
        ]
    elif not has_metrics:
        reason = "Good action verbs but missing quantifiable achievements"
        impact = f"Lost {5} points for lack of measurable results"
        suggestions = [
            "Add specific numbers, percentages, or dollar amounts",
            "Quantify impact: 'Increased sales by 40%' instead of 'Improved sales'",
            "Include metrics for all major achievements"
        ]
    else:
        reason = f"Strong experience section with {verb_count} action verbs and quantifiable results"
        impact = "Excellent experience presentation that demonstrates impact"
        suggestions = [
            "Continue quantifying achievements where possible",
            "Focus on results and impact in future roles"
        ]

    explanation = ScoreExplanation(
        component="Experience Relevance",
        score=score,
        max_score=30,
        reason=reason,
        impact=impact
    )
    explanation.suggestions = suggestions

    return explanation


def create_explainable_ats_score(resume_text: str, skills_found: List[str],
                               skill_frequency: Dict[str, int],
                               sections_detected: Dict[str, bool],
                               formatting_issues: List[str] = None,
                               breakdown: Dict[str, int] = None) -> ExplainableATSScore:
    """
    STEP 2 MAIN FUNCTION
    Create ATS score with detailed explanations
    """

    if formatting_issues is None:
        formatting_issues = []

    if breakdown is None:
        breakdown = {}

    explainable_score = ExplainableATSScore()

    # Add component explanations
    explainable_score.add_explanation(
        explain_keyword_match(skills_found, skill_frequency, resume_text)
    )

    explainable_score.add_explanation(
        explain_section_completeness(sections_detected)
    )

    explainable_score.add_explanation(
        explain_formatting_quality(resume_text, formatting_issues)
    )

    explainable_score.add_explanation(
        explain_experience_relevance(resume_text, breakdown)
    )

    # Calculate total and generate feedback
    explainable_score.calculate_total()

    return explainable_score


def explain_ml_prediction(prediction_result: Dict[str, Any],
                         analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Explain ML prediction with feature importance
    """

    probability = prediction_result.get("probability", 0)
    decision = prediction_result.get("decision", "Unknown")

    # Get key factors
    ats_score = analysis_data.get("ats_score", 0)
    skills_count = len(analysis_data.get("skills_found", []))
    sections_found = sum(analysis_data.get("sections_detected", {}).values())

    # Generate explanation
    if probability > 0.75:
        confidence_reason = "Strong combination of high ATS score, comprehensive skills, and complete resume structure"
    elif probability > 0.6:
        confidence_reason = "Good foundation with room for minor improvements"
    elif probability > 0.4:
        confidence_reason = "Moderate resume quality - several areas need attention"
    else:
        confidence_reason = "Significant gaps in resume quality and ATS optimization"

    # Key influencing factors
    factors = []
    if ats_score >= 70:
        factors.append("High ATS score indicates good system compatibility")
    elif ats_score < 50:
        factors.append("Low ATS score suggests parsing and keyword issues")

    if skills_count >= 8:
        factors.append("Strong skill coverage across multiple technologies")
    elif skills_count < 5:
        factors.append("Limited technical skills listed")

    if sections_found >= 4:
        factors.append("Comprehensive resume structure")
    else:
        factors.append("Missing important resume sections")

    return {
        "probability": probability,
        "decision": decision,
        "confidence_explanation": confidence_reason,
        "key_factors": factors,
        "prediction_reasoning": prediction_result.get("reasoning", []),
        "improvement_focus": "Focus on ATS score and skill coverage" if probability < 0.6 else "Refine resume structure and content",
    }