import json
from openai import AsyncOpenAI
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_BASE_URL

_client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

_CV_PROMPT = """You are an expert CV/resume parser. Extract all information from the CV text below and return ONLY valid JSON with this exact structure:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number or null",
  "location": "City, Country or null",
  "linkedin": "url or null",
  "github": "url or null",
  "summary": "professional summary or null",
  "total_years_experience": 0,
  "skills": {
    "technical": [],
    "soft": [],
    "tools": [],
    "programming_languages": []
  },
  "experience": [
    {
      "company": "Company",
      "title": "Job Title",
      "start_date": "MM/YYYY",
      "end_date": "MM/YYYY or Present",
      "duration_months": 0,
      "location": "City or null",
      "description": "brief description",
      "achievements": [],
      "technologies": []
    }
  ],
  "education": [
    {
      "institution": "University",
      "degree": "Bachelor/Master/PhD",
      "field": "Field of Study",
      "start_year": 2018,
      "end_year": 2022,
      "gpa": "null or 3.8/4.0",
      "honors": "null or Summa Cum Laude"
    }
  ],
  "certifications": [],
  "projects": [
    {
      "name": "Project",
      "description": "description",
      "technologies": [],
      "url": "null or url"
    }
  ],
  "spoken_languages": [
    {"language": "English", "level": "Native/Fluent/Intermediate/Basic"}
  ]
}

Return ONLY valid JSON. No markdown, no explanation.

CV TEXT:
"""

_JD_PROMPT = """You are an expert job description parser. Extract all requirements from the job description below and return ONLY valid JSON with this exact structure:
{
  "title": "Job Title",
  "company": "Company Name or null",
  "location": "City, Country or Remote",
  "employment_type": "Full-time/Part-time/Contract/Remote",
  "experience_required": {
    "min_years": 0,
    "max_years": null,
    "description": "e.g. 3-5 years of backend development"
  },
  "education_required": {
    "min_level": "Bachelor/Master/PhD/Any",
    "field": "Computer Science or Any",
    "required": true
  },
  "required_skills": [
    {"skill": "Python", "importance": "critical", "years_required": null}
  ],
  "preferred_skills": [
    {"skill": "Docker", "importance": "nice-to-have"}
  ],
  "responsibilities": [],
  "benefits": [],
  "salary_range": "null or $80,000-$100,000",
  "company_culture": [],
  "keywords": []
}

Return ONLY valid JSON. No markdown, no explanation.

JOB DESCRIPTION:
"""

_MATCH_PROMPT = """You are a senior HR professional and technical recruiter with 20 years of experience.
Analyze how well the candidate matches the job requirements and return ONLY valid JSON.

Return exactly this JSON structure:
{{
  "overall_score": 0,
  "scores": {{
    "skills": 0,
    "experience": 0,
    "education": 0,
    "culture_fit": 0
  }},
  "recommendation": "Strong Match",
  "matched_skills": [],
  "missing_critical_skills": [],
  "missing_preferred_skills": [],
  "strengths": [
    {{"point": "Strength title", "explanation": "Why this matters"}}
  ],
  "concerns": [
    {{"point": "Concern title", "explanation": "Why this is a concern"}}
  ],
  "experience_analysis": "Detailed analysis of experience relevance",
  "skills_analysis": "Detailed analysis of skills match",
  "education_analysis": "Detailed analysis of education match",
  "overall_analysis": "3-4 paragraph comprehensive analysis",
  "interview_questions": [],
  "onboarding_notes": "Key things to address if hired"
}}

Rules:
- overall_score: weighted average (skills 35% + experience 30% + education 15% + culture 20%)
- recommendation: one of "Strong Match" (85+), "Good Match" (70-84), "Partial Match" (50-69), "Weak Match" (30-49), "Poor Match" (<30)
- All scores are 0-100 integers

CANDIDATE CV DATA:
{cv_data}

JOB REQUIREMENTS:
{jd_data}

Return ONLY valid JSON. No markdown, no explanation."""


async def parse_cv(raw_text: str) -> dict:
    response = await _client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": _CV_PROMPT + raw_text}],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=4096,
    )
    return json.loads(response.choices[0].message.content)


async def parse_job(description: str) -> dict:
    response = await _client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": _JD_PROMPT + description}],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=2048,
    )
    return json.loads(response.choices[0].message.content)


async def match_cv_to_job(cv_data: dict, jd_data: dict) -> dict:
    prompt = _MATCH_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2, ensure_ascii=False),
        jd_data=json.dumps(jd_data, indent=2, ensure_ascii=False),
    )
    response = await _client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=4096,
    )
    return json.loads(response.choices[0].message.content)
