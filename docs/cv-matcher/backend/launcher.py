"""
CV Matcher — Lanceur Windows (Mode 100% Local)
Fonctionne avec Ollama : Gemma, LLaMA, Mistral, Phi, Qwen…
Aucune connexion Internet requise — toutes vos données restent sur votre PC.
"""
import sys
import os
import threading
import time
import socket
import webbrowser
import json
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox, ttk

# ── Résolution des chemins ────────────────────────────────────────────────────
FROZEN  = getattr(sys, "frozen", False)
EXE_DIR = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(EXE_DIR, "uploads"), exist_ok=True)
os.environ.setdefault("UPLOAD_DIR",   os.path.join(EXE_DIR, "uploads"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(EXE_DIR, 'cv_matcher.db')}")
os.environ.setdefault("API_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("API_KEY",      "ollama")
os.environ.setdefault("AI_MODEL",     "gemma3:4b")

_env = os.path.join(EXE_DIR, ".env")
if os.path.exists(_env):
    try:
        from dotenv import load_dotenv
        load_dotenv(_env, override=True)
    except ImportError:
        pass

PORT        = 8000
APP_URL     = f"http://localhost:{PORT}"
OLLAMA_URL  = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Helpers Ollama ────────────────────────────────────────────────────────────

def _ollama_models() -> list:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return []

def _ollama_up() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/", timeout=2)
        return True
    except Exception:
        return False

def _wait_app(timeout: int = 45) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                return True
        except OSError:
            time.sleep(0.4)
    return False

def _run_server():
    from app.main import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")

def _save_env(**kwargs):
    """Met à jour les variables dans le fichier .env."""
    path = os.path.join(EXE_DIR, ".env")
    lines = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    lines[k.strip()] = v.strip()
    lines.update(kwargs)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in lines.items():
            f.write(f"{k}={v}\n")


# ── Interface graphique ───────────────────────────────────────────────────────

class CVMatcherApp(tk.Tk):
    BG      = "#0f172a"
    SURFACE = "#1e293b"
    BORDER  = "#334155"
    TEXT    = "#f1f5f9"
    MUTED   = "#64748b"
    PRIMARY = "#6366f1"
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    DANGER  = "#ef4444"
    INFO    = "#38bdf8"

    def __init__(self):
        super().__init__()
        self.title("CV Matcher — IA Locale")
        self.geometry("500x430")
        self.resizable(False, False)
        self.configure(bg=self.BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Style ttk
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=self.SURFACE,
                         background=self.SURFACE,
                         foreground=self.TEXT,
                         selectbackground=self.PRIMARY,
                         arrowcolor=self.MUTED)

        self._build_ui()
        self._start_server()
        self.after(500, self._refresh_ollama)

    # ── Construction UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        # En-tête
        hdr = tk.Frame(self, bg=self.BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🎯  CV Matcher",
                 bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Matching de CV par IA — 100% local, 100% privé",
                 bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        self._sep()

        # ── Section Ollama ────────────────────────────────────────────────────
        tk.Label(self, text="MOTEUR IA LOCAL (OLLAMA)",
                 bg=self.BG, fg="#475569",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 6))

        of = tk.Frame(self, bg=self.BG)
        of.pack(fill="x", padx=24, pady=(0, 6))
        tk.Label(of, text="Ollama :", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
        self._ollama_var = tk.StringVar(value="Vérification…")
        self._ollama_lbl = tk.Label(of, textvariable=self._ollama_var,
                                     bg=self.BG, fg=self.WARNING,
                                     font=("Segoe UI", 9, "bold"))
        self._ollama_lbl.pack(side="left")
        tk.Button(of, text="↻ Actualiser", bg=self.SURFACE, fg=self.MUTED,
                  relief="flat", padx=8, pady=2, font=("Segoe UI", 8),
                  cursor="hand2", command=self._refresh_ollama).pack(side="right")

        # Sélecteur de modèle
        mf = tk.Frame(self, bg=self.BG)
        mf.pack(fill="x", padx=24, pady=(0, 4))
        tk.Label(mf, text="Modèle :", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
        self._model_var = tk.StringVar(value=os.environ.get("AI_MODEL", "gemma3:4b"))
        self._model_cb  = ttk.Combobox(mf, textvariable=self._model_var,
                                        font=("Segoe UI", 9), width=26,
                                        state="readonly")
        self._model_cb["values"] = [os.environ.get("AI_MODEL", "gemma3:4b")]
        self._model_cb.pack(side="left")
        tk.Button(mf, text="Choisir", bg=self.PRIMARY, fg="white",
                  relief="flat", padx=10, pady=2, font=("Segoe UI", 9),
                  cursor="hand2", command=self._apply_model).pack(side="left", padx=(8, 0))

        # Conseil installation modèle
        hint = tk.Frame(self, bg=self.BG)
        hint.pack(fill="x", padx=24, pady=(2, 0))
        tk.Label(hint, text="Installer un modèle (terminal Windows) :",
                 bg=self.BG, fg="#475569", font=("Segoe UI", 8)).pack(anchor="w")
        for cmd in ("ollama pull gemma3:4b", "ollama pull llama3.2", "ollama pull mistral"):
            tk.Label(hint, text=f"  > {cmd}",
                     bg=self.BG, fg="#334155",
                     font=("Courier New", 8)).pack(anchor="w")

        self._sep()

        # ── Section Serveur app ───────────────────────────────────────────────
        tk.Label(self, text="SERVEUR APPLICATION",
                 bg=self.BG, fg="#475569",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 6))

        sf = tk.Frame(self, bg=self.BG)
        sf.pack(fill="x", padx=24, pady=(0, 4))
        tk.Label(sf, text="Statut :", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
        self._server_var = tk.StringVar(value="Démarrage…")
        self._server_lbl = tk.Label(sf, textvariable=self._server_var,
                                     bg=self.BG, fg=self.WARNING,
                                     font=("Segoe UI", 9, "bold"))
        self._server_lbl.pack(side="left")

        uf = tk.Frame(self, bg=self.BG)
        uf.pack(fill="x", padx=24, pady=(0, 4))
        tk.Label(uf, text="Adresse :", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
        tk.Label(uf, text=APP_URL, bg=self.BG, fg=self.INFO,
                 font=("Segoe UI", 9, "bold"),
                 cursor="hand2").pack(side="left")

        self._sep()

        # ── Boutons ───────────────────────────────────────────────────────────
        bf = tk.Frame(self, bg=self.BG)
        bf.pack(pady=6)
        self._open_btn = tk.Button(bf, text="🌐  Ouvrir l'application",
                                    bg=self.PRIMARY, fg="white",
                                    relief="flat", padx=20, pady=8,
                                    font=("Segoe UI", 10, "bold"),
                                    state="disabled", cursor="hand2",
                                    command=lambda: webbrowser.open(APP_URL))
        self._open_btn.pack(side="left", padx=6)
        tk.Button(bf, text="Arrêter",
                  bg=self.SURFACE, fg=self.MUTED,
                  relief="flat", padx=18, pady=8,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=self._on_close).pack(side="left", padx=6)

        # Pied de page
        tk.Label(self,
                 text="🔒  Données 100% locales — aucune connexion Internet requise",
                 bg=self.BG, fg="#1e3a5f",
                 font=("Segoe UI", 8)).pack(pady=(8, 14))

    def _sep(self):
        tk.Frame(self, height=1, bg=self.SURFACE).pack(fill="x", padx=20, pady=10)

    # ── Logique Ollama ────────────────────────────────────────────────────────

    def _refresh_ollama(self):
        def _check():
            models = _ollama_models()
            up = bool(models) or _ollama_up()
            self.after(0, self._update_ollama, up, models)
        threading.Thread(target=_check, daemon=True).start()

    def _update_ollama(self, up: bool, models: list):
        if up and models:
            self._ollama_var.set(f"✓  En ligne  ({len(models)} modèle(s) installé(s))")
            self._ollama_lbl.configure(fg=self.SUCCESS)
            self._model_cb["values"] = models
            cur = self._model_var.get()
            if cur not in models:
                self._model_var.set(models[0])
                os.environ["AI_MODEL"] = models[0]
        elif up:
            self._ollama_var.set("✓  En ligne  — aucun modèle installé")
            self._ollama_lbl.configure(fg=self.WARNING)
            messagebox.showwarning("Aucun modèle",
                "Ollama est en ligne mais aucun modèle n'est installé.\n\n"
                "Ouvrez un terminal Windows et tapez :\n"
                "  ollama pull gemma3:4b\n\n"
                "Puis cliquez ↻ Actualiser.")
        else:
            self._ollama_var.set("✕  Non démarré")
            self._ollama_lbl.configure(fg=self.DANGER)
            messagebox.showerror("Ollama introuvable",
                "Ollama n'est pas démarré.\n\n"
                "Étape 1 — Installez Ollama :\n"
                "  https://ollama.com\n\n"
                "Étape 2 — Ouvrez un terminal et tapez :\n"
                "  ollama pull gemma3:4b\n\n"
                "Étape 3 — Cliquez ↻ Actualiser ci-dessus.")

    def _apply_model(self):
        model = self._model_var.get()
        os.environ["AI_MODEL"] = model
        _save_env(AI_MODEL=model)
        self._ollama_var.set(f"✓  Modèle « {model} » sélectionné")
        self._ollama_lbl.configure(fg=self.SUCCESS)

    # ── Serveur FastAPI ───────────────────────────────────────────────────────

    def _start_server(self):
        threading.Thread(target=_run_server, daemon=True).start()
        threading.Thread(target=self._wait_and_open, daemon=True).start()

    def _wait_and_open(self):
        ok = _wait_app()
        self.after(0, self._on_ready if ok else self._on_error)

    def _on_ready(self):
        self._server_var.set("✓  En ligne")
        self._server_lbl.configure(fg=self.SUCCESS)
        self._open_btn.configure(state="normal")
        webbrowser.open(APP_URL)

    def _on_error(self):
        self._server_var.set("✕  Échec du démarrage")
        self._server_lbl.configure(fg=self.DANGER)
        messagebox.showerror("Erreur", f"Impossible de démarrer le serveur sur le port {PORT}.\nVérifiez qu'il n'est pas déjà utilisé.")

    def _on_close(self):
        if messagebox.askyesno("Quitter", "Arrêter le serveur et quitter l'application ?"):
            self.destroy()
            os._exit(0)


if __name__ == "__main__":
    CVMatcherApp().mainloop()
