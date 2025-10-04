# -*- mode: python ; coding: utf-8 -*-

# This file is a PyInstaller specification file.
# It tells PyInstaller how to package the PyVault application.

# Analysis: This section finds all the Python modules and libraries your application needs.
a = Analysis(
    ['main.py'],
    pathex=['/home/kiet/projects/pyvault'],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# PYC: This creates the .pyc files (compiled Python)
pyz = PYZ(a.pure)

# EXE: This section creates the executable file itself.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pyvault',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Set to False for GUI applications on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT: This gathers all the dependent files into one folder.
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyvault'
)

# For macOS, create a bundle
app = BUNDLE(
    coll,
    name='PyVault.app',
    icon=None, # Specify icon for macOS
    bundle_identifier='com.yourcompany.pyvault'
)
