"""
AI Resume Rewriter Module
Improves bullet points and experience descriptions using rule-based transformations
and optionally LLM integration
"""

import re
import random


class ResumeRewriter:
    """
    Rewrites resume bullet points to make them more impactful and professional
    """
    
    def __init__(self):
        """Initialize the rewriter with verb and phrase mappings"""
        self.weak_to_strong_verbs = {
            # Weak verbs → Strong alternatives
            'worked on': ['developed', 'engineered', 'built', 'designed', 'implemented'],
            'did': ['accomplished', 'executed', 'delivered', 'achieved', 'completed'],
            'made': ['created', 'produced', 'generated', 'constructed', 'established'],
            'helped': ['assisted', 'supported', 'facilitated', 'contributed to', 'enabled'],
            'handled': ['managed', 'coordinated', 'oversaw', 'directed', 'administered'],
            'responsible for': ['led', 'managed', 'directed', 'oversaw', 'spearheaded'],
            'was involved in': ['participated in', 'contributed to', 'collaborated on'],
            'got': ['achieved', 'obtained', 'secured', 'acquired', 'attained'],
            'used': ['utilized', 'leveraged', 'employed', 'applied', 'implemented'],
            'tried': ['attempted', 'endeavored', 'initiated', 'pioneered'],
            'fixed': ['resolved', 'corrected', 'remediated', 'debugged', 'optimized'],
        }
        
        # Strong action verbs by category
        self.strong_verbs = {
            'leadership': [
                'led', 'directed', 'managed', 'coordinated', 'supervised',
                'mentored', 'guided', 'orchestrated', 'spearheaded', 'championed'
            ],
            'achievement': [
                'achieved', 'improved', 'increased', 'reduced', 'boosted',
                'enhanced', 'optimized', 'exceeded', 'surpassed', 'accelerated'
            ],
            'creation': [
                'developed', 'designed', 'created', 'built', 'established',
                'launched', 'engineered', 'architected', 'pioneered', 'innovated'
            ],
            'analysis': [
                'analyzed', 'evaluated', 'assessed', 'researched', 'investigated',
                'examined', 'identified', 'diagnosed', 'measured', 'quantified'
            ],
            'communication': [
                'presented', 'communicated', 'collaborated', 'negotiated', 'facilitated',
                'articulated', 'conveyed', 'documented', 'reported', 'briefed'
            ]
        }
        
        # Metrics and impact phrases
        self.impact_phrases = [
            'resulting in {metric}',
            'leading to {metric}',
            'achieving {metric}',
            'which improved {metric}',
            'driving {metric}',
            'delivering {metric}'
        ]
        
        # Common metrics templates
        self.metric_templates = [
            '{num}% improvement',
            '{num}% increase in efficiency',
            '{num}% reduction in costs',
            '{num}x faster performance',
            '${num}K in cost savings',
            '{num}+ users/customers',
            '{num}% higher conversion rate'
        ]
    
    
    def rewrite_bullet_points(self, bullet_points_list, add_metrics_suggestions=True):
        """
        Rewrite multiple bullet points
        
        Args:
            bullet_points_list (list): List of bullet point strings
            add_metrics_suggestions (bool): Whether to suggest adding metrics
            
        Returns:
            list: List of dictionaries with original and improved versions
        """
        results = []
        
        for bullet in bullet_points_list:
            if not bullet or len(bullet.strip()) < 5:
                continue
                
            improved = self.improve_bullet_point(bullet)
            
            result = {
                'original': bullet.strip(),
                'improved': improved['text'],
                'changes': improved['changes'],
                'suggestions': improved['suggestions']
            }
            
            # Add metric suggestions if bullet lacks quantification
            if add_metrics_suggestions and not self._has_metrics(bullet):
                result['suggestions'].append("Consider adding quantifiable results (e.g., percentages, numbers, time saved)")
            
            results.append(result)
        
        return results
    
    
    def improve_bullet_point(self, bullet_text):
        """
        Improve a single bullet point
        
        Args:
            bullet_text (str): Original bullet point text
            
        Returns:
            dict: Improved text, changes made, and suggestions
        """
        improved = bullet_text.strip()
        changes_made = []
        suggestions = []
        
        # Remove bullet symbols if present
        improved = re.sub(r'^[•\-–▪►\*]\s*', '', improved)
        
        # Step 1: Replace weak verbs with strong verbs
        improved, weak_verbs_replaced = self._replace_weak_verbs(improved)
        if weak_verbs_replaced:
            changes_made.append(f"Replaced weak verbs: {', '.join(weak_verbs_replaced)}")
        
        # Step 2: Remove passive voice
        improved, passive_removed = self._remove_passive_voice(improved)
        if passive_removed:
            changes_made.append("Converted passive voice to active")
        
        # Step 3: Condense wordy phrases
        improved, condensed = self._condense_wordy_phrases(improved)
        if condensed:
            changes_made.append("Condensed wordy phrases")
        
        # Step 4: Ensure it starts with a strong verb
        improved, verb_added = self._ensure_strong_start(improved)
        if verb_added:
            changes_made.append(f"Started with action verb: '{verb_added}'")
        
        # Step 5: Optimize length (ideal: 15-20 words)
        word_count = len(improved.split())
        if word_count > 25:
            suggestions.append("Consider shortening this bullet point (currently too long)")
        elif word_count < 8:
            suggestions.append("Consider expanding with more details or impact")
        
        # Step 6: Check for metrics
        if not self._has_metrics(improved):
            suggestions.append("Add quantifiable metrics to demonstrate impact")
        
        # Capitalize first letter
        if improved:
            improved = improved[0].upper() + improved[1:]
        
        return {
            'text': improved,
            'changes': changes_made,
            'suggestions': suggestions
        }
    
    
    def _replace_weak_verbs(self, text):
        """Replace weak verbs with strong alternatives"""
        text_lower = text.lower()
        replaced_verbs = []
        
        for weak, strong_options in self.weak_to_strong_verbs.items():
            if weak in text_lower:
                # Choose a random strong alternative
                replacement = random.choice(strong_options)
                
                # Replace (case-insensitive)
                pattern = re.compile(re.escape(weak), re.IGNORECASE)
                text = pattern.sub(replacement, text, count=1)
                
                replaced_verbs.append(weak)
        
        return text, replaced_verbs
    
    
    def _remove_passive_voice(self, text):
        """Convert passive voice to active voice where possible"""
        passive_patterns = [
            (r'was responsible for (\w+)', r'managed \1'),
            (r'were responsible for (\w+)', r'managed \1'),
            (r'was involved in (\w+)', r'participated in \1'),
            (r'were involved in (\w+)', r'participated in \1'),
            (r'was tasked with (\w+)', r'\1'),
            (r'were tasked with (\w+)', r'\1'),
            (r'was assigned to (\w+)', r'\1'),
        ]
        
        changed = False
        for pattern, replacement in passive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                changed = True
        
        return text, changed
    
    
    def _condense_wordy_phrases(self, text):
        """Replace wordy phrases with concise alternatives"""
        condensations = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'at the present time': 'currently',
            'for the purpose of': 'to',
            'in the event that': 'if',
            'on a daily basis': 'daily',
            'on a regular basis': 'regularly',
            'a number of': 'several',
            'a large number of': 'many',
            'in spite of the fact that': 'although',
            'with the exception of': 'except',
        }
        
        changed = False
        for wordy, concise in condensations.items():
            if wordy in text.lower():
                pattern = re.compile(re.escape(wordy), re.IGNORECASE)
                text = pattern.sub(concise, text)
                changed = True
        
        return text, changed
    
    
    def _ensure_strong_start(self, text):
        """Ensure bullet starts with a strong action verb"""
        # Check if it already starts with a strong verb
        first_word = text.split()[0].lower() if text.split() else ''
        
        all_strong_verbs = []
        for category in self.strong_verbs.values():
            all_strong_verbs.extend(category)
        
        # If already starts with strong verb, no change needed
        if first_word in [v.lower() for v in all_strong_verbs]:
            return text, None
        
        # Common weak starts to replace
        weak_starts = {
            'involved in': 'led',
            'worked with': 'collaborated with',
            'participated in': 'contributed to',
            'helped with': 'supported',
        }
        
        for weak, strong in weak_starts.items():
            if text.lower().startswith(weak):
                text = strong + text[len(weak):]
                return text, strong
        
        return text, None
    
    
    def _has_metrics(self, text):
        """Check if text contains quantifiable metrics"""
        metric_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Money
            r'\d+[KkMm]',  # Thousands/Millions
            r'\d+\+',  # Plus numbers
            r'\d+x',  # Multipliers
            r'\d+\s*(million|thousand|billion|hours|days|users|customers|clients)',
        ]
        
        for pattern in metric_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    
    def suggest_metric_additions(self, bullet_text):
        """
        Suggest where metrics could be added to a bullet point
        
        Args:
            bullet_text (str): Bullet point text
            
        Returns:
            list: Suggested metric additions with examples
        """
        suggestions = []
        
        # Keywords that often have measurable impact
        impact_keywords = {
            'improved': 'by X%',
            'increased': 'by X%',
            'reduced': 'by X%',
            'developed': 'for X users/clients',
            'managed': 'team of X members',
            'saved': '$X or X hours',
            'launched': 'reaching X users',
            'optimized': 'resulting in X% improvement',
        }
        
        text_lower = bullet_text.lower()
        
        for keyword, metric_suggestion in impact_keywords.items():
            if keyword in text_lower:
                suggestions.append({
                    'keyword': keyword,
                    'suggestion': f"Add metric: {metric_suggestion}",
                    'example': f"Example: '{keyword.capitalize()} ... {metric_suggestion}'"
                })
        
        if not suggestions:
            suggestions.append({
                'general': True,
                'suggestion': 'Add specific numbers, percentages, or time frames',
                'examples': [
                    'Increased efficiency by 25%',
                    'Managed team of 5 developers',
                    'Reduced costs by $50K annually',
                    'Served 10K+ customers'
                ]
            })
        
        return suggestions


# Standalone function for ease of use
def rewrite_bullet_points(bullet_points_list, add_metrics_suggestions=True):
    """
    Convenience function to rewrite bullet points
    
    Args:
        bullet_points_list (list): List of bullet points to improve
        add_metrics_suggestions (bool): Whether to add metric suggestions
        
    Returns:
        list: Improved bullet points with suggestions
    """
    rewriter = ResumeRewriter()
    return rewriter.rewrite_bullet_points(bullet_points_list, add_metrics_suggestions)


# Example usage
if __name__ == "__main__":
    # Test the rewriter
    sample_bullets = [
        "Worked on ML project for customer segmentation",
        "Responsible for managing a team and did code reviews",
        "Helped improve the website performance",
        "Was involved in developing REST APIs using Python",
        "Fixed bugs in the production system on a regular basis"
    ]
    
    print("=== Resume Bullet Point Rewriter ===\n")
    
    results = rewrite_bullet_points(sample_bullets)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Bullet {i} ---")
        print(f"Original:  {result['original']}")
        print(f"Improved:  {result['improved']}")
        
        if result['changes']:
            print(f"Changes:   {', '.join(result['changes'])}")
        
        if result['suggestions']:
            print(f"Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
