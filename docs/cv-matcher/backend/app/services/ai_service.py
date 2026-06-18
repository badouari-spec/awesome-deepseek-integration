"""
AI service — OpenAI-compatible (Ollama local / Groq / DeepSeek / OpenAI).
Enhanced: 6-dimension scoring, interview questions, onboarding plan, skills gap.
"""
import os, re, json
from openai import AsyncOpenAI
from ..config import API_KEY, API_BASE_URL, AI_MODEL

_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
    timeout=180.0,
    max_retries=0,
)

def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass
    t = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r'\{[\s\S]*\}', t)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}

async def _chat(prompt: str, system: str = "Expert RH senior. Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.") -> dict:
    model = os.environ.get("AI_MODEL", AI_MODEL)
    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.1,
        max_tokens=3500,
        response_format={"type": "json_object"},
    )
    try:
        resp = await _client.chat.completions.create(**kwargs)
        return _parse_json(resp.choices[0].message.content)
    except Exception as e:
        if any(k in str(e).lower() for k in ("response_format", "json", "format", "unsupported", "extra")):
            kwargs.pop("response_format", None)
            try:
                resp = await _client.chat.completions.create(**kwargs)
                return _parse_json(resp.choices[0].message.content)
            except Exception:
                pass
    return {}

_CV_PROMPT = """\
Analyse ce CV et retourne UNIQUEMENT ce JSON valide :
{"nom_candidat":"","titre_profil":"","email":"","telephone":"","localisation":"",
"resume_profil":"","annees_experience":0,
"competences_techniques":[],"competences_comportementales":[],
"formation_niveau":"","formation_domaine":"",
"certifications":[],"logiciels_outils":[],"langues":[],"secteurs_expertise":[],
"realisations_chiffrees":[],"disponibilite":"","pretentions_salariales":""}

CV :
%s"""

_JD_PROMPT = """\
Analyse cette fiche de poste et retourne UNIQUEMENT ce JSON valide :
{"intitule_poste":"","entreprise":"","secteur":"","localisation":"","type_contrat":"","salaire":"",
"competences_obligatoires":[],"competences_souhaitees":[],
"formation_requise":"","experience_min_annees":0,
"logiciels_requis":[],"certifications_requises":[],"langues_requises":[],
"responsabilites_cles":[],"criteres_eliminatoires":[],"valeurs_entreprise":[],
"resume_poste":""}

FICHE DE POSTE :
%s"""

_MATCH_PROMPT = """\
Évalue en profondeur la correspondance entre ce candidat et ce poste.
Génère des questions d'entretien personnalisées basées sur les écarts de compétences.

Retourne UNIQUEMENT ce JSON valide (scores de 0 à 100) :
{
  "score_global": 0,
  "recommendation": "PRIORITAIRE",
  "scores_detail": {
    "competences_techniques": 0,
    "experience_pertinente": 0,
    "formation": 0,
    "culture_fit": 0,
    "potentiel_evolution": 0,
    "communication_leadership": 0
  },
  "competences_matchees": [],
  "competences_manquantes": [],
  "competences_bonus": [],
  "points_forts": [],
  "risques": [],
  "trajectoire_carriere": "ASCENDANTE",
  "questions_entretien": [
    "Question 1 ?",
    "Question 2 ?",
    "Question 3 ?",
    "Question 4 ?",
    "Question 5 ?"
  ],
  "plan_integration": [
    {"periode": "Semaine 1-2", "focus": ""},
    {"periode": "Mois 1", "focus": ""},
    {"periode": "Mois 2-3", "focus": ""}
  ],
  "justification": ""
}

Pondération score_global : compétences_techniques=30%%, expérience_pertinente=20%%,
formation=15%%, culture_fit=15%%, potentiel_evolution=10%%, communication_leadership=10%%

recommendation doit être : PRIORITAIRE (≥85), FORT (70-84), MOYEN (55-69), FAIBLE (40-54), ÉLIMINATOIRE (<40)
trajectoire_carriere : ASCENDANTE | STABLE | RECONVERSION | LATERALE

CANDIDAT :
%s

POSTE :
%s"""

async def parse_cv(text: str) -> dict:
    return await _chat(_CV_PROMPT % text[:10000])

async def parse_job(text: str) -> dict:
    return await _chat(_JD_PROMPT % text[:6000])

async def match_cv_to_job(cv_data: dict, job_data: dict) -> dict:
    cv_json = json.dumps(cv_data,  ensure_ascii=False)[:4000]
    jd_json = json.dumps(job_data, ensure_ascii=False)[:4000]
    return await _chat(_MATCH_PROMPT % (cv_json, jd_json))
