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
@click.option('-sc', '--session-check', type=click.Choice(['y', 'n'], case_sensitive=False), help='Enable or disable session check (y/n)')
@click.option('-se', '--session-expiration', type=int, help='Update the session expiration time (in sec) for the Vault')
def update_vault(name, owner, email, session_check, session_expiration):
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
      -sc, --session-check TEXT (y or n)    Enable or disable session check (y or n). If enabled, the 
                                            app will check for a saved master password from the session. 
                                            Consequently, as long as the master password is in session, the 
                                            app will not prompt you for it.
      -se, '--session-expiration' INTEGER    Update the session expiration time (in sec) for the Vault.

    Examples:
      Update the name and owner of the vault:
      $ vaultsafe update-vault -n "New Vault Name" -o "New Owner Name"

      Update only the owner email:
      $ vaultsafe update-vault -e "newemail@example.com"

      Update only the session expiration time to 5 hrs (i.e. 18000 secs):
      $ vaultsafe update-vault -s 18000
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("[bold cyan]Update Vault Information[/bold cyan]")

    # Retrieve the vault from the database
    vault = session.query(Vault).first()

    session_check_bool = True if session_check and session_check.lower() == 'y' else False

    # Update vault attributes
    if name:
        vault.name = name
    if owner:
        vault.owner_name = owner
    if email:
        vault.owner_email = email
    if session_expiration:
        vault.session_expiration = int(session_expiration)
    if session_check is not None:
        vault.session_check = session_check_bool

    # Commit changes to the database
    session.commit()

    console.print(Panel("[bold green]Vault information updated successfully![/bold green]", style="bold green"))

    # Display the Vault
    vault.print_on_screen()


    