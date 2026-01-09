# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PythonApp.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scipy', 'scipy.optimize', 'scipy.interpolate', 'scipy.sparse', 'scipy.spatial', 'scipy.stats', 'openpyxl', 'pandas', 'numpy'],
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
    a.binaries,
    a.datas,
    [],
    name='PythonApp',
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
    icon=['DataProcessing.ico'],
)
