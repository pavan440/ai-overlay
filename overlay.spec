# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['overlay.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        # scikit-learn internals
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.neighbors._partition_nodes',
        'sklearn.feature_extraction',
        'sklearn.feature_extraction.text',
        'sklearn.metrics.pairwise',
        'sklearn.utils._weight_vector',
        # PIL
        'PIL._tkinter_finder',
        # sounddevice needs PortAudio
        'sounddevice',
        # voice / vision / rag modules
        'voice',
        'voice.recorder',
        'vision',
        'vision.screenshot',
        'rag',
        'rag.extractor',
        'rag.chunker',
        'rag.retriever',
        # ai modules
        'ai',
        'ai.openai_client',
        'ai.anthropic_client',
        # ui modules
        'ui',
        'ui.app',
        'ui.chat_tab',
        'ui.settings_tab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter', 'notebook'],
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
    console=False,       # ← no black console window
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
