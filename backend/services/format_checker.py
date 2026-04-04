"""
Resume Format Checking Module
Analyzes resume structure, length, bullet points, action verbs, and quantified results
"""

import re
import fitz  # PyMuPDF
from docx import Document


def check_resume_format(file_path, resume_text):
    """
    Comprehensive resume format analysis
    
    Args:
        file_path (str): Path to resume file (PDF or DOCX)
        resume_text (str): Extracted text from resume
        
    Returns:
        dict: Format analysis with warnings and suggestions
    """
    # Determine file type
    file_extension = file_path.lower().split('.')[-1]
    
    # Check page length
    page_count = get_page_count(file_path, file_extension)
    length_check = check_page_length(page_count)
    
    # Extract and check bullet points
    bullet_points = extract_bullet_points(resume_text)
    bullet_check = check_bullet_points(bullet_points)
    
    # Check action verbs
    verb_check = check_action_verbs(resume_text, bullet_points)
    
    # Check for quantified results
    quantified_check = check_quantified_results(resume_text)
    
    # Check for weak wording
    weak_wording_check = check_weak_wording(resume_text)
    
    # Calculate overall format score
    format_score = calculate_format_score(
        length_check, bullet_check, verb_check, quantified_check, weak_wording_check
    )
    
    # Build consolidated warnings list
    all_warnings = build_warnings_list(
        length_check, bullet_check, verb_check, quantified_check, weak_wording_check
    )
    
    return {
        'format_score': format_score,
        'page_count': page_count,
        'length_analysis': length_check,
        'bullet_point_analysis': bullet_check,
        'action_verb_analysis': verb_check,
        'quantified_results_analysis': quantified_check,
        'weak_wording_analysis': weak_wording_check,
        'warnings': all_warnings,
        'overall_suggestions': generate_format_suggestions(
            length_check, bullet_check, verb_check, quantified_check
        )
    }


def get_page_count(file_path, file_extension):
    """
    Get number of pages in resume
    
    Args:
        file_path (str): Path to file
        file_extension (str): File extension (pdf, doc, docx)
        
    Returns:
        int: Number of pages
    """
    try:
        if file_extension == 'pdf':
            pdf_doc = fitz.open(file_path)
            page_count = pdf_doc.page_count
            pdf_doc.close()
            return page_count
            
        elif file_extension in ['doc', 'docx']:
            doc = Document(file_path)
            # Approximate page count (DOCX doesn't have exact pages)
            # Estimate: ~500 words per page
            total_text = '\n'.join([para.text for para in doc.paragraphs])
            word_count = len(total_text.split())
            return max(1, round(word_count / 500))
            
    except Exception as e:
        print(f"Error getting page count: {e}")
        return 1  # Default to 1 page


def check_page_length(page_count):
    """
    Check if resume length is appropriate
    
    Args:
        page_count (int): Number of pages
        
    Returns:
        dict: Length analysis
    """
    if page_count <= 2:
        status = 'Good'
        message = f'Resume length is ideal ({page_count} page{"s" if page_count > 1 else ""})'
        warning = False
    elif page_count == 3:
        status = 'Warning'
        message = f'Resume is {page_count} pages - consider condensing to 1-2 pages'
        warning = True
    else:
        status = 'Poor'
        message = f'Resume is too long ({page_count} pages) - reduce to 1-2 pages maximum'
        warning = True
        
    return {
        'status': status,
        'page_count': page_count,
        'message': message,
        'has_warning': warning
    }


def extract_bullet_points(text):
    """
    Extract bullet points from resume text
    
    Args:
        text (str): Resume text
        
    Returns:
        list: List of bullet point strings
    """
    bullet_points = []
    
    # Common bullet point indicators
    patterns = [
        r'•\s*(.+)',  # Bullet •
        r'–\s*(.+)',  # En dash
        r'-\s*(.+)',  # Hyphen
        r'▪\s*(.+)',  # Small bullet
        r'►\s*(.+)',  # Arrow
        r'\*\s*(.+)', # Asterisk
    ]
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Try each pattern
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                bullet_text = match.group(1).strip()
                if len(bullet_text) > 10:  # Ignore very short lines
                    bullet_points.append(bullet_text)
                break
    
    return bullet_points


