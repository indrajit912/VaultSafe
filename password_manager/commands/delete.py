# This script handles the del command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console
from rich.prompt import Confirm

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
def delete(mnemonic):
    """
    Delete a credential from the database.

    Args:
        mnemonic (str, optional): The mnemonic associated with the credential to delete.

    If 'mnemonic' is not provided as an argument, the user will be prompted to enter it interactively.

    This command requires the database to be initialized. It will:
    - Prompt for the master password to derive the vault key.
    - Query the database for the credential associated with the provided mnemonic.
    - Display the details of the credential before deletion.
    - Ask for confirmation before proceeding with deletion.
    """
    print_basic_info()
    assert_db_init()

    console.rule("Delete Credential")
    
    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    if not mnemonic:
        mnemonic = click.prompt("No matching mnemonic found. Please provide the mnemonic associated with the credential to be deleted")

    mnemonic_entry = session.query(Mnemonic).filter_by(name=mnemonic).first()
    if not mnemonic_entry:
        console.print(f"[bold red]Mnemonic not found with the name '{mnemonic}'[/bold red].")
        return
    
    # Get the credential associated with the mnemonic
    credential = mnemonic_entry.credential
    console.print("\n")
    Credential._print_on_screen(credential.json(vault_key))
    console.print("\n")

    confirmation = Confirm.ask("Do you want to delete this credential?", default=False)
    if confirmation:
        session.delete(credential)
        session.commit()
        console.print("[bold green]Credential deleted successfully.[/bold green]")
    else:
        console.print("[bold yellow]Deletion cancelled.[/bold yellow]")
    