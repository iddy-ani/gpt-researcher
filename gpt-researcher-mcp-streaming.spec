# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gpt_researcher_mcp_streaming.py'],
    pathex=[],
    binaries=[],
    datas=[('gpt_researcher', 'gpt_researcher')],
    hiddenimports=['gpt_researcher', 'mcp', 'aiohttp'],
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
    name='gpt-researcher-mcp-streaming',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
