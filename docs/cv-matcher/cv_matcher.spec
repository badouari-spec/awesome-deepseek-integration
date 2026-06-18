# -*- mode: python ; coding: utf-8 -*-
# ════════════════════════════════════════════════════════════════
#  CV MATCHER WEB — Spec PyInstaller
#  Build :  pyinstaller cv_matcher.spec --noconfirm
#  Génère :  dist\CV_Matcher\CV_Matcher.exe  (Windows)
# ════════════════════════════════════════════════════════════════
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

datas, binaries, hiddenimports = [], [], []

# ── Frontend (HTML/CSS/JS statiques) ─────────────────────────────
datas += [("frontend", "frontend")]

# ── Paquets avec données internes ────────────────────────────────
for pkg in [
    "pdfplumber", "pdfminer", "docx", "pptx",
    "openpyxl", "PIL", "striprtf", "odfpy",
    "uvicorn", "fastapi", "starlette", "anyio",
    "aiofiles", "multipart",
]:
    try:
        d, b, h = collect_all(pkg)
        datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass

# ── Sous-modules critiques ────────────────────────────────────────
hiddenimports += collect_submodules("sqlalchemy")
hiddenimports += collect_submodules("sqlalchemy.dialects.sqlite")
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("fastapi")
hiddenimports += collect_submodules("starlette")
hiddenimports += collect_submodules("email")
hiddenimports += [
    "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
    "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl", "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan", "uvicorn.lifespan.on",
    "sqlalchemy.dialects.sqlite.pysqlite",
    "app.main", "app.database", "app.config",
    "app.models.db_models", "app.models.schemas",
    "app.routers.cv_router", "app.routers.job_router", "app.routers.match_router",
    "app.services.ai_service", "app.services.document_parser",
    "python_multipart", "python_dotenv", "dotenv",
    "openai", "requests", "httpx",
    "pdfplumber", "pdfminer", "docx", "pptx", "openpyxl",
    "striprtf.striprtf", "odf", "bs4",
    "pytesseract", "PIL._tkinter_finder",
    "tkinter", "tkinter.ttk",
    "aiofiles", "aiofiles.os", "aiofiles.threadpool",
    "h11", "httptools", "websockets",
]

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["backend"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch", "tensorflow", "sklearn", "scipy", "numpy",
        "matplotlib", "pandas", "cv2",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="CV_Matcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="cv_matcher_icon.ico" if os.path.exists("cv_matcher_icon.ico") else None,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name="CV_Matcher",
)
