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


_PROVIDERS = {
    "1": {
        "name": "Groq (gratuit, très rapide)",
        "url": "https://console.groq.com/keys",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
    },
    "2": {
        "name": "DeepSeek",
        "url": "https://platform.deepseek.com",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "3": {
        "name": "OpenAI",
        "url": "https://platform.openai.com/api-keys",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
}


def _ask_api_key():
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        return
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Configuration initiale — choisissez votre fournisseur IA")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    for k, p in _PROVIDERS.items():
        print(f"  {k}. {p['name']}")
    print()
    choice = input("  Votre choix (1/2/3) [1 par défaut] : ").strip() or "1"
    provider = _PROVIDERS.get(choice, _PROVIDERS["1"])

    print(f"\n  Obtenez votre clé sur : {provider['url']}")
    key = input("  Collez votre clé API ici : ").strip()

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"API_KEY={key}\n")
        f.write(f"API_BASE_URL={provider['base_url']}\n")
        f.write(f"AI_MODEL={provider['model']}\n")
    print(f"\n✓ Clé sauvegardée ({provider['name']}, modèle : {provider['model']})\n")


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
