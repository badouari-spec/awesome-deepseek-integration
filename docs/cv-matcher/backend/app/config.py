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

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(_DATA_DIR, "uploads"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_DATA_DIR, 'cv_matcher.db')}")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
