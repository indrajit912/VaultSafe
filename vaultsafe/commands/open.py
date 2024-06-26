# This script handles the open command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import webbrowser

import click
from rich.console import Console
from rich.prompt import Prompt

from vaultsafe.db.models import session, Mnemonic
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify
from vaultsafe.utils.crypto_utils import derive_vault_key, decrypt
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
def open(mnemonic):
    """
    Retrieve and display a credential from the database. If the credential's URL entry 
    is not None, open the URL in a web browser.

    Arg:
        -mnemonic TEXT : mnemonic of the credential to be opened.

    Examples:
        To retrieve a credential by mnemonic:
        \b
        $ vaultsafe open my_mnemonic
    """

    print_basic_info()
    assert_db_init()
    
    console.rule("Open Credential in Browser")
    
    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Take the mnemonic if not given
    mnemonic = Prompt.ask("Enter the mnemonic of the credential: ") if mnemonic is None else mnemonic

    mnemonic_entry = session.query(Mnemonic).filter_by(name=mnemonic).first()
    if not mnemonic_entry:
        console.print(f"[bold red]Mnemonic not found with the name '{mnemonic}'[/bold red].")
        return
        
    # Get the credential associated with the mnemonic
    credential = mnemonic_entry.credential
    console.print("\n")
    credential.print_on_screen(vault_key)

    
    if credential.url:
        cred_key = credential.get_decrypted_key(vault_key)
        url_decrypted = decrypt(credential.url, cred_key)

        webbrowser.open(url_decrypted)
        

