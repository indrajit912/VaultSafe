# config.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
from pathlib import Path
from datetime import date

DOT_PASSWD_MANGR_DIR = Path.home() / '.password_manager' 

DATABASE_PATH = DOT_PASSWD_MANGR_DIR / 'password_manager.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Basic information
APP_NAME = "Indrajit's Password Manager"
CURRENT_YEAR = date.today().year
COPYRIGHT_STATEMENT = f"© {CURRENT_YEAR} Indrajit Ghosh. All rights reserved."