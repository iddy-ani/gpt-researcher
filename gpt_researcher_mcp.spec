# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the absolute path to the gpt-researcher directory
# Use SPECPATH which is provided by PyInstaller
gpt_researcher_path = Path(SPECPATH).absolute()
sys.path.insert(0, str(gpt_researcher_path))

block_cipher = None

# Data files to include
datas = [
    # Include the entire gpt_researcher package
    (str(gpt_researcher_path / 'gpt_researcher'), 'gpt_researcher'),
    # Include any configuration files
    (str(gpt_researcher_path / '.env'), '.'),
    (str(gpt_researcher_path / '.env.example'), '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'gpt_researcher',
    'gpt_researcher.agent',
    'gpt_researcher.config',
    'gpt_researcher.config.config',
    'gpt_researcher.config.variables',
    'gpt_researcher.config.variables.default',
    'gpt_researcher.utils',
    'gpt_researcher.utils.llm',
    'gpt_researcher.llm_provider',
    'gpt_researcher.llm_provider.generic',
    'gpt_researcher.llm_provider.generic.base',
    'gpt_researcher.memory',
    'gpt_researcher.memory.embeddings',
    'gpt_researcher.retrievers',
    'gpt_researcher.retrievers.duckduckgo',
    'gpt_researcher.actions',
    'gpt_researcher.actions.query_processing',
    'gpt_researcher.scraper',
    'gpt_researcher.document',
    'gpt_researcher.context',
    'gpt_researcher.skills',
    'gpt_researcher.vector_store',
    'gpt_researcher.prompts',
    'langchain_openai',
    'langchain_openai.chat_models',
    'langchain_openai.embeddings',
    'httpx',
    'ddgs',
    'ddgs.ddgs',
    'mcp',
    'mcp.server',
    'mcp.server.stdio',
    'mcp.types',
    'asyncio',
    'aiohttp',
    'pydantic',
    'beautifulsoup4',
    'requests',
    'python-dotenv'
]

a = Analysis(
    ['gpt_researcher_mcp.py'],
    pathex=[str(gpt_researcher_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'jupyter',
        'notebook',
        'IPython'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gpt-researcher-mcp',
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
    icon=None
)