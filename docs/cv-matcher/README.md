# CV Matcher — Matching de CV par IA

> Logiciel de matching CV / fiche de poste alimenté par IA — uploadez des CVs, définissez des fiches de poste, et laissez l'IA classer et analyser les candidats. Fonctionne **100 % en local avec Ollama** (Gemma, LLaMA, Mistral…) ou via une API cloud (Groq, DeepSeek, OpenAI).

---

## Fonctionnalités

- **Parsing universel** — PDF, DOCX, DOC, ODT, RTF, HTML, XLSX, PPTX, EML, TXT, images (JPG/PNG via OCR). Extraction sémantique réelle via IA.
- **Analyse des fiches de poste** — Identification des compétences requises, niveau d'expérience, critères éliminatoires. Saisie texte ou upload fichier.
- **Scoring multi-dimensionnel** — Chaque candidat est évalué sur :

  | Dimension | Poids |
  |-----------|-------|
  | Compétences métier | 35 % |
  | Expérience | 25 % |
  | Diplôme | 15 % |
  | Mots-clés sectoriels | 10 % |
  | Outils / logiciels | 5 % |
  | Langues | 5 % |
  | Localisation | 5 % |

- **Classement des candidats** — Triés par score global avec label PRIORITAIRE / MOYEN / FAIBLE.
- **Rapports détaillés** — Points forts, réserves, critères éliminatoires touchés, justification IA.
- **Traitement asynchrone** — Upload et parsing en arrière-plan ; le statut se met à jour automatiquement.

---

## Mode local 100 % (recommandé)

