# config.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
from pathlib import Path
from datetime import date

DOT_VAULTSAFE_DIR = Path.home() / '.vaultsafe' 

DATABASE_PATH = DOT_VAULTSAFE_DIR / 'vaultsafe.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
DOT_SESSION_FILE = DOT_VAULTSAFE_DIR / '.session'
VENV_DIR = DOT_VAULTSAFE_DIR / 'pwenv'
VENV_PYTHON = VENV_DIR / 'bin' / 'python'
VENV_PYTHON = 'python' if not VENV_PYTHON.exists() else VENV_PYTHON

# Basic information
APP_NAME = "VaultSafe"
GITHUB_REPO = "https://github.com/indrajit912/VaultSafe.git"
CURRENT_YEAR = date.today().year
COPYRIGHT_STATEMENT = f"© {CURRENT_YEAR} Indrajit Ghosh. All rights reserved."

# Server info
RUN_FLASK_PY = Path(__file__).parent.parent.resolve() / 'run_flask.py'
DEFAULT_SERVER_PORT = 8000

class Config:
    SECRET_KEY = 'a_hard_to_guess_string'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
