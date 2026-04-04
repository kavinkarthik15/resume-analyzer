"""
PHASE 8: Context-Aware Chat Assistant
Turn chatbot into career assistant using resume analysis context
"""

import re
from typing import Optional, List, Dict, Any


# Templates for common improvements
BULLET_IMPROVEMENT_TEMPLATES = {
    "weak_action_verb": "❌ {original}\n✅ Replace '{verb}' with stronger action: {suggestions}",
    "missing_metrics": "❌ {original}\n✅ Add measurement: {suggestion}",
    "missing_impact": "❌ {original}\n✅ Show impact: {suggestion}",
}

SKILL_SUGGESTION_TEMPLATES = {
    "trending": "Consider learning {skill} - it's trending strongly in {role} roles",
    "complementary": "{skill} pairs well with your {existing_skill} skillset",
    "gap_filler": "Adding {skill} would close a gap in your technical portfolio",
}

PROMPT_TEMPLATES = {
    "improve_bullet": "Improve this resume bullet point: '{bullet}'",
    "suggest_skills": "What skills should I focus on for a {role} position?",
    "resume_feedback": "Give me specific feedback on my resume for {target_role}",
    "ats_improvement": "How can I improve my ATS score of {score}?",
    "interview_prep": "I have an interview for a {role} role. How should I prepare?",
}


class ChatResponse:
    """Structured chat response"""
    
    def __init__(self):
        self.answer: str = ""
        self.tips: List[str] = []
        self.action_items: List[str] = []
        self.resources: List[Dict[str, str]] = []
        
    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "tips": self.tips,
            "action_items": self.action_items,
            "resources": self.resources,
        }


def _identify_intent(question: str) -> str:
    """Identify the intent of user's question"""
    question_lower = question.lower()
    
    intent_patterns = {
        "improve_bullet": r"improve|better|rewrite|enhance.*bullet",
        "suggest_skills": r"what.*skill|missing.*skill|learn|recommend.*skill",
        "ats_feedback": r"ats|score|improve.*score|why.*low",
        "jd_match": r"match|jd|job.*description|alignment",
        "resume_feedback": r"feedback|review|evaluation|assess",
        "interview_prep": r"interview|prepare|ready|tips.*role",
        "career_advice": r"career|path|growth|transition",
        "formatting": r"format|layout|structure|organize",
    }
    
    for intent, pattern in intent_patterns.items():
        if re.search(pattern, question_lower):
            return intent
    
    return "general_help"


def improve_bullet_point(bullet: str, analysis_data: dict) -> ChatResponse:
    """
    Improve a single bullet point based on analysis context
    """
    response = ChatResponse()
    
    # Extract skills and metrics from analysis
    skills_found = analysis_data.get("skills_found", [])
    has_action_verb = False
    has_metric = False
    
    # Check for action verbs
    action_verbs = {
        "achieved", "built", "created", "designed", "developed", "directed",
        "discovered", "eliminated", "established", "expanded", "generated",
        "improved", "increased", "initiated", "implemented", "invented",
        "led", "launched", "optimized", "organized", "pioneered",
        "produced", "reduced", "restructured", "streamlined", "transformed",
    }
    
    bullet_lower = bullet.lower()
    has_action_verb = any(f"\b{verb}\b" in bullet_lower for verb in action_verbs)
    
    # Check for metrics
    has_metric = bool(re.search(r"\d+%|\$[\d,]+|\d+x|top\s+\d+", bullet))
    
    # Build response
    improvements = []
    
    if not has_action_verb:
        improvements.append("Start with a strong action verb (achieved, built, created, etc.)")
        response.tips.append("✨ Use power verbs to grab attention")
    
    if not has_metric:
        improvements.append("Add a quantifiable result (%, $, numbers, multiplier)")
        response.tips.append("📊 Metrics make achievements measurable")
    
    if len(bullet) < 20:
        improvements.append("Expand the bullet to show context and impact")
        response.tips.append("📝 Give enough detail to understand the achievement")
    
    if improvements:
        response.answer = f"Here's how to improve: '{bullet}'\n\n" + "\n".join(f"• {imp}" for imp in improvements)
        response.action_items = [f"Rewrite bullet with: {', '.join(improvements[:2])}"]
    else:
        response.answer = f"Nice bullet point! It has a strong action verb and includes metrics. Minor refinements:\n• Could emphasize business impact more\n• Consider adding context about the project/company"
        response.tips.append("✅ This bullet follows best practices")
    
    return response


def suggest_missing_skills(analysis_data: dict, target_role: Optional[str] = None) -> ChatResponse:
    """
    Suggest missing skills based on resume analysis and target role
    """
    response = ChatResponse()
    
    skills_found = analysis_data.get("skills_found", [])
    missing_skills = analysis_data.get("missing_skills", {})
    jd_comparison = analysis_data.get("jd_comparison", {})
    
    response.answer = f"You have {len(skills_found)} skills currently. "
    
    # Priority missing skills from JD
    jd_missing = jd_comparison.get("missing_skills", []) if jd_comparison else []
    if jd_missing:
        response.answer += f"\nFor your target JD, prioritize these:\n"
        for skill in jd_missing[:5]:
            response.tips.append(f"🎯 {skill}")
            response.action_items.append(f"Build project demonstrating {skill}")
    
    # Skills by category
    if missing_skills:
        response.answer += "\nSkills by category you might be missing:\n"
        for category, skills in list(missing_skills.items())[:3]:
            top_skill = skills[0] if skills else ""
            if top_skill:
                response.tips.append(f"{category}: {top_skill}")
    
    # Learning resources
    response.resources = [
        {"name": "freeCodeCamp", "url": "freecodecamp.org", "type": "Learning Platform"},
        {"name": "Coursera", "url": "coursera.org", "type": "Structured Courses"},
        {"name": "LeetCode", "url": "leetcode.com", "type": "Practice & Interview Prep"},
    ]
    
    if not response.tips:
        response.answer = "Your skill set looks well-rounded! Consider specializing deeper in one area or exploring complementary technologies."
    
    return response


