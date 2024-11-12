from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Discord.py 관련 hiddenimports
hiddenimports = [
    'discord',
    'discord.ext.commands',
    'pathlib',
    'logging',
    'importlib.util',
    'PyNaCl',
] + collect_submodules('discord') + collect_submodules('pathlib') + collect_submodules('logging') + collect_submodules('PyNaCl')

# cogs 디렉토리의 모든 파일 포함
datas = [
    ('cogs/*.py', 'cogs'),  # cogs 디렉토리의 모든 Python 파일
]