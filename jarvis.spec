# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

jarvis_dir = os.path.abspath('jarvis')

# Collect all UI assets, skills, sounds
added_files = [
    (os.path.join(jarvis_dir, 'ui'), 'jarvis/ui'),
    (os.path.join(jarvis_dir, 'agents'), 'jarvis/agents'),
    (os.path.join(jarvis_dir, 'icon.ico'), 'jarvis'),
]

# Collect hidden imports for edge-tts, faster-whisper, pyaudio, webview, ctranslate2
hidden_imports = [
    'jarvis',
    'jarvis.core',
    'jarvis.sound_fx',
    'jarvis.settings_manager',
    'jarvis.tools.system_control',
    'jarvis.tools.app_launcher',
    'jarvis.tools.updater',
    'jarvis.voice.engine',
    'jarvis.voice.vad_listener',
    'pyaudio',
    'edge_tts',
    'gtts',
    'pygame',
    'webview',
    'clr',
    'comtypes',
    'pycparser',
    'faster_whisper',
    'ctranslate2',
    'av',
    'scipy',
    'numpy',
    'requests',
    'dotenv',
    'PIL',
]

a = Analysis(
    ['jarvis/app_ultimate.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'pandas'],
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
    name='JARVIS',
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
    icon=os.path.join(jarvis_dir, 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JARVIS',
)
