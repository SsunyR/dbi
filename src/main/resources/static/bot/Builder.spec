# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import platform
import sys

# Get the requirements from requirements.txt
def get_requirements():
    reqs_path = Path('docs/requirements.txt')
    if reqs_path.exists():
        with open(reqs_path) as f:
            context = f.read()
            reqs = context.splitlines()
        return [req for req in reqs]
    return []

block_cipher = None

# make hiddenimports list from hooks folder
def get_imports():
    hooks_path = Path('hooks')
    hiddenimports = []
    if hooks_path.exists():
        for file in hooks_path.iterdir():
            if file.is_file() and file.suffix == '.py' and file.name != '__init__.py':
                # 파일 속 hiddenimports 리스트를 가져와서 추가
                local_vars = {}
                with open(file, 'r') as f:
                    exec(f.read(), {}, local_vars)
                    if 'hiddenimports' in local_vars:
                        hiddenimports.extend(local_vars['hiddenimports'])
    return hiddenimports


# Project structure
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('./cogs', './cogs'),
        ('./logs', './logs'),
        ('./docs', './docs'),
        ('main.py', '.'),
    ],
    hiddenimports=get_imports(),
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create the PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BotLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 모드로 실행
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='discord_icon.ico',  # 아이콘 파일 경로
)