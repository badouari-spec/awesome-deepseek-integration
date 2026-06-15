"""
CV Matcher — Lanceur simple (sans compilation EXE)
Double-cliquez sur start.bat pour lancer.
"""
import subprocess, sys, os, threading, time, webbrowser, json, urllib.request

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
    "striprtf==0.0.26",
    "beautifulsoup4==4.12.3",
    "odfpy==1.4.1",
    "openpyxl==3.1.2",
    "python-pptx==1.0.2",
    "Pillow==10.3.0",
    "openai==1.23.6",
    "python-dotenv==1.0.1",
    "aiofiles==23.2.1",
]

OLLAMA_URL = "http://localhost:11434"
_PROVIDERS = {
    "2": ("Groq (gratuit, cloud)",    "https://console.groq.com/keys",     "https://api.groq.com/openai/v1",  "llama-3.3-70b-versatile"),
    "3": ("DeepSeek",                  "https://platform.deepseek.com",      "https://api.deepseek.com",        "deepseek-chat"),
    "4": ("OpenAI",                    "https://platform.openai.com/api-keys","https://api.openai.com/v1",      "gpt-4o"),
}


def _ollama_models():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return []


def _install_once():
    marker = os.path.join(ROOT_DIR, ".installed")
    if os.path.exists(marker):
        return
    print("┌──────────────────────────────────────────┐")
    print("│  1er lancement — installation des outils │")
    print("│  (~2 minutes, une seule fois)             │")
    print("└──────────────────────────────────────────┘\n")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + PACKAGES)
    open(marker, "w").close()
    print("✓ Installation terminée.\n")


def _configure():
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  CV Matcher — Configuration initiale")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    print("  Choisissez votre moteur IA :\n")
    print("  1. Ollama — IA 100% locale (recommandé)")
    print("     → Gratuit, privé, hors ligne (Gemma, LLaMA, Mistral…)")
    for k, (name, url, _, _) in _PROVIDERS.items():
        print(f"  {k}. {name} — API cloud")
    print()

    choice = input("  Votre choix [1] : ").strip() or "1"

    if choice == "1":
        models = _ollama_models()
        if not models:
            print("\n  ⚠  Ollama n'est pas détecté ou aucun modèle n'est installé.")
            print("     Installez Ollama : https://ollama.com")
            print("     Puis dans un terminal : ollama pull gemma3:4b\n")
            model = input("  Nom du modèle à utiliser [gemma3:4b] : ").strip() or "gemma3:4b"
        else:
            print(f"\n  Modèles disponibles : {', '.join(models)}")
            model = input(f"  Modèle à utiliser [{models[0]}] : ").strip() or models[0]

        with open(env_path, "w", encoding="utf-8") as f:
            f.write("AI_PROVIDER=ollama\n")
            f.write("API_KEY=ollama\n")
            f.write("API_BASE_URL=http://localhost:11434/v1\n")
            f.write(f"AI_MODEL={model}\n")
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
        print(f"\n✓ Mode local configuré — modèle : {model}\n")

    elif choice in _PROVIDERS:
        name, url, base_url, default_model = _PROVIDERS[choice]
        print(f"\n  Obtenez votre clé API sur : {url}")
        key = input("  Collez votre clé API : ").strip()
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"AI_PROVIDER=cloud\n")
            f.write(f"API_KEY={key}\n")
            f.write(f"API_BASE_URL={base_url}\n")
            f.write(f"AI_MODEL={default_model}\n")
        print(f"\n✓ Mode cloud configuré ({name})\n")
    else:
        print("Choix invalide — mode Ollama par défaut.\n")
        _configure()


def main():
    print("\n  🎯  CV Matcher — Matching de CV par IA\n")
    _install_once()
    _configure()

    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    os.chdir(BACKEND_DIR)

    import uvicorn
    from app.main import app

    print(f"  Serveur démarré sur : http://localhost:{PORT}")
    print("  Le navigateur s'ouvrira automatiquement.")
    print("  Appuyez sur Ctrl+C pour arrêter.\n")

    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open(f"http://localhost:{PORT}")),
        daemon=True,
    ).start()

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
