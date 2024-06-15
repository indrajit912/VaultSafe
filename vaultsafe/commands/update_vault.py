# This script handles the update-vault command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console
from rich.panel import Panel

from vaultsafe.db.models import session, Vault
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.option('-n', '--name', type=str, help='Update the name of the Vault')
@click.option('-o', '--owner', type=str, help='Update the owner name for the Vault')
@click.option('-e', '--email', type=str, help='Update the owner email for the Vault')
def update_vault(name, owner, email):
    """
    Update the vault information in the database.

    This command allows updating various attributes of the vault such as name, owner name,
    and owner email. If any of the options (-n, -o, -e) are provided, the corresponding
    attribute of the vault will be updated. If an option is not provided, the command will
    prompt for the updated value.

    Options:
      -n, --name TEXT     Update the name of the Vault.
      -o, --owner TEXT    Update the owner name for the Vault.
      -e, --email TEXT    Update the owner email for the Vault.

    Examples:
      Update the name and owner of the vault:
      $ vaultsafe update-vault -n "New Vault Name" -o "New Owner Name"

      Update only the owner email:
      $ vaultsafe update-vault -e "newemail@example.com"
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("[bold cyan]Update Vault Information[/bold cyan]")

    # Retrieve the vault from the database
    vault = session.query(Vault).first()

    # Update vault attributes
    if name:
        vault.name = name
    if owner:
        vault.owner_name = owner
    if email:
        vault.owner_email = email


    # Commit changes to the database
    session.commit()


    console.print(Panel("[bold green]Vault information updated successfully![/bold green]", style="bold green"))

    # Display the Vault
    vault.print_on_screen()


    