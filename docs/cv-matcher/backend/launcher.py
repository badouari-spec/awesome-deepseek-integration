"""
DeepSeek CV Matcher — Windows launcher
Double-click CVMatcher.exe to start the server and open the browser.
"""
import sys
import os
import threading
import webbrowser
import time
import socket

# ── Path resolution (must happen before any app import) ──────────────────────
FROZEN   = getattr(sys, "frozen", False)
EXE_DIR  = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(EXE_DIR, "uploads"), exist_ok=True)
os.environ.setdefault("UPLOAD_DIR",   os.path.join(EXE_DIR, "uploads"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(EXE_DIR, 'cv_matcher.db')}")

_env = os.path.join(EXE_DIR, ".env")
if os.path.exists(_env):
    try:
        from dotenv import load_dotenv
        load_dotenv(_env, override=True)
    except ImportError:
        pass

# ── GUI + server ──────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox

PORT = 8000
URL  = f"http://localhost:{PORT}"


def _wait_for_port(timeout: int = 30) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _run_uvicorn():
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


class CVMatcherApp(tk.Tk):
    BG        = "#0f172a"
    SURFACE   = "#1e293b"
    BORDER    = "#334155"
    TEXT      = "#f1f5f9"
    MUTED     = "#64748b"
    PRIMARY   = "#6366f1"
    SUCCESS   = "#22c55e"
    WARNING   = "#f59e0b"
    DANGER    = "#ef4444"

    def __init__(self):
        super().__init__()
        self.title("DeepSeek CV Matcher")
        self.geometry("420x310")
        self.resizable(False, False)
        self.configure(bg=self.BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._start_server()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=self.BG)
        hdr.pack(fill="x", padx=24, pady=(22, 0))
        tk.Label(hdr, text="🎯  DeepSeek CV Matcher",
                 bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(hdr, text="AI-powered resume matching engine",
                 bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        self._sep()

        # Status row
        sf = tk.Frame(self, bg=self.BG)
        sf.pack(fill="x", padx=24, pady=(0, 4))
        tk.Label(sf, text="Status:", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=7, anchor="w").pack(side="left")
        self._status_var = tk.StringVar(value="Starting server…")
        self._status_lbl = tk.Label(sf, textvariable=self._status_var,
                                     bg=self.BG, fg=self.WARNING,
                                     font=("Segoe UI", 9, "bold"))
        self._status_lbl.pack(side="left")

        # URL row
        uf = tk.Frame(self, bg=self.BG)
        uf.pack(fill="x", padx=24, pady=(0, 2))
        tk.Label(uf, text="URL:", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9), width=7, anchor="w").pack(side="left")
        tk.Label(uf, text=URL, bg=self.BG, fg="#38bdf8",
                 font=("Segoe UI", 9)).pack(side="left")

        self._sep()

        # API key
        kf = tk.Frame(self, bg=self.BG)
        kf.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(kf, text="DeepSeek API Key:", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(kf, bg=self.BG)
        row.pack(fill="x")
        self._key_var = tk.StringVar(value=os.getenv("DEEPSEEK_API_KEY", ""))
        self._key_entry = tk.Entry(row, textvariable=self._key_var,
                                    show="*",
                                    bg=self.SURFACE, fg=self.TEXT,
                                    insertbackground=self.TEXT,
                                    relief="flat", font=("Segoe UI", 9),
                                    highlightthickness=1,
                                    highlightcolor=self.PRIMARY,
                                    highlightbackground=self.BORDER)
        self._key_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self._save_btn = tk.Button(row, text="Save",
                                    bg=self.PRIMARY, fg="white",
                                    relief="flat", padx=12, pady=4,
                                    font=("Segoe UI", 9),
                                    cursor="hand2",
                                    command=self._save_key)
        self._save_btn.pack(side="left", padx=(6, 0))

        # Action buttons
        bf = tk.Frame(self, bg=self.BG)
        bf.pack(pady=4)
        self._open_btn = tk.Button(bf, text="🌐  Open in Browser",
                                    bg=self.PRIMARY, fg="white",
                                    relief="flat", padx=18, pady=7,
                                    font=("Segoe UI", 10, "bold"),
                                    state="disabled", cursor="hand2",
                                    command=lambda: webbrowser.open(URL))
        self._open_btn.pack(side="left", padx=5)
        tk.Button(bf, text="Stop",
                  bg=self.SURFACE, fg=self.MUTED,
                  relief="flat", padx=18, pady=7,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=self._on_close).pack(side="left", padx=5)

    def _sep(self):
        tk.Frame(self, height=1, bg=self.SURFACE).pack(fill="x", padx=20, pady=10)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _save_key(self):
        key = self._key_var.get().strip()
        if not key:
            messagebox.showwarning("Empty key", "Please enter your DeepSeek API key.")
            return
        env_path = os.path.join(EXE_DIR, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"DEEPSEEK_API_KEY={key}\n")
            f.write("DEEPSEEK_MODEL=deepseek-chat\n")
        os.environ["DEEPSEEK_API_KEY"] = key
        messagebox.showinfo("Saved ✓",
                            "API key saved to .env\nRestart the app to apply.")

    def _start_server(self):
        threading.Thread(target=_run_uvicorn, daemon=True).start()

        def _wait():
            ok = _wait_for_port()
            self.after(0, self._on_ready if ok else self._on_error)

        threading.Thread(target=_wait, daemon=True).start()

    def _on_ready(self):
        self._status_var.set("Running  ✓")
        self._status_lbl.configure(fg=self.SUCCESS)
        self._open_btn.configure(state="normal")
        webbrowser.open(URL)

    def _on_error(self):
        self._status_var.set("Failed to start ✕")
        self._status_lbl.configure(fg=self.DANGER)
        messagebox.showerror("Error",
                             f"Could not start server on port {PORT}.\n"
                             "Check that port 8000 is not already in use.")

    def _on_close(self):
        if messagebox.askyesno("Quit", "Stop the server and quit?"):
            self.destroy()
            os._exit(0)


if __name__ == "__main__":
    CVMatcherApp().mainloop()
