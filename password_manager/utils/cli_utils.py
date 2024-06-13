# /utils/cli_utils.py

import os
import sys
import pwinput
from rich.console import Console
from rich.panel import Panel

console = Console()

from config import DATABASE_PATH

def clear_terminal_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def input_password(info_msg="Enter your password: "):
    bullet_unicode = '\u2022'
    pw = pwinput.pwinput(info_msg, mask=bullet_unicode)
    return pw

def check_db_init():
    """Checks whether db is initialized or not."""
    if not DATABASE_PATH.exists():
        return False
    else:
        return True

def assert_db_init():
    # Check db_init
    if not check_db_init():
        console.print(Panel("[red]No vault found![/red] The app is probably not initialized yet.", title="Error", style="bold red"))
        console.print("Please use the [bold]`init`[/bold] command to initialize the app.", style="yellow")
        sys.exit(1)