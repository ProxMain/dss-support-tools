# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['dss_support_tool.service', 'PySide6', 'PySide6.QtWebEngineWidgets']
hiddenimports += collect_submodules('dss_support_tool')


a = Analysis(
    ['src\\dss_support_tool\\desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('src\\dss_support_tool\\static', 'dss_support_tool\\static'), ('src\\dss_support_tool\\data', 'dss_support_tool\\data'), ('img\\space-seals-app-icon.png', 'dss_support_tool\\assets'), ('..\\langpack-browser\\dist', 'dss_support_tool\\langpack_dist'), ('..\\tool-scraper\\data', 'tool-scraper\\data')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DSSSupportDesktop',
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
    icon=['img\\space-seals-app-icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DSSSupportDesktop',
)
