"""
Service IA — compatible Ollama (local) ET tout provider OpenAI-compatible.
Gère automatiquement les modèles qui ne supportent pas le mode JSON strict.
"""
import json
import os
import re
from openai import AsyncOpenAI
from ..config import API_KEY, AI_MODEL, API_BASE_URL

# Timeout élevé pour les modèles locaux (chargement initial ~30 s)
_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
    timeout=180.0,
    max_retries=0,
)

# ── Extraction JSON robuste ───────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Extrait du JSON depuis n'importe quel format de réponse du modèle."""
    text = text.strip()
    # 1) Parse direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 2) Blocs markdown ```json ... ```
    for pat in (r'```json\s*([\s\S]*?)```', r'```\s*([\s\S]*?)```'):
        m = re.search(pat, text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass
    # 3) Premier objet JSON dans le texte
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Impossible d'extraire du JSON de la réponse :\n{text[:400]}")


async def _chat(prompt: str) -> dict:
    """Appelle le modèle IA et retourne un dict JSON."""
    model = os.environ.get("AI_MODEL", AI_MODEL)
    kwargs = dict(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    try:
        resp = await _client.chat.completions.create(**kwargs)
        return _parse_json(resp.choices[0].message.content)
    except Exception as e:
        err = str(e).lower()
        # Certains modèles locaux ne supportent pas response_format → on réessaie sans
        if any(k in err for k in ("response_format", "json", "format", "unsupported")):
            del kwargs["response_format"]
            resp = await _client.chat.completions.create(**kwargs)
            return _parse_json(resp.choices[0].message.content)
        raise


# ── Prompts ──────────────────────────────────────────────────────────────────

_CV_PROMPT = """Tu es un expert en analyse de CV. Extrais toutes les informations du texte ci-dessous et retourne UNIQUEMENT du JSON valide avec cette structure exacte :
{
  "name": "Prénom Nom",
  "email": "email@exemple.com",
  "phone": "numéro ou null",
  "location": "Ville, Pays ou null",
  "linkedin": "url ou null",
  "github": "url ou null",
  "summary": "résumé professionnel ou null",
  "total_years_experience": 0,
  "skills": {
    "technical": [],
    "soft": [],
    "tools": [],
    "programming_languages": []
  },
  "experience": [
    {
      "company": "Entreprise",
      "title": "Poste",
      "start_date": "MM/AAAA",
      "end_date": "MM/AAAA ou Présent",
      "duration_months": 0,
      "location": "Ville ou null",
      "description": "description courte",
      "achievements": [],
      "technologies": []
    }
  ],
  "education": [
    {
      "institution": "École",
      "degree": "Bac+2/Licence/Master/Doctorat",
      "field": "Domaine",
      "start_year": 2018,
      "end_year": 2022,
      "gpa": "null ou 16/20",
      "honors": "null ou Mention Très Bien"
    }
  ],
  "certifications": [],
  "projects": [
    {
      "name": "Projet",
      "description": "description",
      "technologies": [],
      "url": "null ou url"
    }
  ],
  "spoken_languages": [
    {"language": "Français", "level": "Natif/Courant/Intermédiaire/Débutant"}
  ]
}

Retourne UNIQUEMENT du JSON valide, sans explication ni balise markdown.

TEXTE DU CV :
"""

_JD_PROMPT = """Tu es un expert en analyse d'offres d'emploi. Extrais toutes les informations de l'offre ci-dessous et retourne UNIQUEMENT du JSON valide avec cette structure exacte :
{
  "title": "Titre du poste",
  "company": "Entreprise ou null",
  "location": "Ville, Pays ou Télétravail",
  "employment_type": "CDI/CDD/Freelance/Stage/Alternance",
  "experience_required": {
    "min_years": 0,
    "max_years": null,
    "description": "ex : 3 à 5 ans d'expérience en développement backend"
  },
  "education_required": {
    "min_level": "Bac+2/Bac+3/Bac+5/Doctorat/Indifférent",
    "field": "Informatique ou Indifférent",
    "required": true
  },
  "required_skills": [
    {"skill": "Python", "importance": "critique", "years_required": null}
  ],
  "preferred_skills": [
    {"skill": "Docker", "importance": "souhaité"}
  ],
  "responsibilities": [],
  "benefits": [],
  "salary_range": "null ou 45000-55000€",
  "company_culture": [],
  "keywords": []
}

Retourne UNIQUEMENT du JSON valide, sans explication ni balise markdown.

OFFRE D'EMPLOI :
"""

_MATCH_PROMPT = """Tu es un expert RH et recruteur technique avec 20 ans d'expérience.
Analyse la compatibilité du candidat avec le poste et retourne UNIQUEMENT du JSON valide.

Structure JSON attendue :
{{
  "overall_score": 0,
  "scores": {{
    "skills": 0,
    "experience": 0,
    "education": 0,
    "culture_fit": 0
  }},
  "recommendation": "Excellent profil",
  "matched_skills": [],
  "missing_critical_skills": [],
  "missing_preferred_skills": [],
  "strengths": [
    {{"point": "Point fort", "explanation": "Pourquoi c'est un atout"}}
  ],
  "concerns": [
    {{"point": "Point faible", "explanation": "Pourquoi c'est une préoccupation"}}
  ],
  "experience_analysis": "Analyse détaillée de l'expérience",
  "skills_analysis": "Analyse détaillée des compétences",
  "education_analysis": "Analyse de la formation",
  "overall_analysis": "Analyse globale en 3-4 paragraphes",
  "interview_questions": [],
  "onboarding_notes": "Points à aborder lors de l'intégration"
}}

Règles de scoring :
- overall_score : moyenne pondérée (compétences 35% + expérience 30% + culture 20% + formation 15%)
- recommendation : "Excellent profil" (≥85), "Bon profil" (70-84), "Profil partiel" (50-69), "Profil faible" (30-49), "Non adapté" (<30)
- Tous les scores sont des entiers de 0 à 100

CV DU CANDIDAT :
{cv_data}

EXIGENCES DU POSTE :
{jd_data}

Retourne UNIQUEMENT du JSON valide, sans explication ni balise markdown."""


# ── API publique ──────────────────────────────────────────────────────────────

async def parse_cv(raw_text: str) -> dict:
    return await _chat(_CV_PROMPT + raw_text)


async def parse_job(description: str) -> dict:
    return await _chat(_JD_PROMPT + description)


async def match_cv_to_job(cv_data: dict, jd_data: dict) -> dict:
    prompt = _MATCH_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2, ensure_ascii=False),
        jd_data=json.dumps(jd_data, indent=2, ensure_ascii=False),
    )
    return await _chat(prompt)
