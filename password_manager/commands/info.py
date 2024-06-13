# This script handles the info command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024

import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Vault, Credential, Mnemonic
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
def info():
    """
    Display information about the password vault.

    This command retrieves and displays the following information:
    - Details about the currently initialized vault, including its name, owner, and creation timestamp.
    - Total number of credentials stored in the vault.
    - Total number of mnemonics associated with credentials in the vault.

    Notes:
        - The command requires the password vault to be initialized (`init` command) before use.
        - It prints the vault information, total number of credentials, and total number of mnemonics.
        - If no vault is found, it prompts the user to initialize the app using the `init` command first.

    Examples:
        To display information about the password vault:
        \b
        $ password-manager info

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