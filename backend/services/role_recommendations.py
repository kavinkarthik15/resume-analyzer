"""
Role-Based Skill Recommendation Module
Compares resume skills against target role requirements and calculates readiness score
"""


def get_role_skill_mapping():
    """
    Comprehensive role-skill mapping for different job positions
    
    Returns:
        dict: Mapping of roles to required skills
    """
    return {
        'Data Scientist': {
            'required': [
                'Python', 'R', 'SQL', 'Statistics', 'Machine Learning',
                'Pandas', 'NumPy', 'Data Visualization', 'Deep Learning'
            ],
            'preferred': [
                'TensorFlow', 'PyTorch', 'scikit-learn', 'Tableau', 'Power BI',
                'Big Data', 'Apache Spark', 'AWS', 'A/B Testing', 'NLP'
            ]
        },
        'Web Developer': {
            'required': [
                'HTML', 'CSS', 'JavaScript', 'React', 'Node.js',
                'Git', 'REST API', 'Responsive Design'
            ],
            'preferred': [
                'TypeScript', 'Redux', 'Next.js', 'Vue.js', 'Angular',
                'MongoDB', 'PostgreSQL', 'GraphQL', 'Docker', 'AWS'
            ]
        },
        'AI Engineer': {
            'required': [
                'Python', 'Machine Learning', 'Deep Learning', 'TensorFlow',
                'PyTorch', 'Neural Networks', 'Data Structures', 'Algorithms'
            ],
            'preferred': [
                'Computer Vision', 'NLP', 'Keras', 'Model Deployment',
                'MLOps', 'Docker', 'Kubernetes', 'AWS', 'Data Pipelines', 'Reinforcement Learning'
            ]
        },
        'Backend Developer': {
            'required': [
                'Python', 'Java', 'Node.js', 'SQL', 'REST API',
                'Git', 'Database Design', 'API Development'
            ],
            'preferred': [
                'Django', 'Flask', 'Spring Boot', 'MongoDB', 'Redis',
                'Microservices', 'Docker', 'Kubernetes', 'AWS', 'GraphQL'
            ]
        },
        'Frontend Developer': {
            'required': [
                'HTML', 'CSS', 'JavaScript', 'React', 'Responsive Design',
                'Git', 'UI/UX Principles', 'Cross-browser Compatibility'
            ],
            'preferred': [
                'TypeScript', 'Redux', 'Tailwind CSS', 'Next.js', 'Vue.js',
                'Angular', 'Webpack', 'Jest', 'Accessibility', 'Performance Optimization'
            ]
        },
        'Full Stack Developer': {
            'required': [
                'HTML', 'CSS', 'JavaScript', 'React', 'Node.js',
                'SQL', 'REST API', 'Git', 'Database Design'
            ],
            'preferred': [
                'TypeScript', 'MongoDB', 'PostgreSQL', 'Docker', 'AWS',
                'CI/CD', 'Redux', 'Express.js', 'GraphQL', 'Microservices'
            ]
        },
        'DevOps Engineer': {
            'required': [
                'Linux', 'Docker', 'Kubernetes', 'CI/CD', 'Git',
                'Shell Scripting', 'AWS', 'Infrastructure as Code'
            ],
            'preferred': [
                'Terraform', 'Ansible', 'Jenkins', 'Azure', 'GCP',
                'Monitoring', 'Prometheus', 'Grafana', 'Python', 'GitLab CI'
            ]
        },
        'Mobile Developer': {
            'required': [
                'iOS', 'Android', 'Swift', 'Kotlin', 'Mobile UI/UX',
                'Git', 'REST API', 'App Deployment'
            ],
            'preferred': [
                'React Native', 'Flutter', 'Firebase', 'Push Notifications',
                'App Store Optimization', 'Performance Optimization', 'SQLite', 'GraphQL'
            ]
        },
        'Cloud Architect': {
            'required': [
                'AWS', 'Azure', 'Cloud Architecture', 'Microservices',
                'Docker', 'Kubernetes', 'Security Best Practices', 'Networking'
            ],
            'preferred': [
                'Terraform', 'CloudFormation', 'Serverless', 'Lambda',
                'API Gateway', 'Cost Optimization', 'Multi-cloud', 'Disaster Recovery'
            ]
        },
        'Machine Learning Engineer': {
            'required': [
                'Python', 'Machine Learning', 'TensorFlow', 'PyTorch',
                'Data Preprocessing', 'Model Deployment', 'Statistics', 'Algorithms'
            ],
            'preferred': [
                'MLOps', 'Docker', 'Kubernetes', 'Apache Spark', 'AWS',
                'Feature Engineering', 'Model Optimization', 'A/B Testing', 'Deep Learning'
            ]
        },
        'QA Engineer': {
            'required': [
                'Manual Testing', 'Test Automation', 'Selenium', 'QA Methodologies',
                'Bug Tracking', 'Test Cases', 'API Testing'
            ],
            'preferred': [
                'Pytest', 'Jest', 'Cypress', 'JUnit', 'Performance Testing',
                'CI/CD', 'Python', 'JavaScript', 'Load Testing', 'Security Testing'
            ]
        },
        'Product Manager': {
            'required': [
                'Product Strategy', 'Roadmap Planning', 'Agile', 'Scrum',
                'User Research', 'Data Analysis', 'Stakeholder Management', 'Wireframing'
            ],
            'preferred': [
                'JIRA', 'SQL', 'A/B Testing', 'Analytics Tools', 'Figma',
                'Market Research', 'Competitive Analysis', 'MVP Development', 'KPI Tracking'
            ]
        }
    }


