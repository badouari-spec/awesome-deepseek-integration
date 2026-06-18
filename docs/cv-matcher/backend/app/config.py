import os
import sys
from dotenv import load_dotenv, find_dotenv

# ── Frozen / dev path resolution ─────────────────────────────────────────────
if getattr(sys, "frozen", False):
    _DATA_DIR = os.path.dirname(sys.executable)
    _env = os.path.join(_DATA_DIR, ".env")
    if os.path.exists(_env):
        load_dotenv(_env, override=True)
else:
    _DATA_DIR = os.getcwd()
    _dot = find_dotenv(usecwd=True)
    if _dot:
        load_dotenv(_dot, override=True)
    else:
        load_dotenv()

# ── Provider (default : Ollama 100% local) ───────────────────────────────────
# Pour utiliser Ollama : ollama pull gemma3:4b  puis lancer Ollama
# Pour utiliser le cloud : AI_PROVIDER=groq  API_KEY=gsk_...  API_BASE_URL=https://api.groq.com/openai/v1

AI_PROVIDER     = os.getenv("AI_PROVIDER",     "ollama")
API_KEY         = os.getenv("API_KEY",         "ollama")     # Ollama n'a pas besoin de clé
API_BASE_URL    = os.getenv("API_BASE_URL",    "http://localhost:11434/v1")
AI_MODEL        = os.getenv("AI_MODEL",        "gemma3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Legacy aliases
DEEPSEEK_API_KEY  = API_KEY
DEEPSEEK_MODEL    = AI_MODEL
DEEPSEEK_BASE_URL = API_BASE_URL

# ── Stockage ──────────────────────────────────────────────────────────────────
UPLOAD_DIR   = os.getenv("UPLOAD_DIR",   os.path.join(_DATA_DIR, "uploads"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_DATA_DIR, 'cv_matcher.db')}")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 Mo
ALLOWED_EXTENSIONS: set = set()   # géré par document_parser.SUPPORTED_EXTENSIONS
