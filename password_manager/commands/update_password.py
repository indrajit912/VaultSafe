# This script is used to update the `password` of an existing credential.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify, get_password
from password_manager.utils.crypto_utils import derive_vault_key, encrypt
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=True)
def update_password(mnemonic):
    """
    Command to update the password of an existing credential.

    This command updates the password of a credential stored in the password vault.
    The credential is identified by a mnemonic provided as an argument. The user is 
    prompted to enter the new password, which is then encrypted and stored in the 
    database.

    Args:
        mnemonic (str): The mnemonic identifier of the credential whose password is to be updated.

    Example:
        To update the password of a credential identified by the mnemonic 'my_mnemonic':
        \b
        $ password-manager update-password my_mnemonic
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("[bold cyan]Update Credential Password[/bold cyan]")

    # Get the credential
    credential = session.query(Credential).join(Mnemonic).filter(Mnemonic.name == mnemonic).first()

    if not credential:
        console.print(f"[yellow]Credential not found with the provided identifier '{mnemonic}'. Update operation aborted.[/yellow]")
        return
    
    # Take old master password
    master_passwd = input_master_passwd_and_verify()

    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Get the cred_key
    cred_key = credential.get_decrypted_key(vault_key=vault_key)

    # Take the new password
    new_password = get_password(
        info_msg="Give the new password for the credential: ",
        success_msg="Passwords matched!"
    )

    # Encrypt the new_password
    new_password_encrypted = encrypt(new_password, cred_key)

    # Set the new passwd
    credential.password = new_password_encrypted

    # Commit
    session.commit()

    console.print(Panel("[bold green]Credential's password changed successfully![/bold green]", style="bold green"))