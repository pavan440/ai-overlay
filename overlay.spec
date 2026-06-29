# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['overlay.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        # scikit-learn
        'sklearn.feature_extraction',
        'sklearn.feature_extraction.text',
        'sklearn.metrics.pairwise',
        # PIL
        'PIL._tkinter_finder',
        # global hotkeys
        'keyboard',
        # sounddevice
        'sounddevice',
        # app modules
        'voice', 'voice.recorder',
        'vision', 'vision.screenshot',
        'rag', 'rag.extractor', 'rag.chunker', 'rag.retriever',
        'ai', 'ai.openai_client', 'ai.anthropic_client',
        'ui', 'ui.app', 'ui.chat_tab', 'ui.settings_tab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter', 'notebook', 'torch', 'torchvision', 'torchaudio', 'tensorflow', 'keras'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIOverlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIOverlay',
)
