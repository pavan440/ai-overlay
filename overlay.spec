# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['overlay.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'sklearn.feature_extraction',
        'sklearn.feature_extraction.text',
        'sklearn.metrics.pairwise',
        'PIL._tkinter_finder',
        'keyboard',
        'sounddevice',
        'voice', 'voice.recorder',
        'vision', 'vision.screenshot',
        'rag', 'rag.extractor', 'rag.chunker', 'rag.retriever',
        'ai', 'ai.openai_client', 'ai.anthropic_client',
        'ui', 'ui.app', 'ui.chat_tab', 'ui.settings_tab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter', 'notebook',
              'torch', 'torchvision', 'torchaudio', 'tensorflow', 'keras'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AIOverlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    runtime_tmpdir=None,
)
