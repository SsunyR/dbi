from PyInstaller.utils.hooks import collect_data_files

# Required hiddenimports for voice.py
hiddenimports = [
    'discord',
    'discord.ext.commands',
    'discord.voice_client',
    'discord.gateway',
    'asyncio'
]

# No specific data files needed for voice functionality
datas = []