def check_bullet_points(bullet_points):
    """
    Analyze bullet point quality
    
    Args:
        bullet_points (list): List of bullet points
        
    Returns:
        dict: Bullet point analysis
    """
    if not bullet_points:
        return {
            'status': 'Warning',
            'total_bullets': 0,
            'long_bullets': 0,
            'message': 'No bullet points detected - use bullets to highlight achievements',
            'warnings': ['Add bullet points to make resume scannable']
        }
    
    # Check bullet length (ideal: 10-20 words, max: 25 words)
    long_bullets = []
    short_bullets = []
    
    for bullet in bullet_points:
        word_count = len(bullet.split())
        if word_count > 25:
            long_bullets.append(bullet[:60] + '...')
        elif word_count < 5:
            short_bullets.append(bullet)
    
    warnings = []
    if long_bullets:
        warnings.append(f'{len(long_bullets)} bullet points are too long (>25 words)')
    if short_bullets:
        warnings.append(f'{len(short_bullets)} bullet points are too short (<5 words)')
    
    # Determine status
    if not warnings:
        status = 'Good'
        message = 'Bullet points are well-structured'
    elif len(long_bullets) + len(short_bullets) < len(bullet_points) * 0.3:
        status = 'Fair'
        message = 'Most bullet points are good, but some need improvement'
    else:
        status = 'Warning'
        message = 'Many bullet points need to be revised for optimal length'
    
    return {
        'status': status,
        'total_bullets': len(bullet_points),
        'long_bullets': len(long_bullets),
        'short_bullets': len(short_bullets),
        'message': message,
        'warnings': warnings,
        'examples': long_bullets[:3]  # Show first 3 examples
    }


def check_action_verbs(text, bullet_points):
    """
    Check for weak vs strong action verbs
    
    Args:
        text (str): Resume text
        bullet_points (list): List of bullet points
        
    Returns:
        dict: Action verb analysis
    """
    # Weak verbs to avoid
    weak_verbs = [
        'worked', 'did', 'made', 'got', 'helped', 'handled', 'responsible for',
        'duties included', 'was', 'were', 'am', 'is', 'are', 'been', 'being',
        'involved in', 'assisted', 'participated'
    ]
    
    # Strong action verbs (categorized)
    strong_verbs = {
        'leadership': ['led', 'directed', 'managed', 'coordinated', 'supervised', 'mentored'],
        'achievement': ['achieved', 'improved', 'increased', 'reduced', 'boosted', 'enhanced'],
        'creation': ['developed', 'designed', 'created', 'built', 'established', 'launched'],
        'analysis': ['analyzed', 'evaluated', 'assessed', 'researched', 'investigated'],
        'communication': ['presented', 'communicated', 'collaborated', 'negotiated', 'facilitated']
    }
    
    text_lower = text.lower()
    
    # Find weak verbs
    weak_verb_count = 0
    weak_verbs_found = []
    
    for verb in weak_verbs:
        if verb in text_lower:
            weak_verb_count += text_lower.count(verb)
            weak_verbs_found.append(verb)
    
    # Find strong verbs
    strong_verb_count = 0
    strong_verbs_found = []
    
    for category, verbs in strong_verbs.items():
        for verb in verbs:
            if verb in text_lower:
                strong_verb_count += 1
                strong_verbs_found.append(verb)
    
    # Calculate strength ratio
    total_verbs = weak_verb_count + strong_verb_count
    strong_ratio = (strong_verb_count / total_verbs * 100) if total_verbs > 0 else 0
    
    # Determine status
    if strong_ratio >= 70:
        status = 'Good'
        message = 'Good use of strong action verbs'
    elif strong_ratio >= 40:
        status = 'Fair'
        message = 'Mix of weak and strong verbs - replace weak verbs with stronger alternatives'
    else:
        status = 'Poor'
        message = 'Weak action verb usage detected - use impactful action verbs'
    
    # Generate suggestions
    suggestions = []
    if weak_verbs_found:
        suggestions.append(f"Replace weak verbs: {', '.join(list(set(weak_verbs_found))[:5])}")
        suggestions.append("Use strong action verbs like: developed, achieved, led, designed, improved")
    
    return {
        'status': status,
        'weak_verb_count': weak_verb_count,
        'strong_verb_count': strong_verb_count,
        'strong_ratio': round(strong_ratio, 1),
        'message': message,
        'weak_verbs_found': list(set(weak_verbs_found)),
        'suggestions': suggestions
    }


