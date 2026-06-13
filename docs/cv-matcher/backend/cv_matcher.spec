# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for DeepSeek CV Matcher
# Run:  pyinstaller cv_matcher.spec --clean --noconfirm

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Bundle the frontend alongside Python code
        ('../frontend', 'frontend'),
    ],
    hiddenimports=[
        # ── uvicorn ──
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # ── starlette / fastapi ──
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.staticfiles',
        'starlette.responses',
        'anyio',
        'anyio._backends._asyncio',
        'anyio.from_thread',
        # ── PDF ──
        'pdfplumber',
        'pdfminer',
        'pdfminer.high_level',
        'pdfminer.layout',
        'pdfminer.pdftypes',
        'pdfminer.pdfpage',
        'pdfminer.pdfinterp',
        'pdfminer.converter',
        'pdfminer.pdfparser',
        'pdfminer.pdfdocument',
        'pdfminer.cmapdb',
        'pdfminer.jbig2',
        'pdfminer.image',
        # ── DOCX ──
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.shared',
        # ── SQLAlchemy ──
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.dialects',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlalchemy.sql.sqltypes',
        # ── File upload ──
        'multipart',
        'python_multipart',
        # ── Async file I/O ──
        'aiofiles',
        'aiofiles.os',
        'aiofiles.threadpool',
        # ── HTTP clients ──
        'httpx',
        'httpcore',
        'httpcore._sync',
        'httpcore._async',
        'h11',
        'h2',
        # ── OpenAI SDK ──
        'openai',
        'openai.resources',
        'openai.resources.chat',
        # ── Misc ──
        'certifi',
        'charset_normalizer',
        'chardet',
        'dotenv',
        'python_dotenv',
        'pydantic',
        'pydantic.v1',
        'email_validator',
        'pkg_resources',
        'sniffio',
        'exceptiongroup',
        # ── App modules (dynamic router imports) ──
        'app',
        'app.main',
        'app.config',
        'app.database',
        'app.models',
        'app.models.db_models',
        'app.models.schemas',
        'app.services',
        'app.services.document_parser',
        'app.services.ai_service',
        'app.routers',
        'app.routers.cv_router',
        'app.routers.job_router',
        'app.routers.match_router',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'PIL', 'cv2',
        'torch', 'tensorflow', 'scipy', 'sklearn',
        'IPython', 'notebook', 'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CVMatcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # No black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # Add your .ico path here if you have one
)

# --onedir mode: creates dist/CVMatcher/ folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CVMatcher',
)
