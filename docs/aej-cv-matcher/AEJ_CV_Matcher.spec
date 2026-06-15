# -*- mode: python ; coding: utf-8 -*-
# ════════════════════════════════════════════════════════════════
#  AEJ CV MATCHER PRO — Spec PyInstaller  (MODE LOCAL, SANS GOOGLE)
#  Build :  pyinstaller AEJ_CV_Matcher.spec --noconfirm
# ════════════════════════════════════════════════════════════════
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = [], [], []

# Paquets nécessitant data + sous-modules complets
for pkg in ['pdfplumber', 'pdfminer', 'docx', 'pptx', 'matplotlib',
            'sklearn', 'rank_bm25', 'rapidfuzz', 'openpyxl', 'PIL',
            'cv2', 'pdf2image', 'docx2txt', 'striprtf']:
    try:
        d, b, h = collect_all(pkg)
        datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass

hiddenimports += collect_submodules('scipy')
hiddenimports += [
    'pytesseract', 'win10toast', 'requests',
    'sklearn.feature_extraction.text', 'sklearn.metrics.pairwise',
    'matplotlib.backends.backend_tkagg',
]

block_cipher = None

a = Analysis(
    ['AEJ_CV_Matcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # On EXCLUT explicitement Google + PyTorch pour un exe léger,
    # sans aucune validation/OAuth Google.
    excludes=[
        'google', 'google_auth_oauthlib', 'googleapiclient',
        'google.auth', 'google.oauth2', 'google_auth_httplib2',
        'torch', 'tensorflow', 'sentence_transformers',
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
    name='AEJ_CV_Matcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # application fenêtrée (pas de console noire)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='aej_icon.ico' if __import__('os').path.exists('aej_icon.ico') else None,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name='AEJ_CV_Matcher',
)
