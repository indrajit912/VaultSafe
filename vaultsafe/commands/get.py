# This script handles the get command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from vaultsafe.db.models import session, Credential, Mnemonic
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify
from vaultsafe.utils.crypto_utils import derive_vault_key
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
@click.option('--search', '-s', help="Search keyword for fuzzy matching name, username, or notes.")
def get(mnemonic, search):
    """
    Retrieve and display a credential from the database.

    If 'mnemonic' is provided, display the credential associated with that mnemonic.
    If 'mnemonic' is not provided, display all credentials stored in the vault.

    Args:
        mnemonic (str, optional): The mnemonic associated with the credential to retrieve.

    Examples:
        To retrieve a credential by mnemonic:
        \b
        $ vaultsafe get my_mnemonic

        To retrieve all credentials:
        \b
        $ vaultsafe get

    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Retrieve Credential")
    
    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    if mnemonic and search:
        raise click.UsageError("Cannot provide both 'mnemonic' and '--search' at the same time.")
    
    if mnemonic:
        # Query credential associated with the 'mnemonic'
        mnemonic_entry = session.query(Mnemonic).filter_by(name=mnemonic).first()
        if not mnemonic_entry:
            console.print(f"[bold red]Mnemonic not found with the name '{mnemonic}'[/bold red].")
            return
        
        # Get the credential associated with the mnemonic
        credential = mnemonic_entry.credential
        console.print("\n")
        credential.print_on_screen(vault_key)

    elif search:
        # Fuzzy search logic

        results = (
            session.query(Credential)
            .outerjoin(Credential.mnemonics)
            .options(joinedload(Credential.mnemonics))
            .filter(
                or_(
                    Credential.name.ilike(f"%{search}%"),
                    Credential.username.ilike(f"%{search}%"),
                    Credential.notes.ilike(f"%{search}%"),
                    Mnemonic.name.ilike(f"%{search}%")  # <-- this line enables searching mnemonics
                )
            )
            .distinct()
            .all()
        )


        if not results:
            console.print(f"[bold red]No credentials found matching:[/bold red] '{search}'")
        else:
            for idx, cred in enumerate(results, 1):
                cred.print_on_screen(vault_key, count=idx)


    else:
        # Query all credentials
        credentials = session.query(Credential).all()
        if not credentials:
            console.print("[bold yellow]No credentials found.[/bold yellow]")
            return
        
        for i, credential in enumerate(credentials):
            console.print("\n")
            Credential._print_on_screen(credential.json(vault_key), copy_to_clipboard=False, count=i + 1)