def role_skill_recommendation(resume_skills, role, role_skill_mapping=None):
    """
    Analyze resume skills against target role requirements
    
    Args:
        resume_skills (list): Skills extracted from resume
        role (str): Target job role
        role_skill_mapping (dict, optional): Custom role-skill mapping
        
    Returns:
        dict: Skill gap analysis and readiness score
    """
    # Get role skill mapping
    if role_skill_mapping is None:
        role_skill_mapping = get_role_skill_mapping()
    
    # Check if role exists
    if role not in role_skill_mapping:
        return {
            'error': f"Role '{role}' not found in database",
            'available_roles': list(role_skill_mapping.keys())
        }
    
    # Get required and preferred skills for the role
    role_skills = role_skill_mapping[role]
    required_skills = role_skills.get('required', [])
    preferred_skills = role_skills.get('preferred', [])
    
    # Normalize resume skills (case-insensitive comparison)
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    
    # Find matched and missing skills
    matched_required = []
    missing_required = []
    
    for skill in required_skills:
        if skill.lower() in resume_skills_lower:
            matched_required.append(skill)
        else:
            missing_required.append(skill)
    
    matched_preferred = []
    missing_preferred = []
    
    for skill in preferred_skills:
        if skill.lower() in resume_skills_lower:
            matched_preferred.append(skill)
        else:
            missing_preferred.append(skill)
    
    # Calculate readiness score
    # Required skills: 70% weight, Preferred skills: 30% weight
    required_score = (len(matched_required) / len(required_skills) * 70) if required_skills else 0
    preferred_score = (len(matched_preferred) / len(preferred_skills) * 30) if preferred_skills else 0
    
    readiness_score = round(required_score + preferred_score, 1)
    
    # Calculate skill gap percentage
    total_role_skills = len(required_skills) + len(preferred_skills)
    total_missing = len(missing_required) + len(missing_preferred)
    skill_gap_percentage = round((total_missing / total_role_skills * 100), 1) if total_role_skills else 0
    
    # Generate personalized suggestions
    suggestions = generate_role_suggestions(
        role, missing_required, missing_preferred, readiness_score
    )
    
    # Determine readiness level
    readiness_level = get_readiness_level(readiness_score)
    
    return {
        'role': role,
        'readiness_score': readiness_score,
        'readiness_level': readiness_level,
        'skill_gap_percentage': skill_gap_percentage,
        'required_skills': {
            'total': len(required_skills),
            'matched': matched_required,
            'missing': missing_required,
            'match_percentage': round(len(matched_required) / len(required_skills) * 100, 1) if required_skills else 0
        },
        'preferred_skills': {
            'total': len(preferred_skills),
            'matched': matched_preferred,
            'missing': missing_preferred,
            'match_percentage': round(len(matched_preferred) / len(preferred_skills) * 100, 1) if preferred_skills else 0
        },
        'suggestions': suggestions,
        'top_priority_skills': missing_required[:5],  # Most important skills to learn
        'nice_to_have_skills': missing_preferred[:5]
    }


def get_readiness_level(score):
    """
    Determine readiness level based on score
    
    Args:
        score (float): Readiness score (0-100)
        
    Returns:
        str: Readiness level description
    """
    if score >= 80:
        return 'Excellent - Highly qualified for this role'
    elif score >= 60:
        return 'Good - Qualified with some skill gaps'
    elif score >= 40:
        return 'Fair - Developing skills needed'
    else:
        return 'Beginner - Significant upskilling required'


