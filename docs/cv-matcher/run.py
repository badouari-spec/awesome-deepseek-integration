"""
DeepSeek CV Matcher — simple launcher
Usage: double-click start.bat  (or: python run.py)
"""
import subprocess, sys, os, threading, time, webbrowser

ROOT_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
PORT        = 8000

PACKAGES = [
    "fastapi==0.110.1",
    "uvicorn[standard]==0.29.0",
    "python-multipart==0.0.9",
    "sqlalchemy==2.0.29",
    "pdfplumber==0.11.0",
    "python-docx==1.1.2",
    "openai==1.23.6",
    "python-dotenv==1.0.1",
    "aiofiles==23.2.1",
]


def _install_once():
    marker = os.path.join(ROOT_DIR, ".installed")
    if os.path.exists(marker):
        return
    print("┌─────────────────────────────────────────┐")
    print("│  First launch — installing dependencies │")
    print("│  (this takes ~1 minute, only once)      │")
    print("└─────────────────────────────────────────┘\n")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet"] + PACKAGES
    )
    open(marker, "w").close()
    print("\n✓ Done.\n")


def _ask_api_key():
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        return
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  DeepSeek API key not found.")
    print("  Get one free at: https://platform.deepseek.com")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    key = input("  Paste your API key (starts with sk-): ").strip()
    with open(env_path, "w") as f:
        f.write(f"DEEPSEEK_API_KEY={key}\n")
        f.write("DEEPSEEK_MODEL=deepseek-chat\n")
    print("\n✓ Key saved to .env\n")


def main():
    print("\n  🎯  DeepSeek CV Matcher\n")

    _install_once()
    _ask_api_key()

    # Add backend to path for `from app.xxx import ...`
    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    os.chdir(BACKEND_DIR)

    import uvicorn
    from app.main import app

    print(f"  Server → http://localhost:{PORT}")
    print("  Browser will open automatically.")
    print("  Press Ctrl+C to stop.\n")

    # Open browser after the server is up
    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open(f"http://localhost:{PORT}")),
        daemon=True,
    ).start()

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
