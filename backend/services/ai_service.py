import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4.1-mini"


def _build_prompt(role_data: Dict[str, Any]) -> str:
    return f"""
You are a hiring manager.

Create a professional job description for:

Role: {role_data.get('role', '').strip()}
Experience: {role_data.get('experience', '').strip()}
Work Type: {role_data.get('workType', '').strip()}
Location: {role_data.get('location', '').strip()}

Include:
- Job summary
- Key responsibilities
- Required skills
- Preferred qualifications

Keep it concise and realistic.
""".strip()


def _fallback_job_description(role_data: Dict[str, Any]) -> str:
    role = role_data.get("role", "the role")
    experience = role_data.get("experience", "the required experience")
    work_type = role_data.get("workType", "the specified work type")
    location = role_data.get("location", "the specified location")
    skills = role_data.get("skills", "relevant technical and soft skills")

    lines = [
        f"Job Title: {role}",
        "",
        f"Job Summary: We are looking for a {role.lower()} with {experience} experience to join our team in a {work_type or 'flexible'} setting based in {location or 'a suitable location'}.",
        "",
        "Key Responsibilities:",
        f"- Build and maintain high-quality solutions aligned to the {role.lower()} function.",
        "- Collaborate with cross-functional teams to deliver reliable outcomes.",
        "- Contribute to planning, execution, and continuous improvement.",
        "",
        "Required Skills:",
        f"- {skills}",
        "- Strong communication and problem-solving skills.",
        "- Ability to work independently and as part of a team.",
        "",
        "Preferred Qualifications:",
        f"- Experience in {role.lower()}-related projects or products.",
        "- Familiarity with modern tools, workflows, and best practices.",
    ]

    return "\n".join(lines).strip()


def generate_job_description(role_data: Dict[str, Any]) -> str:
    prompt = _build_prompt(role_data)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        return _fallback_job_description(role_data)

    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    request = urllib.request.Request(
        OPENAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return _fallback_job_description(role_data)

    choices = response_payload.get("choices", [])
    if not choices:
        return _fallback_job_description(role_data)

    message = choices[0].get("message", {})
    content = message.get("content", "").strip()
    return content or _fallback_job_description(role_data)