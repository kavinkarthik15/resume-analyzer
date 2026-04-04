import json
import os
import re
from collections import Counter

# ── Expanded Skill Dataset ──────────────────────────────────────────────────────
SKILL_DATABASE = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "c", "javascript", "typescript",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "matlab", "perl", "lua", "dart", "haskell", "objective-c",
        "visual basic", "assembly", "fortran", "cobol", "groovy",
        "elixir", "clojure", "julia",
    ],
    "Web Development": [
        "html", "css", "react", "angular", "vue", "svelte", "nextjs",
        "nuxtjs", "gatsby", "tailwind css", "bootstrap", "sass", "less",
        "webpack", "vite", "jquery", "redux", "graphql", "rest api",
        "websocket", "pwa", "web components",
    ],
    "Backend & APIs": [
        "nodejs", "express", "django", "flask", "fastapi", "spring boot",
        "rails", "laravel", "asp.net", "nestjs", "gin", "fiber",
        "microservices", "grpc", "soap",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis",
        "elasticsearch", "cassandra", "dynamodb", "firebase",
        "oracle", "mariadb", "neo4j", "couchdb", "influxdb",
    ],
    "AI & Machine Learning": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "nlp", "natural language processing",
        "computer vision", "opencv", "neural networks",
        "reinforcement learning", "generative ai", "llm",
        "transformers", "hugging face", "langchain",
        "stable diffusion", "gpt", "bert", "yolo",
    ],
    "Data Science & Analytics": [
        "pandas", "numpy", "matplotlib", "seaborn", "scipy",
        "data analysis", "data visualization", "data mining",
        "statistical analysis", "jupyter", "r studio",
        "data wrangling", "feature engineering", "a/b testing",
        "excel", "power bi", "tableau", "looker", "qlik",
        "apache spark", "hadoop", "airflow", "etl",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "github actions",
        "gitlab ci", "circleci", "heroku", "vercel", "netlify",
        "cloudflare", "nginx", "apache", "linux", "bash",
        "shell scripting", "prometheus", "grafana",
    ],
    "Mobile Development": [
        "react native", "flutter", "swift", "kotlin", "android",
        "ios", "xamarin", "ionic", "cordova", "swiftui",
        "jetpack compose",
    ],
    "Cybersecurity": [
        "penetration testing", "ethical hacking", "owasp",
        "network security", "cryptography", "siem", "firewall",
        "vulnerability assessment", "soc", "incident response",
        "malware analysis", "burp suite", "nmap", "wireshark",
        "metasploit",
    ],
    "Version Control & Collaboration": [
        "git", "github", "gitlab", "bitbucket", "svn",
        "jira", "confluence", "trello", "slack", "agile",
        "scrum", "kanban",
    ],
    "Testing & QA": [
        "unit testing", "integration testing", "selenium",
        "cypress", "jest", "mocha", "pytest", "junit",
        "test driven development", "tdd", "bdd",
        "postman", "load testing", "qa automation",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "project management",
        "presentation", "negotiation", "mentoring",
        "adaptability", "creativity",
    ],
}

# Flat list of all skills
SKILLS = []
for _category_skills in SKILL_DATABASE.values():
    SKILLS.extend(_category_skills)

# Category mapping (skill -> category)
SKILL_TO_CATEGORY = {}
for _cat, _skills in SKILL_DATABASE.items():
    for _s in _skills:
        SKILL_TO_CATEGORY[_s] = _cat


def _count_skill_occurrences(text: str, skill: str) -> int:
    """Count how many times a skill appears in text using word boundaries."""
    escaped = re.escape(skill)

    if " " in skill:
        pattern = rf"\b{escaped}\b"
    elif "+" in skill:
        pattern = escaped
    elif "/" in skill:
        pattern = escaped
    else:
        pattern = rf"\b{escaped}\b"

    return len(re.findall(pattern, text, re.IGNORECASE))


def extract_skills(text: str):
    """
    Detect skills, count frequency, and categorize them.

    Returns:
        skills_found (list[str])
        skill_categories (dict[str, list[str]])
        skill_frequency (dict[str, int])
        missing_skills (dict[str, list[str]])  — important skills not found, grouped by category
    """
    frequency_counter = Counter()
    text_lower = text.lower()

    for skill in SKILLS:
        count = _count_skill_occurrences(text_lower, skill)
        if count > 0:
            frequency_counter[skill] = count

    skills_found = sorted(frequency_counter.keys())

    # Build categorized found skills
    categorized = {}
    for category_name, category_skills in SKILL_DATABASE.items():
        matches = [skill for skill in category_skills if skill in frequency_counter]
        if matches:
            categorized[category_name] = matches

    # Build missing skills per category (only categories where user has at least 1 skill)
    missing_skills = {}
    for category_name, category_skills in SKILL_DATABASE.items():
        if category_name in ("Soft Skills",):
            continue  # skip soft skills for missing list
        found_in_cat = [s for s in category_skills if s in frequency_counter]
        missed_in_cat = [s for s in category_skills if s not in frequency_counter]
        # Only show missing if user has at least 1 skill in the category
        if found_in_cat and missed_in_cat:
            # Limit to top 5 missing per category to avoid overwhelming
            missing_skills[category_name] = missed_in_cat[:5]

    skill_frequency = dict(sorted(frequency_counter.items(), key=lambda item: (-item[1], item[0])))

    return skills_found, categorized, skill_frequency, missing_skills
