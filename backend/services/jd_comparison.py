"""
Job Description Comparison Module
Compares resume with job description using TF-IDF and cosine similarity
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def compare_with_jd(resume_text, jd_text, skill_list):
    """
    Compare resume text with job description and identify missing skills
    
    Args:
        resume_text (str): Extracted text from resume
        jd_text (str): Job description text provided by user
        skill_list (list): List of skills extracted from resume
        
    Returns:
        dict: JD match score, missing skills, and suggestions
    """
    # Preprocess texts
    resume_clean = preprocess_text(resume_text)
    jd_clean = preprocess_text(jd_text)
    
    # Calculate TF-IDF similarity
    match_score = calculate_tfidf_similarity(resume_clean, jd_clean)
    
    # Extract skills from JD
    jd_skills = extract_skills_from_jd(jd_text)
    
    # Find missing skills (skills in JD but not in resume)
    resume_skills_lower = [skill.lower() for skill in skill_list]
    missing_skills = [
        skill for skill in jd_skills 
        if skill.lower() not in resume_skills_lower
    ]
    
    # Generate suggestions
    suggestions = generate_jd_suggestions(match_score, missing_skills)
    
    return {
        'jd_match_score': round(match_score, 2),
        'missing_skills': missing_skills,
        'matched_skills': [s for s in jd_skills if s.lower() in resume_skills_lower],
        'suggestions': suggestions,
        'total_jd_skills': len(jd_skills),
        'matched_count': len(jd_skills) - len(missing_skills)
    }


def preprocess_text(text):
    """
    Clean and preprocess text for TF-IDF vectorization
    
    Args:
        text (str): Raw text
        
    Returns:
        str: Cleaned text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    return text


def calculate_tfidf_similarity(text1, text2):
    """
    Calculate cosine similarity between two texts using TF-IDF
    
    Args:
        text1 (str): First text (resume)
        text2 (str): Second text (job description)
        
    Returns:
        float: Similarity score as percentage (0-100)
    """
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # Use unigrams and bigrams
            stop_words='english'
        )
        
        # Transform texts to TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        return similarity * 100
        
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


def extract_skills_from_jd(jd_text):
    """
    Extract technical skills from job description
    Uses predefined skill dataset for matching
    
    Args:
        jd_text (str): Job description text
        
    Returns:
        list: List of skills found in JD
    """
    # Comprehensive skill dataset (technical skills commonly found in JDs)
    skill_dataset = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'TypeScript', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
        
        # Web Technologies
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
        'Django', 'Flask', 'FastAPI', 'Spring Boot', 'ASP.NET', 'jQuery',
        'Bootstrap', 'Tailwind CSS', 'Next.js', 'Nuxt.js', 'Redux',
        
        # Databases
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis', 'Cassandra',
        'DynamoDB', 'SQLite', 'MS SQL Server', 'MariaDB', 'Neo4j', 'Elasticsearch',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
        'CI/CD', 'Terraform', 'Ansible', 'Git', 'GitHub', 'GitLab', 'Bitbucket',
        'Linux', 'Unix', 'Shell Scripting', 'Bash', 'CloudFormation',
        
        # Data Science & ML
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
        'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'NLP',
        'Computer Vision', 'Neural Networks', 'Data Analysis', 'Statistics',
        'Data Visualization', 'Power BI', 'Tableau', 'Apache Spark', 'Hadoop',
        
        # Mobile Development
        'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin',
        
        # APIs & Architecture
        'REST API', 'RESTful', 'GraphQL', 'Microservices', 'API Development',
        'System Design', 'Software Architecture', 'Design Patterns',
        
        # Testing & Quality
        'Unit Testing', 'Integration Testing', 'Jest', 'Pytest', 'Selenium',
        'JUnit', 'Test Automation', 'QA', 'Quality Assurance',
        
        # Project Management & Methodologies
        'Agile', 'Scrum', 'JIRA', 'Kanban', 'Waterfall', 'CI/CD',
        
        # Other Technical Skills
        'Data Structures', 'Algorithms', 'OOP', 'Object-Oriented Programming',
        'Functional Programming', 'Version Control', 'Debugging', 'Performance Optimization'
    ]
    
    jd_lower = jd_text.lower()
    found_skills = []
    
    for skill in skill_dataset:
        # Check if skill appears in JD (case-insensitive)
        if skill.lower() in jd_lower:
            found_skills.append(skill)
    
    # Remove duplicates and return
    return list(set(found_skills))


def generate_jd_suggestions(match_score, missing_skills):
    """
    Generate actionable suggestions based on JD comparison
    
    Args:
        match_score (float): JD match percentage
        missing_skills (list): List of missing skills
        
    Returns:
        list: List of suggestion strings
    """
    suggestions = []
    
    # Score-based suggestions
    if match_score < 50:
        suggestions.append("Your resume has low alignment with the JD. Consider tailoring it more closely to the job requirements.")
    elif match_score < 70:
        suggestions.append("Moderate match with JD. Highlight relevant experience and add missing skills.")
    else:
        suggestions.append("Good match with JD! Make sure to emphasize your relevant achievements.")
    
    # Missing skills suggestions
    if missing_skills:
        if len(missing_skills) <= 3:
            suggestions.append(f"Add these important skills: {', '.join(missing_skills)}")
        else:
            top_missing = missing_skills[:3]
            suggestions.append(f"Focus on adding these key skills: {', '.join(top_missing)}")
        
        suggestions.append("Consider adding projects or experience demonstrating these missing skills.")
    
    # General recommendations
    suggestions.append("Use keywords from the JD naturally throughout your resume.")
    suggestions.append("Quantify your achievements with metrics that align with JD requirements.")
    
    return suggestions


# Example usage
if __name__ == "__main__":
    # Test the module
    sample_resume = """
    Software Engineer with 3 years experience in Python, JavaScript, and React.
    Built web applications using Django and Node.js. Experience with MySQL and Git.
    """
    
    sample_jd = """
    We are looking for a Full Stack Developer with experience in:
    - Python, JavaScript, React, Node.js
    - AWS, Docker, Kubernetes
    - REST API development
    - MySQL or PostgreSQL
    - Agile methodologies
    """
    
    resume_skills = ['Python', 'JavaScript', 'React', 'Django', 'Node.js', 'MySQL', 'Git']
    
    result = compare_with_jd(sample_resume, sample_jd, resume_skills)
    print("JD Comparison Result:")
    print(f"Match Score: {result['jd_match_score']}%")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Suggestions: {result['suggestions']}")