def check_quantified_results(text):
    """
    Check for quantified results (numbers, percentages, metrics)
    
    Args:
        text (str): Resume text
        
    Returns:
        dict: Quantified results analysis
    """
    # Patterns for quantified results
    patterns = [
        r'\d+%',  # Percentages (e.g., 25%)
        r'\$\d+',  # Money (e.g., $50K)
        r'\d+[KkMm]',  # Thousands/Millions (e.g., 10K, 5M)
        r'\d+\+',  # Plus numbers (e.g., 100+)
        r'\d+x',  # Multipliers (e.g., 5x)
        r'\d+\s*(million|thousand|billion|hours|days|users|customers|projects)',  # Metrics
    ]
    
    metrics_found = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics_found.extend(matches)
    
    metric_count = len(metrics_found)
    
    # Determine status
    if metric_count >= 5:
        status = 'Good'
        message = f'Good quantification with {metric_count} measurable results'
    elif metric_count >= 2:
        status = 'Fair'
        message = f'Some quantification ({metric_count} metrics) - add more measurable achievements'
    else:
        status = 'Poor'
        message = 'Few or no quantified results detected'
    
    suggestions = []
    if metric_count < 5:
        suggestions.append("Add numbers to quantify your impact (e.g., 'increased sales by 25%')")
        suggestions.append("Include metrics: percentages, dollar amounts, time saved, users impacted")
        suggestions.append("Examples: 'Reduced costs by $50K', 'Managed team of 10+', 'Improved efficiency by 30%'")
    
    return {
        'status': status,
        'metric_count': metric_count,
        'message': message,
        'examples': list(set(metrics_found))[:10],
        'suggestions': suggestions
    }


def check_weak_wording(text):
    """
    Detect weak, vague, or passive wording that weakens resume impact.
    
    Returns:
        dict: Weak wording analysis with found phrases and replacements
    """
    weak_phrases = {
        "responsible for": "Led / Managed / Directed",
        "duties included": "Achieved / Delivered / Executed",
        "helped with": "Contributed to / Supported / Drove",
        "worked on": "Developed / Built / Designed",
        "assisted in": "Collaborated on / Facilitated",
        "was involved in": "Participated in / Spearheaded",
        "played a role in": "Drove / Championed / Influenced",
        "familiar with": "Proficient in / Experienced with",
        "some experience": "Demonstrated ability in",
        "basic knowledge": "Foundational expertise in",
        "team player": "Collaborated cross-functionally",
        "hard worker": "Dedicated professional with proven results",
        "self-starter": "Proactive initiator",
        "detail-oriented": "Ensured accuracy and quality",
        "good communication": "Strong verbal and written communication",
        "various": "Specify exactly what/how many",
        "several": "Specify the exact number",
        "many": "Quantify with a specific number",
        "stuff": "Replace with specific deliverables",
        "things": "Replace with specific items/tasks",
        "etc": "List all relevant items explicitly",
    }

    text_lower = text.lower()
    found_weak = []

    for phrase, replacement in weak_phrases.items():
        count = text_lower.count(phrase)
        if count > 0:
            found_weak.append({
                "phrase": phrase,
                "replacement": replacement,
                "count": count,
            })

    # Sort by count descending
    found_weak.sort(key=lambda x: -x["count"])

    total_weak = sum(item["count"] for item in found_weak)

    if total_weak == 0:
        status = "Good"
        message = "No weak wording detected — strong language throughout"
    elif total_weak <= 3:
        status = "Fair"
        message = f"Found {total_weak} instances of weak wording — minor improvements possible"
    else:
        status = "Poor"
        message = f"Found {total_weak} instances of weak/vague wording — strengthen your language"

    return {
        "status": status,
        "total_weak_phrases": total_weak,
        "message": message,
        "weak_phrases_found": found_weak,
    }


