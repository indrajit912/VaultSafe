# /utils/cli_utils.py

import os
import sys
import pwinput
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import date

from password_manager.config import APP_NAME, COPYRIGHT_STATEMENT, DATABASE_PATH

console = Console()

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


# Function to print basic information
def print_basic_info():

    clear_terminal_screen()

    # Create title with centered alignment
    title = Panel(f"{APP_NAME}", title="Password Manager", title_align="center", style="bold white on blue", border_style="bright_blue")

    # Create information table with centered alignment
    info_table = Table(show_header=False)
    info_table.add_row("[center]Copyright[/center]", f"[center]{COPYRIGHT_STATEMENT}[/center]")
    info_table.add_row("[center]Today's Date[/center]", f"[center]{date.today().strftime('%B %d, %Y')}[/center]")

    # Print title and information table
    console.print(title)
    console.print(info_table)
    console.print("\n")