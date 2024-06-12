# /utils/cli_utils.py

import os
import pwinput

def clear_terminal_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def input_password(info_msg="Enter your password: "):
    bullet_unicode = '\u2022'
    pw = pwinput.pwinput(info_msg, mask=bullet_unicode)
    return pw