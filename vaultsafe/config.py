# config.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import os
from pathlib import Path
from datetime import date

from dotenv import load_dotenv

# Define the path to the .env file
DOT_ENVPATH = Path(__file__).parent.parent.resolve() / '.env'

# Load the environment variables from the .env file
load_dotenv(DOT_ENVPATH)

# Example environment variable
DEV_MODE = os.getenv('DEV_MODE', 'off')

DOT_VAULTSAFE_DIR = Path.home() / '.vaultsafe' if DEV_MODE != 'on' else Path.cwd() / '.vaultsafe'

DATABASE_PATH = DOT_VAULTSAFE_DIR / 'vaultsafe.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
DOT_SESSION_FILE = DOT_VAULTSAFE_DIR / '.session'

# Basic information
APP_NAME = "VaultSafe"
GITHUB_REPO = "https://github.com/indrajit912/VaultSafe.git"
CURRENT_YEAR = date.today().year
COPYRIGHT_STATEMENT = f"© {CURRENT_YEAR} Indrajit Ghosh. All rights reserved."

# Server info
DEFAULT_SERVER_PORT = 8000

class Config:
    SECRET_KEY = 'a_hard_to_guess_string'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
