import os
import sys
from dotenv import load_dotenv

# When running as a PyInstaller .exe, store writable data next to the executable.
if getattr(sys, "frozen", False):
    _DATA_DIR = os.path.dirname(sys.executable)
else:
    _DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# .env file lives next to the .exe (or in the project root during dev)
_env_path = os.path.join(_DATA_DIR, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)
else:
    load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(_DATA_DIR, "uploads"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_DATA_DIR, 'cv_matcher.db')}")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