def calculate_format_score(length_check, bullet_check, verb_check, quantified_check, weak_wording_check=None):
    """
    Calculate overall format score (0-100)
    
    Args:
        length_check (dict): Page length analysis
        bullet_check (dict): Bullet point analysis
        verb_check (dict): Action verb analysis
        quantified_check (dict): Quantified results analysis
        weak_wording_check (dict): Weak wording analysis
        
    Returns:
        int: Overall format score
    """
    # Scoring weights
    scores = {
        'length': 0,
        'bullets': 0,
        'verbs': 0,
        'quantified': 0,
        'wording': 0,
    }
    
    # Length score (20 points)
    if length_check['status'] == 'Good':
        scores['length'] = 20
    elif length_check['status'] == 'Warning':
        scores['length'] = 12
    else:
        scores['length'] = 4
    
    # Bullet score (20 points)
    if bullet_check['status'] == 'Good':
        scores['bullets'] = 20
    elif bullet_check['status'] == 'Fair':
        scores['bullets'] = 12
    else:
        scores['bullets'] = 4
    
    # Verb score (20 points)
    if verb_check['status'] == 'Good':
        scores['verbs'] = 20
    elif verb_check['status'] == 'Fair':
        scores['verbs'] = 12
    else:
        scores['verbs'] = 4
    
    # Quantified score (20 points)
    if quantified_check['status'] == 'Good':
        scores['quantified'] = 20
    elif quantified_check['status'] == 'Fair':
        scores['quantified'] = 12
    else:
        scores['quantified'] = 4
    
    # Weak wording score (20 points)
    if weak_wording_check:
        if weak_wording_check['status'] == 'Good':
            scores['wording'] = 20
        elif weak_wording_check['status'] == 'Fair':
            scores['wording'] = 12
        else:
            scores['wording'] = 4
    else:
        scores['wording'] = 15  # Default if not checked
    
    total_score = sum(scores.values())
    return total_score


