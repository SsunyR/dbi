from PyInstaller.utils.hooks import collect_data_files

# Required hiddenimports for forbidden.py
hiddenimports = [
    'discord',
    'discord.ext.commands',
    'pathlib',
    'aiofiles',
    'aiofiles.os',
    'os',
    'sys'
]

# Data files
datas = [
    ('docs/금지어.txt', 'docs'),  # Include forbidden words file
]
