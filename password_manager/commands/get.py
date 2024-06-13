# This script handles the get command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
def get(mnemonic):
    """
    Retrieve and display a credential. If no mnemonic is given, display all credentials.
    """
    console.rule("Retrieve Credential")
    
    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)
    
    if mnemonic:
        mnemonic_entry = session.query(Mnemonic).filter_by(name=mnemonic).first()
        if not mnemonic_entry:
            console.print(f"[bold red]Mnemonic not found with the name '{mnemonic}'[/bold red].")
            return
        
        # Get the credential associated with the mnemonic
        credential = mnemonic_entry.credential
        console.print("\n")
        Credential.print_on_screen(credential.json(vault_key))
    else:
        # Query all credentials
        credentials = session.query(Credential).all()
        if not credentials:
            console.print("[bold yellow]No credentials found.[/bold yellow]")
            return
        
        for i, credential in enumerate(credentials):
            console.print("\n")
            Credential.print_on_screen(credential.json(vault_key), copy_to_clipboard=False, count=i + 1)