def provide_ats_feedback(analysis_data: dict) -> ChatResponse:
    """
    Provide detailed ATS feedback based on scoring analysis
    """
    response = ChatResponse()
    
    ats_score = analysis_data.get("ats_score", 0)
    breakdown = analysis_data.get("breakdown", {})
    missing_sections = analysis_data.get("missing_sections", [])
    formatting_issues = analysis_data.get("formatting_issues", [])
    
    response.answer = f"Your ATS Score: {ats_score}/100\n\n"
    
    if ats_score >= 80:
        response.answer += "🟢 Excellent! Your resume will likely pass ATS filters.\n"
    elif ats_score >= 60:
        response.answer += "🟡 Moderate - You need improvements to reliably pass ATS filters.\n"
    else:
        response.answer += "🔴 Low - Significant changes needed to pass ATS screening.\n"
    
    # Breakdown
    if breakdown:
        response.answer += "\nScore Breakdown:\n"
        response.answer += f"• Keywords: {breakdown.get('keywords', 0)}/30\n"
        response.answer += f"• Sections: {breakdown.get('sections', 0)}/20\n"
        response.answer += f"• Format: {breakdown.get('format', 0)}/20\n"
        response.answer += f"• Experience: {breakdown.get('experience', 0)}/30\n"
    
    # Top issues
    issues = []
    if breakdown.get('keywords', 0) < 20:
        issues.append("Low keyword match - add more relevant technical terms")
        response.action_items.append("Add industry-specific keywords naturally")
    
    if breakdown.get('sections', 0) < 15:
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
            response.action_items.append(f"Add these sections: {', '.join(missing_sections[:3])}")
    
    if formatting_issues:
        issues.extend(formatting_issues[:2])
    
    if issues:
        response.answer += "\nKey Issues:\n"
        for issue in issues:
            response.tips.append(f"⚠️ {issue}")
    
    return response


def provide_resume_feedback(analysis_data: dict, target_role: Optional[str] = None) -> ChatResponse:
    """
    Provide comprehensive resume feedback for a specific role
    """
    response = ChatResponse()
    
    skills_found = analysis_data.get("skills_found", [])
    ats_score = analysis_data.get("ats_score", 0)
    
    response.answer = f"Resume Analysis Summary:\n"
    response.answer += f"• Current ATS Score: {ats_score}/100\n"
    response.answer += f"• Skills Listed: {len(skills_found)}\n"
    
    if target_role:
        response.answer += f"\nFor {target_role} role:\n"
    
    # Strengths
    response.answer += "\nStrengths:\n"
    if ats_score >= 60:
        response.tips.append("✅ Solid ATS score foundation")
    if len(skills_found) >= 8:
        response.tips.append("✅ Good technical skill breadth")
    
    # Improvements
    response.answer += "\nImportant Improvements:\n"
    if ats_score < 80:
        improvement = "Boost ATS score to 75+ for reliable ATS passage"
        response.action_items.append(improvement)
        response.tips.append(f"🎯 {improvement}")
    
    if len(skills_found) < 10:
        improvement = f"Add {10 - len(skills_found)} more relevant technical skills"
        response.action_items.append(improvement)
        response.tips.append(f"🎯 {improvement}")
    
    return response


def chat_assistant(question: str, context_data: dict) -> ChatResponse:
    """
    PHASE 8 MAIN FUNCTION
    Answer user questions with context from resume analysis
    
    Args:
        question: User's question
        context_data: Analysis context (ATS score, skills, etc.)
        
    Returns:
        ChatResponse with answer, tips, and action items
    """
    intent = _identify_intent(question)
    response = ChatResponse()
    
    if intent == "improve_bullet":
        # Extract bullet from context or question
        bullets = context_data.get("bullet_points", [])
        if bullets:
            response = improve_bullet_point(bullets[0], context_data)
        else:
            response.answer = "Share a bullet point from your resume, and I'll help improve it with stronger action verbs and metrics."
    
    elif intent == "suggest_skills":
        # Extract target role from question
        role_match = re.search(r"for?\s+(?:a\s+)?(\w+)\s+(?:role|position|job)", question, re.IGNORECASE)
        target_role = role_match.group(1) if role_match else None
        response = suggest_missing_skills(context_data, target_role)
    
    elif intent == "ats_feedback":
        response = provide_ats_feedback(context_data)
    
    elif intent == "resume_feedback":
        # Extract target role if mentioned
        role_match = re.search(r"for?\s+(?:a\s+)?(\w+)\s+(?:role|position|job)", question, re.IGNORECASE)
        target_role = role_match.group(1) if role_match else None
        response = provide_resume_feedback(context_data, target_role)
    
    else:
        response.answer = "I'm your AI resume assistant! I can help you:\n"
        response.answer += "• Improve bullet points\n"
        response.answer += "• Suggest missing skills\n"
        response.answer += "• Boost your ATS score\n"
        response.answer += "• Tailor resume to job descriptions\n"
        response.answer += "• Provide interview preparation tips\n\n"
        response.answer += "What would you like help with?"
    
    return response
