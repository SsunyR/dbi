from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 필요한 hiddenimports
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'threading',
    'datetime',
    'platform',
    'importlib.util',
    'subprocess',
]

# 데이터 파일 수집
datas = [
    ('docs/token.txt', 'docs'),  # token.txt 파일 포함
]