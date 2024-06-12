# /utils/cli_utils.py

import os

def clear_terminal_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')