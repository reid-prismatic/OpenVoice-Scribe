# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['scribe-tts-v1.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('checkpoints/base_speakers/EN/*', 'checkpoints/base_speakers/EN'),
        ('checkpoints/converter/*', 'checkpoints/converter'),
        ('resources/example_reference.mp3', 'resources'),
        ('resources/demo_speaker0.mp3', 'resources'),        
        ('resources/demo_speaker1.mp3', 'resources'),
        ('resources/demo_speaker2.mp3', 'resources'),
    ],
    hiddenimports=[
        'torch',
        'openvoice'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

a.datas += Tree('../openvoice', prefix='openvoice')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='scribe_tts_v1_onefile',
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
    icon='icons/scribetts.ico'
)
