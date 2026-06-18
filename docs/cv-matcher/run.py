"""
CV Matcher — Lanceur universel
  - Mode développement : python run.py  (configure + installe)
  - Mode EXE PyInstaller : lanceur direct (tout est embarqué)
"""
import subprocess, sys, os, threading, time, webbrowser, json, urllib.request

ROOT_DIR    = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
PORT        = 8000
OLLAMA_URL  = "http://localhost:11434"

PACKAGES = [
    "fastapi==0.110.1", "uvicorn[standard]==0.29.0", "python-multipart==0.0.9",
    "sqlalchemy==2.0.29", "pdfplumber==0.11.0", "python-docx==1.1.2",
    "striprtf==0.0.26", "beautifulsoup4==4.12.3", "odfpy==1.4.1",
    "openpyxl==3.1.2", "python-pptx==1.0.2", "Pillow==10.3.0",
    "openai==1.23.6", "python-dotenv==1.0.1", "aiofiles==23.2.1",
]

_PROVIDERS = {
    "2": ("Groq (gratuit, cloud)",  "https://console.groq.com/keys",      "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
    "3": ("DeepSeek",               "https://platform.deepseek.com",       "https://api.deepseek.com",       "deepseek-chat"),
    "4": ("OpenAI",                 "https://platform.openai.com/api-keys","https://api.openai.com/v1",      "gpt-4o"),
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


def _write_env(content: str):
    env_path = os.path.join(ROOT_DIR, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)


def _configure_cli():
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
        print(f"  {k}. {name}")
    print()

    choice = input("  Votre choix [1] : ").strip() or "1"

    if choice == "1":
        models = _ollama_models()
        if not models:
            print("\n  ⚠  Ollama non détecté. Installez-le sur https://ollama.com")
            print("     Puis : ollama pull gemma3:4b\n")
            model = input("  Modèle [gemma3:4b] : ").strip() or "gemma3:4b"
        else:
            print(f"\n  Modèles : {', '.join(models)}")
            model = input(f"  Modèle [{models[0]}] : ").strip() or models[0]
        _write_env(
            f"AI_PROVIDER=ollama\nAPI_KEY=ollama\n"
            f"API_BASE_URL={OLLAMA_URL}/v1\nAI_MODEL={model}\n"
            f"OLLAMA_BASE_URL={OLLAMA_URL}\n"
        )
        print(f"\n✓ Mode local — modèle : {model}\n")

    elif choice in _PROVIDERS:
        name, url, base_url, default_model = _PROVIDERS[choice]
        print(f"\n  Obtenez votre clé sur : {url}")
        key = input("  Clé API : ").strip()
        _write_env(
            f"AI_PROVIDER=cloud\nAPI_KEY={key}\n"
            f"API_BASE_URL={base_url}\nAI_MODEL={default_model}\n"
        )
        print(f"\n✓ Mode cloud ({name})\n")
    else:
        print("Choix invalide — mode Ollama par défaut.\n")
        _configure_cli()


def _configure_gui():
    """Tkinter config dialog used in frozen (EXE) mode when .env is missing."""
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        return
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        _write_env(
            f"AI_PROVIDER=ollama\nAPI_KEY=ollama\n"
            f"API_BASE_URL={OLLAMA_URL}/v1\nAI_MODEL=gemma3:4b\n"
            f"OLLAMA_BASE_URL={OLLAMA_URL}\n"
        )
        return

    root = tk.Tk()
    root.title("CV Matcher — Configuration")
    root.geometry("520x400")
    root.resizable(False, False)
    root.configure(bg="#0f1117")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background="#0f1117", foreground="#e2e8f0", font=("Segoe UI", 11))
    style.configure("TFrame", background="#0f1117")
    style.configure("TButton", background="#6366f1", foreground="white", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("TEntry", fieldbackground="#1e2130", foreground="#e2e8f0")
    style.configure("TCombobox", fieldbackground="#1e2130", foreground="#e2e8f0")

    frame = ttk.Frame(root, padding=30)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="🎯 CV Matcher — Configuration IA", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

    ttk.Label(frame, text="Moteur IA :").pack(anchor="w")
    provider_var = tk.StringVar(value="ollama")
    provider_combo = ttk.Combobox(frame, textvariable=provider_var, state="readonly", width=40,
        values=["ollama — Local 100% (Gratuit, Privé)", "groq — Cloud Groq", "openai — OpenAI"])
    provider_combo.pack(fill="x", pady=(4, 16))

    ttk.Label(frame, text="Modèle Ollama (ex: gemma3:4b, llama3.2, mistral) :").pack(anchor="w")
    models = _ollama_models()
    model_var = tk.StringVar(value=models[0] if models else "gemma3:4b")
    model_entry = ttk.Combobox(frame, textvariable=model_var, width=40, values=models or ["gemma3:4b", "llama3.2", "mistral"])
    model_entry.pack(fill="x", pady=(4, 16))

    ttk.Label(frame, text="Clé API (pour Groq/OpenAI, laisser vide pour Ollama) :").pack(anchor="w")
    key_var = tk.StringVar()
    key_entry = ttk.Entry(frame, textvariable=key_var, show="*", width=40)
    key_entry.pack(fill="x", pady=(4, 24))

    status_var = tk.StringVar(value="")
    status_label = ttk.Label(frame, textvariable=status_var, foreground="#22c55e")
    status_label.pack()

    def test_ollama():
        ms = _ollama_models()
        if ms:
            model_entry["values"] = ms
            status_var.set(f"✓ Ollama OK — {len(ms)} modèle(s) disponible(s)")
        else:
            status_var.set("✗ Ollama non détecté. Installez ollama.com")

    def save_config():
        p = provider_var.get().split(" — ")[0].strip()
        m = model_var.get().strip() or "gemma3:4b"
        k = key_var.get().strip()

        if p == "ollama":
            _write_env(
                f"AI_PROVIDER=ollama\nAPI_KEY=ollama\n"
                f"API_BASE_URL={OLLAMA_URL}/v1\nAI_MODEL={m}\n"
                f"OLLAMA_BASE_URL={OLLAMA_URL}\n"
            )
        elif "groq" in p:
            if not k:
                messagebox.showerror("Erreur", "Clé API Groq requise")
                return
            _write_env(f"AI_PROVIDER=groq\nAPI_KEY={k}\nAPI_BASE_URL=https://api.groq.com/openai/v1\nAI_MODEL=llama-3.3-70b-versatile\n")
        else:
            if not k:
                messagebox.showerror("Erreur", "Clé API OpenAI requise")
                return
            _write_env(f"AI_PROVIDER=openai\nAPI_KEY={k}\nAPI_BASE_URL=https://api.openai.com/v1\nAI_MODEL=gpt-4o\n")

        root.destroy()

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=(8, 0))
    ttk.Button(btn_frame, text="🔗 Tester Ollama", command=test_ollama).pack(side="left", padx=(0, 8))
    ttk.Button(btn_frame, text="✓ Enregistrer & Lancer", command=save_config).pack(side="right")

    root.mainloop()


def main():
    frozen = getattr(sys, "frozen", False)

    print("\n  🎯  CV Matcher — IA Locale\n")

    if not frozen:
        _install_once()
        _configure_cli()
    else:
        _configure_gui()

    if not frozen:
        if BACKEND_DIR not in sys.path:
            sys.path.insert(0, BACKEND_DIR)
        os.chdir(BACKEND_DIR)

    import uvicorn
    from app.main import app  # noqa: E402  (import after path setup)

    print(f"  Serveur démarré → http://localhost:{PORT}")
    print("  Appuyez sur Ctrl+C pour arrêter.\n")

    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open(f"http://localhost:{PORT}")),
        daemon=True,
    ).start()

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
