# This script handles the copy command.
# Author: Indrajit Ghosh
# Created On: Jun 15, 2024
# 
import click
import pyperclip
from rich.console import Console

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key, decrypt
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=True)
@click.option('-u', '--username', is_flag=True, help='Username for the credential')
@click.option('-pw', '--password', is_flag=True, help="Flag to copy the password.")
@click.option('-rk', '--recovery-key', is_flag=True, help='Flag to copy the recovery key.')
@click.option('-tk', '--token', is_flag=True, help="Flag to copy the token.")
@click.option('-pe', '--primary-email', is_flag=True, help='Primary email id associated with the credential')
@click.option('-se', '--secondary-email', is_flag=True, help='Secondary email id associated with the credential')
def copy_credential(mnemonic, username, password, recovery_key, token, primary_email, secondary_email):
    """
    Copy a specific field from a credential associated with the mnemonic to the clipboard.

    Arguments:
        mnemonic (str): The mnemonic identifier of the credential whose field is to be copied.

    Options:
        -u, --username   : Copy the username of the credential.
        -pw, --password  : Copy the password of the credential.
        -rk, --recovery-key : Copy the recovery key of the credential.
        -tk, --token     : Copy the token of the credential.
        -pe, --primary-email : Copy the primary email of the credential.
        -se, --secondary-email : Copy the secondary email of the credential.

    Example:
        To copy the password of a credential identified by the mnemonic 'my_mnemonic':
        \b
        $ password-manager copy my_mnemonic -pw

        To copy the username of a credential identified by the mnemonic 'my_mnemonic':
        \b
        $ password-manager copy my_mnemonic -u

        Only one flag can be specified at a time to indicate which field to copy. If more than one flag is provided, the command will display an error.
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Copy Credential Field")
    
    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Verify the mnemonic
    mnemonic_entry = session.query(Mnemonic).filter_by(name=mnemonic).first()
    if not mnemonic_entry:
        console.print(f"[bold red]Mnemonic not found with the name '{mnemonic}'[/bold red].")
        return
    
    # Get the credential associated with the mnemonic
    credential = mnemonic_entry.credential

    # Ensure that exactly one option flag is given
    flags = [username, password, recovery_key, token, primary_email, secondary_email]
    if sum(flags) != 1:
        console.print("[bold red]Please provide exactly one flag to specify which attribute to copy.[/bold red]")
        return
    
    # Decrypt the necessary attribute based on the given flag
    decrypted_value = None
    credential_key = credential.get_decrypted_key(vault_key=vault_key)

    if username:
        decrypted_value = decrypt(credential.username, credential_key) if credential.username else None
    elif password:
        decrypted_value = decrypt(credential.password, credential_key) if credential.password else None
    elif recovery_key:
        decrypted_value = decrypt(credential.recovery_key, credential_key) if credential.recovery_key else None
    elif token:
        decrypted_value = decrypt(credential.token, credential_key) if credential.token else None
    elif primary_email:
        decrypted_value = decrypt(credential.primary_email, credential_key) if credential.primary_email else None
    elif secondary_email:
        decrypted_value = decrypt(credential.secondary_email, credential_key) if credential.secondary_email else None

    # Copy the decrypted value to the clipboard
    if decrypted_value:
        pyperclip.copy(decrypted_value)
        console.print("[bold green]The specified field has been copied to the clipboard![/bold green]")
    else:
        console.print("[bold red]The specified field is empty or not provided for this credential.[/bold red]")
