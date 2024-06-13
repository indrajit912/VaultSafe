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

from password_manager.commands import init, add, get, update, delete, info
from password_manager.utils.cli_utils import clear_terminal_screen, check_db_init

console = Console()

# Basic information
app_name = "Indrajit's Password Manager"
current_year = date.today().year
copyright_statement = f"© {current_year} Indrajit Ghosh. All rights reserved."

# Function to print basic information
def print_basic_info():

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

@click.command()
def help():
    """Displays help about the available commands."""
    console.print(Panel("Help - Password Manager CLI", style="green", title="Command List"))

    for command in cli.commands.values():
        if command is not help:  # Skip displaying help for the help command itself
            console.print(f"\n[bold yellow]{command.name}[/bold yellow]: {command.help}")

@click.group()
def cli():
    pass

cli.add_command(init.init)
cli.add_command(help, name='help')
cli.add_command(info.info)
cli.add_command(add.add)
cli.add_command(get.get)
cli.add_command(update.update)
cli.add_command(delete.delete, name='del')


if __name__ == '__main__':
    print_basic_info()
    cli()