# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['scribe-tts-v1.py'],
    pathex=['.'],
    binaries=[
        ('binaries/ffmpeg', '.'),
        ('binaries/ffprobe', '.')
    ],
    # binaries=[],
    datas=[
        ('checkpoints/base_speakers/EN/*', 'checkpoints/base_speakers/EN'),
        ('checkpoints/converter/*', 'checkpoints/converter'),
        ('resources/example_reference.mp3', 'resources'),
        ('resources/demo_speaker0.mp3', 'resources'),        
        ('resources/demo_speaker1.mp3', 'resources'),
        ('resources/demo_speaker2.mp3', 'resources'),
        ('resources/dv.mp3', 'resources'),
        ('silero-vad/snakers4_silero-vad_master.zip', 'silero-vad')
    ],
    hiddenimports=[
        'torch',
        'openvoice'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# a.datas += Tree('checkpoints', prefix='checkpoints')
a.datas += Tree('../openvoice', prefix='openvoice')
# a.datas += Tree('resources', prefix='resources')


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='scribe_tts_v1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,    
    icon='icons/scribetts.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='scribe_tts_v1_collection'
)