def build_warnings_list(length_check, bullet_check, verb_check, quantified_check, weak_wording_check):
    """
    Build a consolidated list of warning objects for the frontend.
    
    Each warning has: id, priority (high/medium/low), category, title, message, suggestion
    """
    warnings = []
    warning_id = 0
    
    # ── Page length warnings ──
    if length_check['has_warning']:
        warning_id += 1
        warnings.append({
            'id': warning_id,
            'priority': 'high' if length_check['status'] == 'Poor' else 'medium',
            'category': 'Page Length',
            'icon': '📄',
            'title': 'Resume Length Issue',
            'message': length_check['message'],
            'suggestion': 'Keep your resume to 1-2 pages. Remove outdated or irrelevant content.',
        })
    
    # ── Bullet point warnings ──
    if bullet_check['status'] != 'Good':
        for w in bullet_check.get('warnings', []):
            warning_id += 1
            warnings.append({
                'id': warning_id,
                'priority': 'high' if bullet_check['status'] == 'Warning' else 'medium',
                'category': 'Bullet Points',
                'icon': '📝',
                'title': 'Bullet Point Issue',
                'message': w,
                'suggestion': 'Use 10-20 word bullet points starting with action verbs.',
            })
        if bullet_check['total_bullets'] == 0:
            warning_id += 1
            warnings.append({
                'id': warning_id,
                'priority': 'high',
                'category': 'Bullet Points',
                'icon': '📝',
                'title': 'No Bullet Points Found',
                'message': 'Your resume doesn\'t use bullet points — they help ATS and recruiters scan quickly.',
                'suggestion': 'Add bullet points under Experience and Projects sections.',
            })
    
    # ── Action verb warnings ──
    if verb_check['status'] != 'Good':
        warning_id += 1
        priority = 'high' if verb_check['status'] == 'Poor' else 'medium'
        weak_list = ', '.join(verb_check.get('weak_verbs_found', [])[:5])
        warnings.append({
            'id': warning_id,
            'priority': priority,
            'category': 'Action Verbs',
            'icon': '💪',
            'title': 'Weak Action Verbs Detected',
            'message': f"{verb_check['message']}. Weak verbs found: {weak_list}" if weak_list else verb_check['message'],
            'suggestion': 'Replace with: Led, Developed, Achieved, Designed, Implemented, Optimized.',
        })
    
    # ── Quantified results warnings ──
    if quantified_check['status'] != 'Good':
        warning_id += 1
        warnings.append({
            'id': warning_id,
            'priority': 'high' if quantified_check['status'] == 'Poor' else 'medium',
            'category': 'Quantified Results',
            'icon': '📊',
            'title': 'Lack of Measurable Results',
            'message': quantified_check['message'],
            'suggestion': "Add metrics: 'Increased revenue by 25%', 'Managed team of 10+', 'Reduced load time by 40%'.",
        })
    
    # ── Weak wording warnings ──
    if weak_wording_check and weak_wording_check['status'] != 'Good':
        for item in weak_wording_check.get('weak_phrases_found', [])[:5]:
            warning_id += 1
            warnings.append({
                'id': warning_id,
                'priority': 'medium' if item['count'] <= 2 else 'high',
                'category': 'Weak Wording',
                'icon': '⚠️',
                'title': f'Weak phrase: "{item["phrase"]}"',
                'message': f'Found {item["count"]} time{"s" if item["count"] > 1 else ""}. This weakens your resume impact.',
                'suggestion': f'Replace with: {item["replacement"]}',
            })
    
    # Sort: high first, then medium, then low
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    warnings.sort(key=lambda w: priority_order.get(w['priority'], 1))
    
    return warnings


def generate_format_suggestions(length_check, bullet_check, verb_check, quantified_check):
    """
    Generate overall format improvement suggestions
    
    Args:
        length_check, bullet_check, verb_check, quantified_check: Analysis results
        
    Returns:
        list: List of prioritized suggestions
    """
    suggestions = []
    
    # High priority suggestions
    if length_check['has_warning']:
        suggestions.append(f"PRIORITY: {length_check['message']}")
    
    if verb_check['status'] == 'Poor':
        suggestions.append("PRIORITY: Replace weak verbs with strong action verbs")
    
    if quantified_check['status'] == 'Poor':
        suggestions.append("PRIORITY: Add quantified results to demonstrate impact")
    
    # Additional suggestions
    if bullet_check['status'] != 'Good':
        suggestions.extend(bullet_check['warnings'])
    
    if verb_check['suggestions']:
        suggestions.extend(verb_check['suggestions'])
    
    if quantified_check['suggestions']:
        suggestions.extend(quantified_check['suggestions'][:2])
    
    # General formatting tips
    suggestions.append("Use consistent formatting throughout the document")
    suggestions.append("Ensure proper spacing and margins (0.5-1 inch)")
    
    return suggestions


# Example usage
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Experience:
    • Worked on multiple projects using Python and JavaScript
    • Helped develop web applications
    • Reduced load time by 40%
    • Managed a team of 5 developers and improved deployment speed by 50%
    • Responsible for database optimization which saved $20K annually
    """
    
    # Note: For full testing, you need an actual file path
    print("Format Checker Module - Test mode")
    print("Note: Page count check requires actual PDF/DOCX file")