Le logiciel tourne **entièrement sur votre PC** avec [Ollama](https://ollama.com) — aucune donnée ne quitte votre machine.

### Prérequis

1. **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/) (cocher *Add to PATH*)
2. **Ollama** — [ollama.com](https://ollama.com)
3. Un modèle IA installé :
   ```
   ollama pull gemma3:4b          # léger, recommandé
   ollama pull llama3.2           # Meta, rapide
   ollama pull mistral            # Mistral AI
   ```

### Démarrage (Windows)

Double-cliquez sur **`start.bat`** — les dépendances s'installent automatiquement au premier lancement, puis le navigateur s'ouvre sur `http://localhost:8000`.

### Démarrage (Mac / Linux)

```bash
cd docs/cv-matcher
python run.py
```

---

## Providers IA supportés

Le fichier `.env` (copié depuis `.env.example`) contrôle le moteur IA :

| Provider | Clé | Modèle conseillé |
|----------|-----|-----------------|
| **Ollama** (local, défaut) | `ollama` | `gemma3:4b`, `llama3.2`, `mistral` |
| Groq (cloud gratuit) | `gsk_…` | `llama-3.3-70b-versatile` |
| DeepSeek (cloud) | `sk-…` | `deepseek-chat` |
| OpenAI (cloud) | `sk-…` | `gpt-4o` |

Au premier lancement de `run.py`, un assistant interactif configure le bon provider.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                     Navigateur (SPA)                   │
│  Vanilla JS · Aucune compilation · CSS personnalisé    │
└────────────────────────┬───────────────────────────────┘
                         │ REST / JSON
┌────────────────────────▼───────────────────────────────┐
│              FastAPI Backend (Python 3.11)             │
│                                                        │
│  /api/cv       — upload, liste, détail, suppression    │
│  /api/jobs     — CRUD fiches de poste + upload fichier │
│  /api/matching — lancer le matching, résultats classés │
│                                                        │
│  ┌───────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │DocumentParser │  │  AIService  │  │ MatchEngine │  │
│  │20+ formats    │  │ Ollama/API  │  │ Score+Rapport│  │
│  └───────────────┘  └─────────────┘  └─────────────┘  │
│                                                        │
│  SQLite (SQLAlchemy)       •       Stockage fichiers   │
└────────────────────────────────────────────────────────┘
```

---

## Build .exe Windows (autonome)

Crée un exécutable qui tourne sans Python ni Docker sur la machine cible.

```bat
cd docs\cv-matcher\backend
build_windows.bat
```

**Résultat :**
```
dist\CVMatcher\
├── CVMatcher.exe     ← double-clic pour lancer
├── .env              ← configuration IA
├── uploads\          ← CVs uploadés
└── cv_matcher.db     ← base SQLite (créée automatiquement)
```

**Prérequis sur la machine cible :** Ollama installé + un modèle chargé. Aucune autre dépendance.

---

## Utilisation

1. **Uploader des CVs** — Onglet *CVs / Candidats*, glisser-déposer des fichiers PDF/DOCX/etc. L'IA parse en arrière-plan.
2. **Créer une fiche** — Onglet *Fiches de poste*, saisir le texte ou uploader un fichier (PDF, Word…).
3. **Lancer le matching** — Onglet *Matching*, sélectionner une fiche et les candidats, cliquer *Lancer*.
4. **Consulter les résultats** — Candidats classés par score, avec points forts, réserves et justification IA.

---

## API REST

Swagger interactif disponible sur `/api/docs` une fois le serveur lancé.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/cv/upload` | Uploader un CV |
| `GET`  | `/api/cv/` | Lister les CVs |
| `DELETE` | `/api/cv/{id}` | Supprimer un CV |
| `POST` | `/api/jobs/` | Créer une fiche (texte) |
| `POST` | `/api/jobs/upload` | Créer une fiche (fichier) |
| `GET`  | `/api/jobs/` | Lister les fiches |
| `POST` | `/api/matching/run` | Lancer le matching |
| `GET`  | `/api/matching/job/{job_id}` | Résultats classés |

---

## Configuration

| Variable | Défaut | Description |
|----------|--------|-------------|
| `AI_PROVIDER` | `ollama` | `ollama` / `groq` / `deepseek` / `cloud` |
| `API_KEY` | `ollama` | Clé API (laisser `ollama` pour le mode local) |
| `API_BASE_URL` | `http://localhost:11434/v1` | URL du provider OpenAI-compatible |
| `AI_MODEL` | `gemma3:4b` | Modèle à utiliser |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL Ollama (pour détection des modèles) |
| `DATABASE_URL` | `sqlite:///./cv_matcher.db` | Base de données |
| `UPLOAD_DIR` | `uploads` | Dossier des fichiers uploadés |

---

## Run avec Docker Compose

```bash
cd docs/cv-matcher
cp .env.example .env     # éditer si nécessaire
docker compose up --build
```

Accès sur [http://localhost:8000](http://localhost:8000)

---

## Structure du projet

```
cv-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI + CORS + fichiers statiques
│   │   ├── config.py            # Variables d'environnement
│   │   ├── database.py          # SQLAlchemy
│   │   ├── models/
│   │   │   ├── db_models.py     # Modèles ORM (CV, Job, Match)
│   │   │   └── schemas.py       # Schémas Pydantic
│   │   ├── services/
│   │   │   ├── document_parser.py   # 20+ formats de fichiers
│   │   │   └── ai_service.py        # Appels IA + parsing JSON robuste
│   │   └── routers/
│   │       ├── cv_router.py
│   │       ├── job_router.py
│   │       └── match_router.py
│   ├── requirements.txt
│   ├── launcher.py              # Interface tkinter (EXE)
│   ├── cv_matcher.spec          # PyInstaller
│   └── build_windows.bat        # Build .exe
├── frontend/
│   ├── index.html
│   ├── css/app.css
│   └── js/
│       ├── api.js               # Couche fetch
│       ├── components.js        # Composants UI
│       └── main.js              # Logique & routage
├── run.py                       # Lanceur simple (cross-platform)
├── start.bat                    # Lanceur Windows (double-clic)
├── docker-compose.yml
└── .env.example
```

---

## Licence

MIT
