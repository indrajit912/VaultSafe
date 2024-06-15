# This script handles the info command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024

import click
from rich.console import Console
from rich.panel import Panel

from vaultsafe.db.models import session, Vault, Credential, Mnemonic
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
def info():
    """
    Display information about the password vault.

    Example:
        To display information about the password vault:
        \b
        $ vaultsafe info

    """
    print_basic_info()

    # Check db_init
    assert_db_init()
    
    # Get the vault
    vault = session.query(Vault).first()
    vault.print_on_screen()

    # Count total number of Credentials
    total_credentials = session.query(Credential).count()
        
    # Count total number of Mnemonics
    total_mnemonics = session.query(Mnemonic).count()

    # Print total number of credentials
    console.print(Panel(f"Total number of credentials: [bold]{total_credentials}[/bold]", title="Credentials", style="cyan"))

    # Print total number of mnemonics
    console.print(Panel(f"Total number of mnemonics: [bold]{total_mnemonics}[/bold]", title="Mnemonics", style="magenta"))