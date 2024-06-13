# cli.py - The main entry point for the CLI.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
# Run in dev mode: `python -m password_manager.cli [command] [arguments]`
# Installation: 
#      [1] ` pip install git+https://github.com/indrajit912/PasswordManager.git`
#      [2] `password-manager --help`
# 
import click
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from password_manager.commands import init, add, get, delete
from password_manager.utils.cli_utils import clear_terminal_screen
from password_manager.db.models import session, Vault

# Basic information
app_name = "Indrajit's Password Manager"
current_year = date.today().year
copyright_statement = f"© {current_year} Indrajit Ghosh. All rights reserved."

# TODO: create an info commnad: Getting vault
# vault = session.query(Vault).first()

# Function to print basic information
def print_basic_info():
    console = Console()

    clear_terminal_screen()

    # Create title with centered alignment
    title = Panel(f"{app_name}", title="Password Manager", title_align="center", style="bold white on blue", border_style="bright_blue")

    # Create information table with centered alignment
    info_table = Table(show_header=False)
    info_table.add_row("[center]Copyright[/center]", f"[center]{copyright_statement}[/center]")
    info_table.add_row("[center]Today's Date[/center]", f"[center]{date.today().strftime('%B %d, %Y')}[/center]")

    # Print title and information table
    console.print(title)
    console.print(info_table)
    console.print("\n")


@click.group()
def cli():
    pass

cli.add_command(init.init)
cli.add_command(add.add)
cli.add_command(get.get)
cli.add_command(delete.delete, name='del')

if __name__ == '__main__':
    print_basic_info()
    cli()