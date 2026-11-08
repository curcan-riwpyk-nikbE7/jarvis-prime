# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['jarvis\\app_hud.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('jarvis\\ui\\index.html', 'jarvis\\ui')
    ],
    hiddenimports=[
        'pyautogui',
        'pygetwindow',
        'pystray',
        'keyboard',
        'edge_tts',
        'pyttsx3',
        'pygame',
        'google.genai',
        'clr_loader',
        'pythonnet',
        'webview'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='JarvisPrime',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JarvisPrime',
)
