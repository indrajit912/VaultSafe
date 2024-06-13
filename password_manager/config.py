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
app_name = "Indrajit's Password Manager"
current_year = date.today().year
copyright_statement = f"© {current_year} Indrajit Ghosh. All rights reserved."