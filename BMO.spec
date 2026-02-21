# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get customtkinter path
ctk_path = os.path.dirname(customtkinter.__file__)

# Collect all data files for dependencies if needed (though CTK is the main one)
datas = [
    ('assets/faces/*.png', 'assets/faces'),
    (os.path.join(ctk_path, 'theme'), 'customtkinter/theme'),
    (os.path.join(ctk_path, 'gui'), 'customtkinter/gui'),
]

# Note: config.json and .env are EXCLUDED from the bundle so they are editable
# next to the .exe. The code in src/utils/paths.py handles this correctly.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pkg_resources.py2_warn'], # Optimisation
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    (a.binaries + [('config.json', 'config.json', 'DATA')] if False else a.binaries), # Placeholder for logic
    a.zipfiles,
    a.datas,
    [],
    name='BMO_v4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
