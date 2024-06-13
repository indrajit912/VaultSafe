# cli.py - The main entry point for the CLI.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
# Run in dev mode: `python -m password_manager.cli [command] [arguments]`
# Installation: 
#      [1] `git clone https://github.com/indrajit912/PasswordManager.git`
# 
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.commands import change_passwd, init, add, get, update, delete, info
from password_manager.utils.cli_utils import print_basic_info

console = Console()

@click.command()
def help():
    """Displays help about the available commands."""
    print_basic_info()
    console.print(Panel("Help - Password Manager CLI", style="green", title="Command List"))

    for command_name, command in cli.commands.items():
        if command is not help:  # Skip displaying help for the help command itself
            console.print(f"\n[bold yellow]{command_name}[/bold yellow]: {command.help}")

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
cli.add_command(change_passwd.change_password, name='change-password')


if __name__ == '__main__':
    cli()