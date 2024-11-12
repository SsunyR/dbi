from PyInstaller.utils.hooks import collect_data_files

# Required hiddenimports for search.py
hiddenimports = [
    'discord',
    'discord.ext.commands',
    'aiohttp',
    'aiohttp.client',
    'aiohttp.client_proto',
    'aiohttp.client_reqrep',
    'bs4',
    'bs4.builder',
    'bs4.element',
    'urllib.parse',
    're',
    'typing'
]

# No specific data files needed for search functionality
datas = []