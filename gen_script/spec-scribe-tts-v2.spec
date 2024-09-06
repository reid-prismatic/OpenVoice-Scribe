# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['scribe-tts-v2.py'],
    pathex=['.'],
    binaries=[
        ('binaries/ffmpeg', '.'),
        ('binaries/ffprobe', '.')
    ],
    # binaries=[],
    datas=[
        ('checkpoints_v2/base_speakers/ses/*', 'checkpoints_v2/base_speakers/ses'),
        ('checkpoints_v2/converter/*', 'checkpoints_v2/converter'),
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
a.datas += Tree('./module_v2_necessary/g2p_en', prefix='g2p_en')
a.datas += Tree('./module_v2_necessary/gruut', prefix='gruut')
a.datas += Tree('./module_v2_necessary/jamo', prefix='jamo')
a.datas += Tree('./module_v2_necessary/melo', prefix='melo')
a.datas += Tree('./module_v2_necessary/pykakasi', prefix='pykakasi')
a.datas += Tree('./module_v2_necessary/unidic', prefix='unidic')
a.datas += Tree('./module_v2_necessary/unidic_lite', prefix='unidic_lite')

# a.datas += Tree('resources', prefix='resources')


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='scribe_tts',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,    
    icon='icons/scribetts.ico',
    codesign_identity="9B484EA0B09BA52C286D99CF4134AAD45FE03F81",  # Add your code signing identity here
    entitlements_file="./entitlements.plist"  # Optional, if you need an entitlements file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='scribe_tts_openvoice_v2'
)