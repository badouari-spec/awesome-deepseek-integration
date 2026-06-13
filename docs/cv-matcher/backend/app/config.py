import os
import sys
from dotenv import load_dotenv, find_dotenv

if getattr(sys, "frozen", False):
    # Running as .exe — data lives next to the executable
    _DATA_DIR = os.path.dirname(sys.executable)
    _env = os.path.join(_DATA_DIR, ".env")
    if os.path.exists(_env):
        load_dotenv(_env, override=True)
else:
    # Dev or run.py launcher: search upward from cwd for .env
    _dot = find_dotenv(usecwd=True)
    if _dot:
        load_dotenv(_dot, override=True)
    else:
        load_dotenv()
    # Writable data goes in cwd (backend/ when launched via run.py)
    _DATA_DIR = os.getcwd()

# ── Provider-agnostic settings ───────────────────────────────────────────────
# Groq   → API_KEY=gsk_...  API_BASE_URL=https://api.groq.com/openai/v1  AI_MODEL=llama-3.3-70b-versatile
# DeepSeek → API_KEY=sk-... API_BASE_URL=https://api.deepseek.com        AI_MODEL=deepseek-chat
# Any OpenAI-compatible provider works the same way.

API_KEY      = os.getenv("API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
AI_MODEL     = os.getenv("AI_MODEL") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Legacy aliases (kept for backward compat)
DEEPSEEK_API_KEY  = API_KEY
DEEPSEEK_MODEL    = AI_MODEL
DEEPSEEK_BASE_URL = API_BASE_URL
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(_DATA_DIR, "uploads"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_DATA_DIR, 'cv_matcher.db')}")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