def generate_role_suggestions(role, missing_required, missing_preferred, readiness_score):
    """
    Generate actionable suggestions for skill improvement
    
    Args:
        role (str): Target role
        missing_required (list): Missing required skills
        missing_preferred (list): Missing preferred skills
        readiness_score (float): Overall readiness score
        
    Returns:
        list: List of prioritized suggestions
    """
    suggestions = []
    
    # Overall assessment
    if readiness_score >= 80:
        suggestions.append(f"You're well-prepared for {role} positions!")
        suggestions.append("Focus on building projects that showcase your existing skills.")
    elif readiness_score >= 60:
        suggestions.append(f"You have a solid foundation for {role} but need to fill some skill gaps.")
    else:
        suggestions.append(f"Consider focused learning to meet {role} requirements.")
    
    # Required skills suggestions
    if missing_required:
        if len(missing_required) <= 3:
            suggestions.append(f"PRIORITY: Learn these essential skills: {', '.join(missing_required)}")
        else:
            top_3 = missing_required[:3]
            suggestions.append(f"PRIORITY: Start with these critical skills: {', '.join(top_3)}")
            suggestions.append(f"Then focus on: {', '.join(missing_required[3:5])}")
        
        suggestions.append("Add projects demonstrating these skills to your resume.")
        suggestions.append("Consider online courses or certifications in missing required skills.")
    
    # Preferred skills suggestions
    if missing_preferred and readiness_score < 90:
        top_preferred = missing_preferred[:3]
        suggestions.append(f"To stand out, consider learning: {', '.join(top_preferred)}")
    
    # Role-specific advice
    role_specific_tips = {
        'Data Scientist': "Build end-to-end data science projects and publish findings.",
        'Web Developer': "Create portfolio websites showcasing responsive design and modern frameworks.",
        'AI Engineer': "Contribute to open-source ML projects or publish research papers.",
        'Backend Developer': "Build scalable APIs and microservices - showcase on GitHub.",
        'Frontend Developer': "Create interactive UIs with great user experience - deploy live demos.",
        'Full Stack Developer': "Build full-stack applications from scratch and deploy them.",
        'DevOps Engineer': "Automate deployments and infrastructure - document your CI/CD pipelines.",
        'Mobile Developer': "Publish apps on App Store/Play Store to demonstrate real-world experience."
    }
    
    if role in role_specific_tips:
        suggestions.append(role_specific_tips[role])
    
    # General recommendations
    if readiness_score < 70:
        suggestions.append("Update your resume to highlight relevant projects and experience.")
        suggestions.append("Network with professionals in the field through LinkedIn and communities.")
    
    return suggestions


def compare_multiple_roles(resume_skills, roles=None):
    """
    Compare resume against multiple roles to find best fit
    
    Args:
        resume_skills (list): Skills from resume
        roles (list, optional): List of roles to compare. If None, compare all.
        
    Returns:
        list: Sorted list of role analyses by readiness score
    """
    role_mapping = get_role_skill_mapping()
    
    if roles is None:
        roles = list(role_mapping.keys())
    
    results = []
    
    for role in roles:
        if role in role_mapping:
            analysis = role_skill_recommendation(resume_skills, role)
            results.append(analysis)
    
    # Sort by readiness score (highest first)
    results.sort(key=lambda x: x['readiness_score'], reverse=True)
    
    return results


def get_available_roles():
    """
    Get list of all available roles in the system
    
    Returns:
        list: Available job roles
    """
    return list(get_role_skill_mapping().keys())


# Example usage
if __name__ == "__main__":
    # Test the module
    sample_skills = [
        'Python', 'JavaScript', 'React', 'SQL', 'Git',
        'Machine Learning', 'Pandas', 'NumPy', 'Data Visualization'
    ]
    
    # Test for Data Scientist role
    print("=== Role-Based Skill Analysis ===\n")
    result = role_skill_recommendation(sample_skills, 'Data Scientist')
    
    print(f"Role: {result['role']}")
    print(f"Readiness Score: {result['readiness_score']}%")
    print(f"Readiness Level: {result['readiness_level']}")
    print(f"\nMissing Required Skills: {result['required_skills']['missing']}")
    print(f"\nTop Priority Skills: {result['top_priority_skills']}")
    print(f"\nSuggestions:")
    for i, suggestion in enumerate(result['suggestions'], 1):
        print(f"{i}. {suggestion}")
    
    # Compare across multiple roles
    print("\n\n=== Best Role Matches ===\n")
    all_results = compare_multiple_roles(sample_skills)
    
    for i, role_result in enumerate(all_results[:3], 1):
        print(f"{i}. {role_result['role']}: {role_result['readiness_score']}% - {role_result['readiness_level']}")
