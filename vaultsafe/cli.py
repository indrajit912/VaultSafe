# cli.py - The main entry point for the CLI.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
# Run in dev mode: `python -m vaultsafe.cli [command] [arguments]`
# Installation (locally):
#   `pip install .` 
# 
# Installation via GitHub:
#   `pip install git+https://github.com/indrajit912/PasswordManager.git`
# 
# cli.py - Main entry point for the CLI.
import click
from rich.console import Console
from rich.panel import Panel

from vaultsafe.commands import (
    change_master_passwd, init, add, get, update, delete, info,
    open, update_vault, export, import_credentials, generate_strong_passwd,
    copy_credential, server
)
from vaultsafe.utils.cli_utils import print_basic_info

console = Console()

@click.command()
def help():
    """Displays help about the available commands."""
    print_basic_info()
    console.print(Panel("Help - VaultSafe CLI", style="green", title="Command List"))

    for command_name, command in cli.commands.items():
        if command is not help:  # Skip displaying help for the help command itself
            console.print(f"\n[bold yellow]{command_name}[/bold yellow]: {command.help}")

@click.group()
def cli():
    pass

# Add commands to the group
cli.add_command(init.init)
cli.add_command(help, name='help')
cli.add_command(info.info)
cli.add_command(generate_strong_passwd.generate)
cli.add_command(add.add)
cli.add_command(get.get)
cli.add_command(copy_credential.copy_credential, name='copy')
cli.add_command(update.update)
cli.add_command(delete.delete, name='del')
cli.add_command(open.open)
cli.add_command(change_master_passwd.change_master_password)
cli.add_command(update_vault.update_vault)
cli.add_command(export.export)
cli.add_command(import_credentials.import_credentials, name='import')
cli.add_command(server.server)

if __name__ == '__main__':
    cli()
