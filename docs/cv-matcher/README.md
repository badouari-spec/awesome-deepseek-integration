# DeepSeek CV Matcher

> AI-powered CV/Resume matching engine — upload resumes, define job descriptions, and let DeepSeek rank and analyse candidates with detailed reports.

---

## Features

- **Intelligent Parsing** — Extract structured data from PDF, DOCX, and TXT files using DeepSeek. No regex hacks: real semantic understanding of experience, skills, education, and achievements.
- **Job Description Analysis** — Automatically identify required vs. preferred skills, experience levels, and cultural signals from free-text job descriptions.
- **Multi-dimensional Scoring** — Each candidate is scored across four dimensions (weights are configurable):
  | Dimension | Weight |
  |-----------|--------|
  | Technical Skills | 35% |
  | Work Experience | 30% |
  | Cultural Fit | 20% |
  | Education | 15% |
- **Ranked Candidate List** — Candidates are sorted by overall match score with a clear recommendation label (Strong Match → Poor Match).
- **Detailed Reports** — For every CV × Job pair: matched / missing skills, strengths, concerns, per-dimension analysis, suggested interview questions, and onboarding notes.
- **Async Processing** — Uploads and parsing run in the background so the UI stays responsive; status is polled automatically.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                      Browser (SPA)                     │
│  Vanilla JS · No build step · CSS custom properties    │
└────────────────────────┬───────────────────────────────┘
                         │ REST (JSON)
┌────────────────────────▼───────────────────────────────┐
│               FastAPI Backend (Python 3.11)            │
│                                                        │
│  /api/cv        — upload, list, get, delete            │
│  /api/jobs      — CRUD for job descriptions            │
│  /api/matching  — run matching, get ranked results     │
│                                                        │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ DocumentParser│  │  AIService  │  │  MatchEngine │  │
│  │ PDF/DOCX/TXT │  │ DeepSeek API│  │  Score+Report│  │
│  └──────────────┘  └─────────────┘  └──────────────┘  │
│                                                        │
│  SQLite (SQLAlchemy)     •     Local file storage      │
└────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- A [DeepSeek API key](https://platform.deepseek.com)

### 2. Clone & configure

```bash
cd docs/cv-matcher
cp .env.example .env
# Edit .env and set DEEPSEEK_API_KEY=sk-...
```

### 3. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

### 4. Run manually (development)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Usage

1. **Upload CVs** — Go to *Resumes / CVs*, drag-and-drop PDF/DOCX files. DeepSeek parses them automatically in the background.
2. **Create a Job** — Go to *Job Descriptions*, paste a job posting, click *Create & Parse*. DeepSeek extracts requirements.
3. **Run Matching** — Go to *Run Matching*, select a job and the candidates you want to evaluate, click *Run AI Matching*.
4. **View Reports** — Click *Report* next to any ranked candidate for the full analysis: scores, skill gaps, strengths, interview questions, and onboarding notes.

---

## API Reference

Interactive docs available at `/api/docs` (Swagger UI) once the server is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cv/upload` | Upload a CV file |
| `GET`  | `/api/cv/` | List all CVs |
| `GET`  | `/api/cv/{id}` | Get CV + parsed data |
| `DELETE` | `/api/cv/{id}` | Delete a CV |
| `POST` | `/api/jobs/` | Create a job description |
| `GET`  | `/api/jobs/` | List all jobs |
| `POST` | `/api/matching/run` | Trigger matching (async) |
| `GET`  | `/api/matching/job/{job_id}` | Get ranked results for a job |
| `GET`  | `/api/matching/{id}` | Get a single match report |

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | — | **Required.** Your DeepSeek API key |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Model to use (`deepseek-chat` or `deepseek-reasoner`) |
| `DATABASE_URL` | `sqlite:///./cv_matcher.db` | SQLAlchemy connection string |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |

---

## Project Structure

```
cv-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS + static files
│   │   ├── config.py            # Environment config
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── db_models.py     # ORM models (CV, Job, Match)
│   │   │   └── schemas.py       # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── document_parser.py   # PDF / DOCX / TXT extraction
│   │   │   └── ai_service.py        # DeepSeek prompts & calls
│   │   └── routers/
│   │       ├── cv_router.py
│   │       ├── job_router.py
│   │       └── match_router.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # SPA shell
│   ├── css/app.css
│   └── js/
│       ├── api.js               # Thin fetch wrapper
│       ├── components.js        # UI helpers (cards, reports, toasts)
│       └── main.js              # App logic & routing
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## DeepSeek Integration Details

Three carefully engineered prompts drive all AI features:

| Prompt | Purpose | Output |
|--------|---------|--------|
| `_CV_PROMPT` | Extract structured data from a raw CV | JSON with name, skills, experience, education, projects… |
| `_JD_PROMPT` | Parse a job description into requirements | JSON with required/preferred skills, experience levels, culture indicators |
| `_MATCH_PROMPT` | Score a candidate against a job | JSON with scores, skill gaps, strengths, concerns, interview questions |

All prompts request `response_format: json_object` for deterministic, parseable output.

---

## License

MIT
