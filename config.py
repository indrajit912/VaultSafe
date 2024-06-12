# config.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
from pathlib import Path

DOT_PASSWD_MANGR_DIR = Path.home() / '.password_manager' 

DATABASE_PATH = DOT_PASSWD_MANGR_DIR / 'password_manager.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'